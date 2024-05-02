from lex_manager import LexManager
from dotenv import load_dotenv
from pprint import pprint
from time import sleep
import os
from uuid import uuid4

load_dotenv()

iam_arn = os.getenv("LEX_BOTS_IAM_ROLE_ARN")

manager = LexManager(iam_arn)
manager.list_bots()

bot_id = os.getenv('BOT_ID')
bot_name = os.getenv('BOT_NAME')
bot_alias_id = os.getenv('BOT_ALIAS_ID')
bot_alias_name = os.getenv('BOT_ALIAS_NAME')
bot_locale = os.getenv('BOT_LOCALE_ID')

bot = manager.get_bot(bot_id, bot_alias_id, bot_locale)

intents_file_path = "../AmazonLex/intents/sample.json"
bot.upload_intents_from_file(intents_file_path)

session_id = str(uuid4())
print(session_id)

texts = [
    "Quero me registrar",
    "André Luiz",
    "alpsilva.dev@gmail.com",
    "masculino",
    "16/07/1998",
    "sim",
    "Quero realizar um registro de relato",
    "12/04/2024",
    "15:00",
    "ônibus",
    "Flashing",
    "sim"
]

session_state = None
for i, text in enumerate(texts):
    print(f"Turn {i + 1}:")
    print(f"User message: {text}")

    intent, session_state, confidence, bot_response = bot.detect_intent_text(session_id, text, session_state)
    
    pprint(session_state)

    print(f"Intent: {intent}")
    print(f"State: {session_state['dialogAction']['type']}")
    print(f"NLU confidence: {confidence}")
    print(f"Bot Response: {bot_response}")
    print ("=" * 25)
    print()

    sleep(3)