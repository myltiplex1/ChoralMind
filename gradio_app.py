import time
import gradio as gr
from retriever.retriever import HymnRetriever
from llm.generate_response import generate_hymn_response
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Hymn search function
def search_hymn_gradio(language, query):
    logger.info(f"Language selected: {language}")
    logger.info(f"Hymn search query: {query}")
    
    if not query.strip():
        return ""

    retriever = HymnRetriever()
    retrieved_hymns = retriever.retrieve(query, language.lower())

    if not retrieved_hymns:
        logger.info(f"No hymns found for query: '{query}' in {language}")
        return f"No matching hymns found in {language}. Try another line."
    
    logger.info("Generating response with retrieved hymns")
    return generate_hymn_response(retrieved_hymns, query, language.lower())

# Language change: update placeholder + clear boxes
def on_language_change(language):
    if language == "English":
        placeholder = "Type a line from the hymn e.g All hail the power of Jesus name..."
    else:
        placeholder = "Type a line from the hymn e.g FORE ofę ba awa gbe..."

    return gr.update(value="", placeholder=placeholder), gr.update(value="")

# Clear results
def clear_results():
    return ""

# UI
with gr.Blocks() as demo:
    gr.Markdown("# 🎶 ChoralMind — Hymn Search")
    gr.Markdown("Find hymns in **English** or **Yoruba**.")

    with gr.Row():
        with gr.Column(scale=1):
            language = gr.Dropdown(
                choices=["English", "Yoruba"],
                value="English",
                label="Choose Language"
            )

            query = gr.Textbox(
                placeholder="Type a line from the hymn e.g All hail the power of Jesus name...",
                label="Hymn Line",
                lines=2
            )

            search_btn = gr.Button("🔍 Search")

        with gr.Column(scale=2):
            output = gr.Textbox(
                label="Search Result",
                lines=15
            )

            clear_btn = gr.Button("🗑 Clear Results")

    # Language change → placeholder update & clear fields
    language.change(
        fn=on_language_change,
        inputs=[language],
        outputs=[query, output]
    )

    # Search triggered only by Search button click
    search_btn.click(
        fn=search_hymn_gradio,
        inputs=[language, query],
        outputs=output
    )

    # Clear button
    clear_btn.click(
        fn=clear_results,
        outputs=output
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port, pwa=True, favicon_path="assets/icon-192x192.png")
