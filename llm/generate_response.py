import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

def generate_hymn_response(retrieved_hymns, query, language):
    logger.info(f"Generating response for query: '{query}' in {language}")
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    logger.info("Formatting retrieved hymns for Gemini prompt")
    context = "\n\n".join([
        f"Hymn #{h['hymn_id']}\n{h['text']}" for h in retrieved_hymns
    ])

    prompt =f"""
You are a hymn search assistant. The user asked for a {language.upper()} hymn containing the line: "{query}".

Below are hymn excerpts retrieved from a hymnal. Some may contain the full hymn, others may be partial.

Your task:
- Identify the full hymn if possible.
- Start a new stanza with a new line (blank space between stanzas).
- Number each stanza sequentially (1., 2., 3., etc.).
- If the hymn appears fragmented, stitch together all matching chunks.
- Output ONLY the hymn text.
- Do NOT include a "Retrieved hymn excerpts" section or any reference to hymn numbers or scores unless it's part of the hymn itself.
- Preserve original punctuation and wording exactly as in the excerpts.

Hymn excerpts:
{context}
"""

    logger.info("Sending prompt to Gemini")
    try:
        response = model.generate_content(prompt)
        logger.info("Response generated successfully")
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Sorry, something went wrong while generating the hymn response."