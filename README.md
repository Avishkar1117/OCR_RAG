# PDF Chat

A lightweight, cloud-powered RAG (Retrieval-Augmented Generation) application that lets you chat with any PDF document using OCR. This app uses Google's Gemini API for high-quality OCR and embeddings, and GitHub Models for flexible chat model like GPT-4o.

## How it works

The pipeline runs in three sequential stages:

**Stage 1 — OCR:** Each page of the uploaded PDF is rendered as an image using PyMuPDF and passed to a Gemini  model (here, `gemini-2.5-flash-lite`). The AI extracts text and tables as clean Markdown. Pages are cached to disk locally so re-uploads skip this step entirely.

**Stage 2 — Indexing:** The extracted Markdown is chunked, embedded using Google's `gemini-embedding-001` model, and stored in a local vector index via LlamaIndex. The index is persisted to disk per document so it only needs to be built once.

**Stage 3 — Chat:** A cloud LLM routed through GitHub Models answers questions using only the retrieved document context using `gpt-40`. Conversation history is maintained within the session.

## Requirements

- Python 3.10 or higher
- A [Google AI Studio](https://aistudio.google.com/) API Key (Free tier works great)
- A [GitHub Personal Access Token](https://github.com/settings/tokens) (Classic or Fine-grained) with access to GitHub Models.

## Setup

### 1. Clone the repository

```bash
git clone [https://github.com/your-username/pdf-chat.git](https://github.com/your-username/pdf-chat.git)
cd pdf-chat
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a file named .env in the root directory of the project and add your API keys:

GEMINI_API_KEY=your_google_gemini_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here

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

First run on a new PDF takes 30 to 90 seconds depending on page count and hardware. Re-uploads are near instant.

## Project structure

```
pdf-chat/
├── app.py               # Main Streamlit application
├── .env                 # API Keys
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

## Models used & Architecture History

This project was built to be flexible. It has been successfully tested using both a lightweight cloud-powered pipeline and a fully offline local pipeline. Both combinations work effectively depending on your privacy needs and hardware capabilities.

### Current Setup: Cloud-Powered (Fast & Lightweight)
The default configuration uses cloud APIs to offload the heavy lifting, making it runnable on almost any machine:
* **Vision OCR & Embeddings (Google Gemini):** Uses `gemini-2.5-flash-lite` for incredibly fast and accurate text/table extraction from images, and `gemini-embedding-001` for high-dimensional semantic search.
* **Chat LLM (GitHub Models):** Routes through GitHub's inference API, allowing you the use of model `gpt-4o`.

### Alternative Setup: Fully Local (Privacy-First via Ollama)
The app was originally designed to run 100% locally using Ollama, ensuring no data ever leaves the device. If adapting the code back to local, the following stack was used:
* **Vision OCR:** `qwen2.5vl:3b` 
* **Chat LLM:** `qwen3:4b` 
* **Embeddings:** `nomic-embed-text`

**Hardware Restrictions for Local Execution:** Running the fully local Ollama pipeline requires a **minimum of 16GB RAM**. Because vision and chat models are highly memory-intensive, the pipeline is designed to load and unload these models sequentially. For example, the `qwen2.5vl` model must be completely purged from memory after the OCR stage finishes before the `qwen3` chat model can be loaded to answer questions.

## Output for current models
These are the outputs from streamlit UI

<img width="926" height="1197" alt="Screenshot 2026-03-28 194023" src="https://github.com/user-attachments/assets/b2754ae9-ff90-451e-bf53-2b5efbca80c6" />

<img width="916" height="1194" alt="Screenshot 2026-03-28 194051" src="https://github.com/user-attachments/assets/0510eaac-7703-4063-8b60-41e88bef5b68" />


## Limitations

- Scanned PDFs with handwriting may produce lower quality OCR output
- Very large PDFs (50+ pages) will take several minutes on first processing
- Only one document is active per session; uploading a new PDF starts a fresh chat

## License

MIT
