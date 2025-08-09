# 🎶 ChoralMind – Hymn Search Bot

ChoralMind is a Telegram bot that helps you search and retrieve **English** and **Yoruba** hymns using semantic search with FAISS embeddings.

Try here: 
https://choralmind.onrender.com?__theme=dark
                    or
https://huggingface.co/spaces/timflash/ChoralMind
          

## 📌 Features
- Search hymns in **English** and **Yoruba** by typing any line from the hymn.
- Retrieves relevant hymns using **Google Generative AI embeddings** (`models/text-embedding-004`).
- Supports multilingual hymn databases with separate FAISS indexes.
- Interactive **language selection** via Telegram inline buttons.
- Logs all bot activity for debugging and analytics.
- Maintains `hymn_id` mapping so results link back to the full hymn text.

## 🛠 Tech Stack
- **Python 3.12**
- python-telegram-bot
- LangChain for text chunking and FAISS vector storage
- Google Generative AI API for embeddings
- FAISS for similarity search
- pdfplumber for PDF hymn extraction
- Gradio for interactive web interface

## 📂 Project Structure
```
├── docs/                # hymns PDF source  
├── data/                # Extracted hymns in JSON  
├── embeddings/          # embedding scripts and FAISS Index  
├── retriever/  
│   └── retriever.py     # HymnRetriever class  
├── llm/  
│   └── generate_response.py   # Formats retrieved results into Telegram reply  
├── telegran_bot         # Telegram bot entrypoint  
│   └── bot.py  
├── main.py              # main program  
├── requirements.txt     # Python dependencies
|── gradio_app.py        # interactive web interface


```

## ⚙️ Installation
**Clone the repository**
```bash
git clone https://github.com/yourusername/choralmind.git
cd ChoralMind
```

## 📦 Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## 📥 Install Dependencies
```bash
pip install -r requirements.txt
```

## ⚙️ Set Up Environment Variables
Create a `.env` file:
```ini
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_google_generative_ai_key
```

---

## 📜 Extracting Hymns & Generating Embeddings

### Yoruba Hymns
```bash
python python embeddings/generate_yoruba_embeddings.py
```
- Parses **all PDFs** in `docs/Yoruba/`
- Uses regex to detect hymn headers based on the hymn book structure
- Merges all verses for each hymn into one record
- Splits text into chunks and generates embeddings
- Saves FAISS index in `embeddings/yoruba_index.faiss`

### English Hymns
```bash
python python embeddings/generate_english_embeddings.py
```
- Reads **all PDFs** in `docs/English/`
- Extracts text in **two-column format** (left & right) based on the hymn book structure
- Splits hymns by patterns into chunks and generates embeddings
- Saves to `data/english/hymns.json`
- Generates **FAISS embeddings** and saves to `embeddings/english_index.faiss`

---

## ▶️ Running the Bot
```bash
python main.py
```
## 🚀 Running the Gradio App

This project uses [Gradio](https://gradio.app) to provide an interactive web interface.

```bash
python gradio_app.py
```
---

---

## 💬 Usage Flow
1. **User starts the bot** → Bot sends greeting:
    ```vbnet
    Hello, I'm ChoralMind 🎶
    Click /start to choose your language and search.
    ```
2. **User clicks `/start`** → Bot shows **English / Yoruba** buttons.
3. **User chooses a language**.
4. **User sends any line from a hymn**.
5. **Bot returns top matching hymns with context**.

---

---

## 📜 License
MIT License – feel free to modify and distribute.

---

## 🙌 Credits
- Hymn content from [https://books.google.com.ng/books?id=NONpPAAACAAJ&printsec=frontcover&source=gbs_atb#v=onepage&q&f=false]
                    [https://gospelriver.com/gospelhymnbookuk/Gospel_Hymnbook_UK.pdf]
- Powered by **Google Generative AI** & **LangChain**
- Bot built with **python-telegram-bot**
