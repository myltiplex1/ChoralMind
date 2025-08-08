import os

def create_project_structure():
    # Define project structure
    folders = [
        "docs",
        "data/english",
        "data/yoruba",
        "embeddings",
        "retriever",
        "llm",
        "telegram_bot"
    ]
    files = [
        "main.py",
        "embeddings/generate_english_embeddings.py",
        "embeddings/generate_yoruba_embeddings.py",
        "retriever/retriever.py",
        "llm/generate_response.py",
        "telegram_bot/bot.py",
        "requirements.txt",
        ".env"
    ]

    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

    # Create empty files
    for file in files:
        with open(file, "w") as f:
            pass
        print(f"Created file: {file}")

if __name__ == "__main__":
    create_project_structure()