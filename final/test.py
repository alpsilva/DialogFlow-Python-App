from dotenv import load_dotenv
from lex_manager import LexManager
from lex_bot import LexBot
import os

load_dotenv()

iam_arn = os.getenv("LEX_BOTS_IAM_ROLE_ARN")

manager = LexManager(iam_arn)

manager.list_bots()

# bot = manager.get_bot(prototype_bot_id)

bot_id = os.getenv('BOT_ID')
bot_name = os.getenv('BOT_NAME')
bot_alias_id = os.getenv('BOT_ALIAS_ID')
bot_alias_name = os.getenv('BOT_ALIAS_NAME')
bot_locale = os.getenv('BOT_LOCALE_ID')

bot = LexBot(bot_id, bot_name, bot_alias_id, bot_alias_name, bot_locale)
print(bot.get_status())