import os, hashlib, time
import fitz
import streamlit as st
import google.generativeai as genai
import PIL.Image, io
from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.gemini import GeminiEmbedding
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
GITHUB_MODEL   = "gpt-4o"
INDEX_DIR      = "./index_store"

genai.configure(api_key=GEMINI_API_KEY)
VISION_MODEL = genai.GenerativeModel("gemini-2.5-flash-lite")

Settings.embed_model = GeminiEmbedding(
    model_name="models/gemini-embedding-001",
    api_key=GEMINI_API_KEY
)
Settings.chunk_size = 1024
Settings.chunk_overlap = 50
Settings.llm = OpenAILike(
    model=GITHUB_MODEL,
    api_base="https://models.inference.ai.azure.com",
    api_key=GITHUB_TOKEN,
    is_chat_model=True,
    request_timeout=60.0,
    max_tokens=2048,
)

def pdf_to_images(pdf_bytes):
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    total = len(pdf)
    for i in range(total):
        pix = pdf.load_page(i).get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
        yield i, pix.tobytes("png"), total
    pdf.close()

def ocr_page(args):
    i, img_bytes = args
    img = PIL.Image.open(io.BytesIO(img_bytes))
    for attempt in range(5):
        try:
            response = VISION_MODEL.generate_content([
                "Extract all text and tables from this page as clean Markdown. Nothing else.",
                img
            ])
            return i, response.text
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                wait = 30 * (attempt + 1)
                st.toast(f"Rate limit — waiting {wait}s before retrying page {i+1}...")
                time.sleep(wait)
            else:
                raise e
    raise RuntimeError(f"Page {i+1} failed after 5 retries")

def run_ocr(pdf_bytes, file_hash):
    cache = f"./ocr_cache_{file_hash}.md"
    
    if os.path.exists(cache):
        with open(cache, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(), True

    total = None
    results = {}

    progress = st.progress(0, text="Starting OCR...")
    
    for i, img_bytes, total in pdf_to_images(pdf_bytes):
        i, text = ocr_page((i, img_bytes))
        results[i] = text
        progress.progress(len(results) / total, text=f"OCR: page {i+1} of {total}")

    progress.empty()
    md = "\n\n".join(f"--- Page {i+1} ---\n\n{results[i]}" for i in sorted(results))
    
    with open(cache, "w", encoding="utf-8") as f:
        f.write(md)
        
    return md, False


@st.cache_resource
def build_index(file_hash, md_text):
    Settings.embed_model = GeminiEmbedding(
        model_name="models/gemini-embedding-001",
        api_key=GEMINI_API_KEY
    )
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 50

    persist = f"{INDEX_DIR}_{file_hash}"
    if os.path.exists(persist) and os.listdir(persist):
        return load_index_from_storage(StorageContext.from_defaults(persist_dir=persist))

    nodes = SentenceSplitter(chunk_size=1024, chunk_overlap=50).get_nodes_from_documents([Document(text=md_text)])
    idx = VectorStoreIndex(nodes)
    idx.storage_context.persist(persist_dir=persist)
    return idx


def make_chat_engine(index, model_name=GITHUB_MODEL):
    Settings.llm = OpenAILike(
        model=model_name,
        api_base="https://models.inference.ai.azure.com",
        api_key=GITHUB_TOKEN,
        is_chat_model=True,
        request_timeout=60.0,
        max_tokens=2048,
    )
    return index.as_chat_engine(
        chat_mode="context",
        memory=ChatMemoryBuffer.from_defaults(token_limit=8000),
        system_prompt="Answer using the document context only. If unsure, say so."
    )

# UI part
st.set_page_config(page_title="PDF Chat", layout="centered")
st.title("PDF Chat")
st.caption("OCR via Gemini — Embeddings via Gemini — Chat via gpt-4o")

if "messages"    not in st.session_state: st.session_state.messages = []
if "chat_engine" not in st.session_state: st.session_state.chat_engine = None
if "pdf_name"    not in st.session_state: st.session_state.pdf_name = None
if "index"       not in st.session_state: st.session_state.index = None
if "model"       not in st.session_state: st.session_state.model = GITHUB_MODEL

with st.sidebar:
    st.header("Document")

    if not GITHUB_TOKEN:
        st.error("GITHUB_TOKEN not found in .env")
        st.stop()
    if not GEMINI_API_KEY:
        st.error("GEMINI_API_KEY not found in .env")
        st.stop()

    uploaded = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded and st.session_state.pdf_name != uploaded.name:
        st.session_state.messages = []
        st.session_state.chat_engine = None
        st.session_state.pdf_name = uploaded.name

        pdf_bytes = uploaded.read()
        file_hash = hashlib.md5(pdf_bytes).hexdigest()[:8]

        with st.spinner("Running OCR via Gemini..."):
            md, cached = run_ocr(pdf_bytes, file_hash)
        st.success("Loaded from cache" if cached else "OCR complete")

        with st.spinner("Building index..."):
            index = build_index(file_hash, md)
            st.session_state.index = index

        st.session_state.chat_engine = make_chat_engine(index, st.session_state.model)
        st.success("Ready!")

    if st.session_state.pdf_name:
        st.divider()
        st.caption(f"{st.session_state.pdf_name}")

        if st.button("Clear chat"):
            st.session_state.messages = []
            st.rerun()

if not st.session_state.chat_engine:
    st.info("Upload a PDF in the sidebar to get started.")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask anything about the document..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chat_engine.chat(prompt)
            st.markdown(response.response)
            st.session_state.messages.append({"role": "assistant", "content": response.response})