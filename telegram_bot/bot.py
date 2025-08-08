from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ChatMemberHandler, filters, ContextTypes
from retriever.retriever import HymnRetriever
from llm.generate_response import generate_hymn_response
from dotenv import load_dotenv
import os
import logging

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

WELCOME_MESSAGE = (
    "Hello, I'm ChoralMind! 🎶\n"
    "I can help you find hymns in English or Yoruba. "
    "Please choose a language:"
)

async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the welcome message with language selection buttons."""
    logger.info("Sending welcome message with language selection")
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data="english"),
            InlineKeyboardButton("Yoruba", callback_data="yoruba")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(WELCOME_MESSAGE, reply_markup=reply_markup)
    logger.info("Sent welcome message and language selection prompt")

async def chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new chat members to send welcome message when bot is added."""
    my_chat_member = update.my_chat_member
    new_status = my_chat_member.new_chat_member.status
    logger.info(f"Chat member update received. New status: {new_status}")

    # Trigger when the bot is added to a chat or a private chat is started
    if new_status in ['member', 'administrator']:
        await send_welcome_message(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command to resend welcome message and buttons."""
    logger.info("Received /start command")
    await send_welcome_message(update, context)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear the user's conversation data."""
    logger.info("Received /clear command")
    context.user_data.clear()  # Clear user-specific data
    await update.message.reply_text(
        "Conversation cleared! Click /start or wait for the welcome message to begin again.\n"
        "Note: To manage or forget this chat from my memory, go to the 'Data Controls' section in your settings "
        "or click the book icon beneath this message to select this chat for removal."
    )
    logger.info("Cleared user data and sent confirmation")
    # Resend welcome message after clearing
    await send_welcome_message(update, context)

async def language_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection from inline buttons."""
    query = update.callback_query
    await query.answer()
    language = query.data
    context.user_data["language"] = language
    logger.info(f"User selected language: {language}")
    await query.message.reply_text(f"Selected {language.capitalize()}. Enter a line from the hymn to search:")
    logger.info("Prompted user for hymn line")

async def search_hymn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hymn search queries."""
    query = update.message.text
    language = context.user_data.get("language", None)
    
    logger.info(f"Received hymn search query: '{query}'")
    if not language:
        logger.warning("No language selected for query")
        await update.message.reply_text(
            "Please select a language first. Use /start or wait for the welcome message."
        )
        await send_welcome_message(update, context)
        return
    
    logger.info(f"Retrieving hymns for language: {language}")
    retriever = HymnRetriever()
    retrieved_hymns = retriever.retrieve(query, language)
    
    if not retrieved_hymns:
        logger.info(f"No hymns found for query: '{query}' in {language}")
        await update.message.reply_text(
            f"No matching hymns found in {language.capitalize()}. Try another line."
        )
        return
    
    logger.info("Generating response with retrieved hymns")
    response = generate_hymn_response(retrieved_hymns, query, language)
    await update.message.reply_text(response)
    logger.info("Sent response to user")

def main():
    logger.info("Starting Telegram bot")
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear))
    
    # Chat member handler for new chats
    application.add_handler(ChatMemberHandler(chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    
    # Callback and message handlers
    application.add_handler(CallbackQueryHandler(language_choice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_hymn))
    
    logger.info("Bot polling started")
    application.run_polling()

if __name__ == "__main__":
    main()