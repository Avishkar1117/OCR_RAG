# PDF Chat

A fully offline RAG (Retrieval-Augmented Generation) application that lets you chat with any PDF document. All processing runs locally on your machine using Ollama — no API keys, no internet required after setup, no data leaves your device.

## How it works

The pipeline runs in three sequential stages, each designed to stay within tight RAM budgets by unloading models from memory as soon as they are no longer needed.

Stage 1 — OCR: Each page of the uploaded PDF is rendered as an image and passed to a local vision model (qwen2.5vl) which extracts text and tables as clean Markdown. Pages are cached to disk so re-uploads skip this step entirely.

Stage 2 — Indexing: The extracted Markdown is chunked, embedded using nomic-embed-text, and stored in a local vector index. The index is persisted to disk per document so it only needs to be built once.

Stage 3 — Chat: A local LLM (qwen3) answers questions using only the retrieved document context. Conversation history is maintained within the session.

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.9 or higher
- Ollama installed — https://ollama.com/download
- 16GB RAM minimum (models load and unload sequentially to stay within budget)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/pdf-chat.git
cd pdf-chat
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull the required Ollama models

Run these once. They download to your local Ollama model store and are reused across sessions.

```bash
ollama pull qwen2.5vl:3b
ollama pull qwen3:4b
ollama pull nomic-embed-text
```

### 4. Run the app

```bash
streamlit run app.py
```

The app opens automatically at http://localhost:8501

## Usage

1. Open the app in your browser
2. Upload a PDF using the sidebar
3. Wait for OCR and indexing to complete (first upload only)
4. Ask questions in the chat input

On subsequent uploads of the same PDF, the app loads from cache and skips OCR and re-indexing entirely.

## Performance notes

First run on a new PDF takes 30 to 90 seconds depending on page count and hardware. Re-uploads are near instant. On 16GB RAM systems, avoid running memory-heavy applications alongside the app during the OCR stage.

## Project structure

```
pdf-chat/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
├── README.md
├── ocr_cache_*.md       # Auto-generated OCR cache files (gitignored)
└── index_store_*/       # Auto-generated vector index folders (gitignored)
```

## .gitignore recommendation

Add the following to avoid committing large generated files:

```
ocr_cache_*.md
index_store_*/
__pycache__/
*.pyc
```

## Models used

| Model | Purpose | Size on disk |
|---|---|---|
| qwen2.5vl:3b | Vision OCR — extracts text from PDF page images | ~3.5 GB |
| qwen3:4b | LLM — answers questions from retrieved context | ~3.5 GB |
| nomic-embed-text | Embeddings — converts text chunks to vectors | ~0.5 GB |

## Limitations

- Scanned PDFs with handwriting may produce lower quality OCR output
- Very large PDFs (50+ pages) will take several minutes on first processing
- Only one document is active per session; uploading a new PDF starts a fresh chat

## License

MIT