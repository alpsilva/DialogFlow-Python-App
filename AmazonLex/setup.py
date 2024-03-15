from dotenv import load_dotenv
from pprint import pprint
from time import sleep
import boto3
import os

load_dotenv()

lex_client = boto3.client('lexv2-models')

def create_bot(bot_name: str, bot_alias: str, bot_locale: str, iam_role_arn: str):
    """ 
    Receives:
    - bot_name (str),
    - bot_alias (str) (such as TEST | PROD | etc),
    - bot_locale (str) (such as pt_BR | en_US | etc), # https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html
    - iam_role_arn (str),
    
    Creates a new Amazon Lex bot with the specified name, under the given IAM role.
    Creates a new version for the bot.
    Creates a new locale with the specified language code and loads this language intents.
    Creates a new alias with the specified alias name.

    Returns the new bot ID and and AliasID.
    """
    timeout = 20 * 60 # Time in seconds the bot will retain information about a particular conversation.
    bot_version = "DRAFT"

    create_bot_res = lex_client.create_bot(
        botName=bot_name,
        roleArn=iam_role_arn,
        dataPrivacy={
            'childDirected': False
        },
        idleSessionTTLInSeconds=timeout
    )

    new_bot_id = create_bot_res['botId']
    print(f"Newly created bot ID: {new_bot_id}")
    sleep(5)

    # create bot version
    create_bot_version_res = lex_client.create_bot_version(
        botId=new_bot_id,
        description="First version of the bot.",
        botVersionLocaleSpecification={
            bot_locale: {
                'sourceBotVersion': bot_version
            }
        }
    )

    new_bot_version_number = create_bot_version_res['botVersion']
    print(f"Newly created bot version number: {new_bot_version_number}")
    sleep(5)

    # Determines the threshold where Amazon Lex will insert the AMAZON.FallbackIntent, AMAZON.KendraSearchIntent, or both when returning alternative intents.
    # AMAZON.FallbackIntent and AMAZON.KendraSearchIntent are only inserted if they are configured for the bot.
    # Basically determines the minimum value of confidence needed for intent assertion, from a scale 0 ~ 1.
    # 0.4 is the default value in the AWS Console.

    # For example, suppose a bot is configured with the confidence threshold of 0.80 and the AMAZON.FallbackIntent.
    # Amazon Lex returns three alternative intents with the following confidence scores: IntentA (0.70), IntentB (0.60), IntentC (0.50).
    # The response from the RecognizeText operation would be:
    # - AMAZON.FallbackIntent
    # - IntentA
    # - IntentB
    # - IntentC

    nlu_intent_confidence_thresold = 0.4

    create_bot_locale_res = lex_client.create_bot_locale(
        botId=new_bot_id,
        botVersion=bot_version, # ?
        localeId=bot_locale,
        nluIntentConfidenceThreshold=nlu_intent_confidence_thresold,
    )
    sleep(5)

    create_bot_alias_res = lex_client.create_bot_alias(
        botAliasName=bot_alias,
        description="Staging alias for testing purposes.",
        botVersion=new_bot_version_number,
        botId=new_bot_id,
    )

    new_bot_alias_id = create_bot_alias_res['botAliasId']
    print(f"Newly created bot alias ID: {new_bot_alias_id}")
    sleep(5)

    return new_bot_id, new_bot_alias_id

def load_intents():
    # This may be useful:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lexv2-models/client/create_intent.html
    pass

def update_bot():
    pass

def delete_bot(bot_id):
    response = lex_client.delete_bot(
        botId=bot_id,
        skipResourceInUseCheck=True
    )

    return dict(response)

def list_bots():
    """ List all Amazon Lex bots in the region. """
    print("List of Lex bots in the region:")
    bots = lex_client.list_bots()['botSummaries']
    for bot in bots:
        pprint(bot)
        print()
    print("=" * 20)

def list_bot_aliases(bot_id: str):
    """ List all Amazon Lex bots aliases associated with the bot Id. """
    print(f"List of Lex bots aliases for the bot ID {bot_id}:")
    aliases = lex_client.list_bot_aliases(botId=bot_id)['botAliasSummaries']
    for alias in aliases:
        pprint(alias)
        print()
    print("=" * 20)

name = "TestBotPrototype"
alias_name = "TestBotPrototypeAlias"
locale = "pt_BR"

iam_arn = os.getenv("LEX_BOTS_IAM_ROLE_ARN")

# list_bots()

# id, alias_id = create_bot(name, alias_name, locale, iam_arn)
# delete_res = delete_bot("86HPBIGNRJ")
# sleep(5)

list_bots()
list_bot_aliases("X1VYHNVBJV")
