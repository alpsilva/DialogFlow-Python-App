from dotenv import load_dotenv
from pprint import pprint
from time import sleep
from uuid import uuid4
import boto3
import os

load_dotenv()

# LexV2 client uses 'lexv2-runtime'
client = boto3.client('lexv2-runtime')

def detect_intent_text(bot_id, bot_alias, locale_id, session_id, text):
    """
    Returns the result of detect intent with text as input.

    Using the same `session_id` between requests allows continuation
    of the conversation.
    """
    # Submit the text 'I would like to see a dentist'
    response = client.recognize_text(
        botId=bot_id,
        botAliasId=bot_alias,
        localeId=locale_id,
        sessionId=session_id,
        text=text
    )
    
    intent, confidence, bot_response = None, -1, None
    
    bot_response = response['messages'][0]['content']

    interpretations = response['interpretations']
    session_state = response['sessionState']['dialogAction']['type']

    if len(interpretations) > 0:
        most_confident = interpretations[0]
        intent = most_confident['intent']['name']
        
        if session_state != "ConfirmIntent":
            confidence = most_confident['nluConfidence']['score']

    return intent, session_state, confidence, bot_response

bot_id = os.getenv('BOT_ID')
bot_alias = os.getenv('BOT_ALIAS')
locale_id = os.getenv('BOT_LOCALE_ID')

# This controls if the messages belong to the same thread, to help with context.
session_id = str(uuid4())

texts = [
    "Gostaria de pedir umas flores",
    "Margaridas.",
    "Este sábado.",
    "15 horas.",
]

for i, text in enumerate(texts):
    print(f"Turn {i + 1}:")
    
    intent, state, confidence, bot_response = detect_intent_text(bot_id, bot_alias, locale_id, session_id, text)
    
    print(f"User message: {text}")
    print(f"Intent: {intent}")
    print(f"State: {state}")
    print(f"NLU confidence: {confidence}")
    print(f"Bot Response: {bot_response}")
    print ("=" * 25)
    print()

    sleep(3)
