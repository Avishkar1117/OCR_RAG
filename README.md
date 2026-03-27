# Local Multi-Modal RAG: Vision OCR & Agentic Analysis 👁️🧠📄

This project is an advanced, 100% local Retrieval-Augmented Generation (RAG) pipeline. Unlike standard RAG systems that rely on simple text scrapers (which fail on scanned documents, complex tables, and charts), this project uses a **Vision-Language Model (VLM)** to visually "read" PDF pages via OCR. The structured output is then fed into an Agentic state machine for high-accuracy analysis.

## ✨ Key Features
* **True Visual OCR:** Converts PDF pages into mathematically optimized images and feeds them to Qwen 2.5-VL. The AI "sees" the document, perfectly preserving markdown tables, lists, and formatting from scanned or complex PDFs.
* **Hardware-Optimized:** Features a custom Python image-processing layer using `Pillow` to dynamically scale page dimensions into perfect 28x28 pixel grids, preventing `llama.cpp` tensor crashes and ensuring smooth execution on mid-tier hardware (~8GB RAM).
* **Two-Pass Agentic Analysis:** Utilizes a state machine (LangGraph) to generate a "Draft" answer from the OCR text, and then self-reflects/refines it to eliminate hallucinations before presenting the "Final" answer.
* **100% Local & Private:** Runs entirely on local hardware using Ollama. Zero data is sent to the cloud.

## 🛠️ Tech Stack
* **Vision & Extraction LLM:** Qwen 2.5-VL (3B) via Ollama
* **Analysis LLM:** Qwen 3 (4B) via Ollama
* **Document Processing:** PyMuPDF (`fitz`) & Pillow (`PIL`)
* **Embeddings:** Nomic-Embed-Text
* **Orchestration:** LangGraph & LangChain

## 🚀 How to Run
1. Clone this repository.
2. Install the required Python dependencies:
   bash
   pip install langchain langchain-ollama langgraph pymupdf Pillow chromadb
4. Ensure you have Ollama installed and running. Pull the necessary local models:
   Bash
   ollama pull qwen2.5vl:3b   # The Vision OCR Model
   ollama pull qwen3:4b       # The Agentic Reasoning Model
   ollama pull nomic-embed-text # The Embedding Model
6. Place your target PDF in the project directory.
7. Open the Jupyter Notebook (.ipynb) in VS Code, ensure your Python environment is selected, and run the cells!
