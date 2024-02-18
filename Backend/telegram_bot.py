from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from main import create_trivia_clip
import logging

# Enable logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Token provided by BotFather
TOKEN = '6980476570:AAHC-r83NEo83zwAKLatyRE4F3VC2uZZJgw'
user_preferences = {}  # A simple way to store user preferences based on their chat ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! Use /create <topic> to generate a trivia video.')

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user = update.message.from_user
    language = user_preferences.get(user_id, "english")  # Default to English if no preference is set
 
    logger.info("User %s started the creation process.", user.first_name)
    
    # Extracting the topic from the command
    topic = ' '.join(context.args)

    if not topic:
        await update.message.reply_text('Please provide a topic after the command. E.g., "/create science"')
        return
    
    # Let the user know we're working on it, it will take a while
    await update.message.reply_text(f"Creating a trivia video on the topic: {topic}. This will take a while...")

    # Assume create_trivia_clip is an async function or adjust accordingly
    video_path = create_trivia_clip(topic, language=language)
    
    # Send the video
    with open(video_path, 'rb') as video:
        await update.message.reply_video(video, caption=f"Here's your trivia video on the topic: {topic}")

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Expecting the command format to be: /language <language_name>
    if len(context.args) == 1:
        language = context.args[0].lower()  # Normalize the language input to lowercase
        user_preferences[user_id] = language  # Store the user's language preference
        await update.message.reply_text(f"Language set to {language.capitalize()}.")
    else:
        await update.message.reply_text("Please specify the language. Usage: /language <language_name>")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create", create))
    # Add the /language command handler
    application.add_handler(CommandHandler("language", set_language))

    application.run_polling()

if __name__ == '__main__':
    main()

