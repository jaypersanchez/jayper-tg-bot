from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os
import fitz
import json
from fuzzywuzzy import fuzz, process
import re
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')  # Optional, for multilingual support
from nltk.corpus import wordnet

# Load environment variables from .env file
load_dotenv()

# Retrieve the token from the environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Load questions and answers from JSON file
with open('resume_qa.json', 'r') as file:
    qa_data = json.load(file)

def get_synonyms(word):
    """Get synonyms for a given word using NLTK's WordNet."""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

def find_answer(question):
    """Find the answer to the question from the QA data, considering variations and fuzzy matching."""
    question_lower = question.lower().strip()
    print(f"User question: {question_lower}")

    # Create a list of all variations for comparison
    all_variations = []
    for qa in qa_data['questions']:
        all_variations.extend(qa['variations'])

    # Use fuzzy matching to find the closest variation
    closest_match = process.extractOne(question_lower, all_variations, scorer=fuzz.partial_ratio)
    
    if closest_match:
        closest_variation = closest_match[0]
        for qa in qa_data['questions']:
            if closest_variation in qa['variations']:
                return qa['answer']

    return "Sorry, I couldn't find an answer to your question."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Respond with an answer based on the PDF content."""
    user_message = update.message.text
    answer = find_answer(user_message)
    await update.message.reply_text(answer)

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("JayperBot is running...")
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
