# Multi-Modal RAG: Vision OCR + LlamaIndex (Qwen 3 Edition)

It solves the "Scanned PDF Problem" by using a **Vision-Language Model (VLM)** to visually extract data and **LlamaIndex** to intelligently structure that data for precision querying.

## ✨ Technical Highlights
* **Multi-Modal OCR Engine:** Uses `qwen2.5vl:3b` to visually "see" the PDF. Unlike standard text scrapers, this preserves complex Markdown tables, headers, and bullet points.
* **Hardware-First Engineering:** * **Math-Safe Images:** Resizes PDF pages to 28x28 pixel grids using `Pillow` to prevent engine crashes.
  * **Memory Capping:** Limits the reasoning model's context to `4096` tokens, allowing high-tier models to run on standard 12GB RAM environments.
* **Intelligent Structural Parsing:** Uses LlamaIndex's `MarkdownNodeParser` to chunk data based on document hierarchy (Headers/Tables) rather than arbitrary character counts.
* **Optimized Reasoning:** Leverages the **Qwen 3 (4B)** model for fast, accurate local inference.

## 🛠️ The Local Tech Stack
* **OCR (Vision):** `qwen2.5vl:3b` (The "Eyes")
* **Embeddings:** `nomic-embed-text` (The "Librarian")
* **Reasoning:** `qwen3:4b` (The "Thinker")
* **Orchestration:** LlamaIndex
* **Processing:** PyMuPDF (`fitz`) & Pillow (`PIL`)

## 🚀 The Pipeline Logic
1. **Visual Capture:** PDF pages are converted to images at a scale that ensures AI readability.
2. **Vision Extraction:** The VLM converts visual images into a structured `extracted_text.md` file.
3. **LlamaIndex Indexing:** * The Markdown is parsed into **Nodes** based on its structural layout.
   * Nodes are converted into vectors (mathematical coordinates) and stored in an in-memory index.
4. **Contextual Querying:** When asked a question, the system retrieves only the relevant structural nodes and feeds them to **Qwen 3** for a final, grounded answer.

## 💻 Setup & Usage (Colab)
1. **Install Linux dependencies:** `sudo apt-get install -y zstd`
2. **Install Ollama:** `curl -fsSL https://ollama.com/install.sh | sh`
3. **Initialize Server:** `nohup ollama serve > server.log 2>&1 &`
4. **Pull Models:**
   ```bash
   ollama pull qwen2.5vl:3b
   ollama pull nomic-embed-text
   ollama pull qwen3:4b
6. Upload your PDF and run the Python pipeline!
