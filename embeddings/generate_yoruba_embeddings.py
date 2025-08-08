import os
import re
import json
import logging
import pdfplumber
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

def extract_yoruba_hymns():
    pdf_path = "docs/Yoruba/yoruba_hymns.pdf"
    logger.info(f"Reading {pdf_path}")
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

    # Normalize spaces
    text = re.sub(r"\r", "", text)

    # Match real hymn headers only
    # e.g., "1 ORIN OWURO", "3 OJO ISIMI"
    hymn_header_pattern = re.compile(
        r"(?m)^(?P<num>\d{1,3})\s+(?P<title>(ORIN|OJO|OLORUN|OLUWA|IBI|AFERI|NIGBA|JESU|BABA|MO|EMI|EGBE|IGBALA|IYIN|INU|O)\b[^\n]*)"
    )

    matches = list(hymn_header_pattern.finditer(text))
    hymns = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end].strip()

        number = int(match.group("num"))
        title = match.group("title").strip()

        hymns.append({
            "number": number,
            "title": title,
            "text": block
        })

    os.makedirs("data/yoruba", exist_ok=True)
    with open("data/yoruba/hymns.json", "w", encoding="utf-8") as f:
        json.dump(hymns, f, ensure_ascii=False, indent=2)

    logger.info(f"Extracted {len(hymns)} Yoruba hymns")
    return hymns

def generate_yoruba_embeddings():
    hymns = extract_yoruba_hymns()

    documents = []
    for hymn_id, hymn in enumerate(hymns):
        documents.append({
            "text": hymn["text"],
            "hymn_id": hymn_id,
            "chunk_id": 0
        })

    logger.info(f"Embedding {len(documents)} Yoruba hymns")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    texts = [doc["text"] for doc in documents]
    metadatas = [{"hymn_id": doc["hymn_id"], "chunk_id": doc["chunk_id"]} for doc in documents]
    vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

    os.makedirs("embeddings", exist_ok=True)
    vector_store.save_local("embeddings/yoruba_index.faiss")
    logger.info("Yoruba FAISS index saved")

if __name__ == "__main__":
    generate_yoruba_embeddings()
