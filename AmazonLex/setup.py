from dotenv import load_dotenv
from datetime import datetime
from pprint import pprint
from time import sleep
import boto3
import json
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

def upload_intents(bot_id, bot_alias_id, bot_alias_name, bot_locale):
    """ Uploads the intents in the dict to the Amazon Lex bot identified by the bot id and alias id. """


    def load_intents():
        """ Consumes intents.json and returns intents as a dict. """
        file_path = "./intents/sample.json"
        intents = {}

        with open(file_path, 'r') as json_file:
            intents = json.load(json_file)

        return intents

    intents = load_intents()
    now = str(datetime.now())
    bot_version = "DRAFT"
    
    # Create new bot version
    response = lex_client.create_bot_version(
        botId=bot_id,
        botVersionLocaleSpecification={
            bot_locale: {
                'sourceBotVersion': bot_version
            }
        },
        description=f"Version with intents uploaded on {now}"
    )

    new_version_id = response['botVersion']

    # Sleeps for 5 seconds in order for the new version to finish processing in the cloud.
    sleep(5)

    # Update alias to point to new version  
    response = lex_client.update_bot_alias(
        botId=bot_id,
        botAliasId=bot_alias_id,
        botAliasName=bot_alias_name,
        # botVersion=bot_version,
        botVersion=new_version_id,
        botAliasLocaleSettings={
            bot_locale: {
                'enabled': True,
            }
        },
    )

    for intent_name, intent_data in intents.items():
        utterance_data = [
            {'utterance': utterance}
            for utterance
            in intent_data['sampleUtterances']
        ]

        try:
            intent_response = lex_client.create_intent(
                botId=bot_id,
                botVersion=bot_version,
                localeId=locale,
                intentName=intent_name,
                description=intent_data['description'],
                sampleUtterances=utterance_data,
            )
        except Exception as e:
            print(f"Error while creating intent {intent_name}:")
            print(e)
            print("Skipping...")
            pass

        intent_id = intent_response['intentId']

        print(f"Intent {intent_name} created with ID {intent_id}.")

        slots = intent_data['slots']
        slots_priorites = []

        for index, slot_data in enumerate(slots):
            slot_name = slot_data['name']
            slot_type = slot_data['slotType']
            slot_description = slot_data['description']
            value_elicitation_setting = slot_data['valueElicitationSetting']

            try:
                slot_response = lex_client.create_slot(
                    botId=bot_id,
                    botVersion=bot_version,
                    localeId=locale,
                    intentId=intent_id,
                    slotName=slot_name,
                    slotTypeId=slot_type,
                    description=slot_description,
                    valueElicitationSetting=value_elicitation_setting
                )

                slot_id = slot_response['slotId']
                print(f"Slot {slot_name} created with ID {slot_id} for Intent {intent_name}.")

                slots_priorites.append({
                    'priority': index,
                    'slotId': slot_id
                })

            except Exception as e:
                print(f"Error while creating slot {slot_name}:")
                print(e)
                print("Skipping...")
                pass
        
        print(f"Updating slot priorities for intent {intent_name}...")
        try:
            update_response = lex_client.update_intent(
                botId=bot_id,
                botVersion=bot_version,
                localeId=locale,
                intentId=intent_id,
                intentName=intent_name,
                description=intent_data['description'],
                sampleUtterances=utterance_data,
                slotPriorities=slots_priorites
            )
        except Exception as e:
            print(f"Error while updating intent {intent_name}:")
            print(e)
            print("Skipping...")
            pass
        


    print(f"Intents uploaded to bot {bot_id} alias {bot_alias_id}. Proceeding to build alias...")

    build_response = lex_client.build_bot_locale(
        botId=bot_id,
        botVersion=bot_version,
        localeId=locale
    )

    sleep(5)

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

def list_bot_versions(bot_id: str):
    """ List all Amazon Lex bot versions associated with the bot Id. """
    print(f"List of Lex bots versions for the bot ID {bot_id}:")
    versions = lex_client.list_bot_versions(botId=bot_id)['botVersionSummaries']
    for version in versions:
        pprint(version)
        print()
    print("=" * 20)

name = "TestBotPrototype"
alias_name = "TestBotPrototypeAlias"
locale = "pt_BR"

iam_arn = os.getenv("LEX_BOTS_IAM_ROLE_ARN")

# id, alias_id = create_bot(name, alias_name, locale, iam_arn)
# delete_res = delete_bot("86HPBIGNRJ")
# sleep(5)

bot_id = "X1VYHNVBJV"
bot_alias_id = "C7PGMSD1KT"

list_bots()
list_bot_aliases(bot_id)
# list_bot_versions(bot_id)

# upload_intents(bot_id, bot_alias_id, alias_name, locale)