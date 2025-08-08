import gradio as gr
from retriever.retriever import HymnRetriever
from llm.generate_response import generate_hymn_response
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hymn search function for Gradio
def search_hymn_gradio(language, query):
    logger.info(f"Language selected: {language}")
    logger.info(f"Hymn search query: {query}")
    
    if not query.strip():
        return "Please enter a line from the hymn to search."

    retriever = HymnRetriever()
    retrieved_hymns = retriever.retrieve(query, language.lower())

    if not retrieved_hymns:
        logger.info(f"No hymns found for query: '{query}' in {language}")
        return f"No matching hymns found in {language}. Try another line."
    
    logger.info("Generating response with retrieved hymns")
    response = generate_hymn_response(retrieved_hymns, query, language.lower())
    return response

# Function to clear the result box
def clear_results():
    return ""

# Gradio UI (instant search)
with gr.Blocks() as demo:
    gr.Markdown("# 🎶 ChoralMind — Hymn Search")
    gr.Markdown("Find hymns in **English** or **Yoruba** instantly as you type.")

    with gr.Row():
        with gr.Column(scale=1):
            language = gr.Dropdown(
                choices=["English", "Yoruba"],
                value="English",
                label="Choose Language"
            )

            query = gr.Textbox(
                placeholder="Type a line from the hymn...",
                label="Hymn Line",
                lines=2
            )

        with gr.Column(scale=2):
            output = gr.Textbox(
                label="Search Result",
                lines=15
            )

            clear_btn = gr.Button("🗑 Clear Results")

    # Instant search — triggers when either language changes or query changes
    language.change(
        fn=search_hymn_gradio,
        inputs=[language, query],
        outputs=output
    )

    query.input(  # Fires as the user types
        fn=search_hymn_gradio,
        inputs=[language, query],
        outputs=output
    )

    # Clear results
    clear_btn.click(
        fn=clear_results,
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(pwa=True,favicon_path="assets/icon-192x192.png")
