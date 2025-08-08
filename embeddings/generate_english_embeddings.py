import pdfplumber
import json
import os
import logging
import re
import glob
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()


def extract_english_hymns():
    folder_path = "docs/English"
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF(s) in {folder_path}")

    full_text = ""
    for pdf_path in pdf_files:
        logger.info(f"Extracting hymns from {pdf_path}")
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                width, height = page.width, page.height

                # Left and right column extraction
                left = page.within_bbox((0, 0, width / 2, height))
                right = page.within_bbox((width / 2, 0, width, height))

                left_text = left.extract_text() or ""
                right_text = right.extract_text() or ""
                page_text = left_text + "\n" + right_text
                full_text += page_text + "\n"

    logger.info("Splitting text into hymns using pattern anchors")
    split_pattern = r'(?=\b(?:Tune\s+-|B\.H\.B\.|S\.S\.|R\.S\.|R\.H\.|P\.M\.|\d{1,2}[-\d]+|C\.M\.|L\.M\.)\b)'
    raw_hymns = re.split(split_pattern, full_text)

    hymns = []
    for hymn in raw_hymns:
        cleaned = hymn.strip()
        if len(cleaned.split()) >= 10:
            hymns.append({"text": cleaned})

    logger.info(f"Extracted {len(hymns)} English hymns from all PDFs")

    os.makedirs("data/english", exist_ok=True)
    output_path = "data/english/hymns.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hymns, f, ensure_ascii=False, indent=2)

    return hymns


def generate_english_embeddings():
    logger.info("Starting English embeddings generation")

    hymns = extract_english_hymns()

    logger.info("Splitting hymns into chunks")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    documents = []
    for hymn in hymns:
        text = hymn["text"].strip()
        if not text:
            continue
        chunks = text_splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            documents.append({
                "text": chunk,
                "hymn_id": hymns.index(hymn),
                "chunk_id": i
            })

    logger.info(f"Created {len(documents)} document chunks")

    if not documents:
        logger.warning("No document chunks created. Embedding will not proceed.")
        return

    logger.info("Generating embeddings with GoogleGenerativeAIEmbeddings")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    logger.info("Creating FAISS index")
    texts = [doc["text"] for doc in documents]
    metadatas = [{"hymn_id": doc["hymn_id"], "chunk_id": doc["chunk_id"]} for doc in documents]
    vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

    output_path = "embeddings/english_index.faiss"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    logger.info(f"Saving FAISS index to {output_path}")
    vector_store.save_local(output_path)

    logger.info("English embeddings generation completed")


if __name__ == "__main__":
    generate_english_embeddings()