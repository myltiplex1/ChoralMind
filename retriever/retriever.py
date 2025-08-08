import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

class HymnRetriever:
    def __init__(self):
        logger.info("Initializing HymnRetriever")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        logger.info("Loading English FAISS index")
        self.english_vector_store = FAISS.load_local(
            "embeddings/english_index.faiss", self.embeddings, allow_dangerous_deserialization=True
        )
        logger.info("Loading Yoruba FAISS index")
        self.yoruba_vector_store = FAISS.load_local(
            "embeddings/yoruba_index.faiss", self.embeddings, allow_dangerous_deserialization=True
        )
        logger.info("HymnRetriever initialized")

    def retrieve(self, query, language, k=3):
        logger.info(f"Retrieving hymns for query: '{query}' in {language}")
        vector_store = self.english_vector_store if language == "english" else self.yoruba_vector_store
        results = vector_store.similarity_search_with_score(query, k=k)
        
        retrieved_hymns = []
        for doc, score in results:
            retrieved_hymns.append({
                "text": doc.page_content,
                "hymn_id": doc.metadata["hymn_id"],
                "chunk_id": doc.metadata["chunk_id"],
                "score": score
            })
        
        logger.info(f"Retrieved {len(retrieved_hymns)} hymns")
        return retrieved_hymns