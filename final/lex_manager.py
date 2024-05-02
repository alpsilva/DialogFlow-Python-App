from lex_bot import LexBot
from pprint import pprint
from time import sleep
import boto3

class LexManager:
    def __init__(self, iam_role_arn) -> None:
        self.client = boto3.client('lexv2-models')
        self.iam_role_arn = iam_role_arn

    def create_bot(self, bot_name: str, bot_alias: str, bot_locale: str):
        """ 
        Receives:
        - bot_name (str),
        - bot_alias (str) (such as TEST | PROD | etc),
        - bot_locale (str) (such as pt_BR | en_US | etc), # https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html
        
        Creates a new Amazon Lex bot with the specified name, under the given IAM role.
        Creates a new version for the bot.
        Creates a new locale with the specified language code and loads this language intents.
        Creates a new alias with the specified alias name.

        Returns the new bot ID and and AliasID.
        """
        timeout = 20 * 60 # Time in seconds the bot will retain information about a particular conversation.
        bot_version = "DRAFT"

        create_bot_res = self.client.create_bot(
            botName=bot_name,
            roleArn=self.iam_role_arn,
            dataPrivacy={
                'childDirected': False
            },
            idleSessionTTLInSeconds=timeout
        )

        new_bot_id = create_bot_res['botId']
        print(f"Newly created bot ID: {new_bot_id}")
        sleep(5)

        # create bot version
        create_bot_version_res = self.client.create_bot_version(
            botId=new_bot_id,
            description=f"First version of the bot {bot_name}.",
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

        create_bot_locale_res = self.client.create_bot_locale(
            botId=new_bot_id,
            botVersion=bot_version, # ?
            localeId=bot_locale,
            nluIntentConfidenceThreshold=nlu_intent_confidence_thresold,
        )
        sleep(5)

        create_bot_alias_res = self.client.create_bot_alias(
            botAliasName=bot_alias,
            description="Staging alias for testing purposes.",
            botVersion=new_bot_version_number,
            botId=new_bot_id,
        )

        new_bot_alias_id = create_bot_alias_res['botAliasId']
        print(f"Newly created bot alias ID: {new_bot_alias_id}")
        sleep(5)

        return new_bot_id, new_bot_alias_id

    def list_bots(self):
        """ List all Amazon Lex bots in the region. """
        bots = self.client.list_bots()['botSummaries']
        output = [ dict(bot) for bot in bots ]
        return output

    def get_bot(self, bot_id, bot_alias_id, bot_locale) -> LexBot:
        """
        Returns LexBot class. For a bot to be specified in the cloud, it is needed:
        - botId (identifier of the bot).
        - botAliasId (identifier of specific bot alias. Aliases point to specific versions to ease integration).
        - localeId (Language code, such as pt_BR, within the bot).
        """
        bot_info = self.client.describe_bot(botId=bot_id)
        bot_name = bot_info['botName']

        bot_alias_info = self.client.describe_bot_alias(botId=bot_id, botAliasId=bot_alias_id)
        bot_alias_name = bot_alias_info['botAliasName']

        bot = LexBot(bot_id, bot_name, bot_alias_id, bot_alias_name, bot_locale)
        return bot

    def delete_bot(self, bot_id):
        response = self.client.delete_bot(
            botId=bot_id,
            skipResourceInUseCheck=True
        )

        return dict(response)

    def list_bot_aliases(self, bot_id: str):
        """ List all Amazon Lex bots aliases associated with the bot Id. """
        print(f"List of Lex bots aliases for the bot ID {bot_id}:")
        aliases = self.client.list_bot_aliases(botId=bot_id)['botAliasSummaries']
        output = [ dict(alias) for alias in aliases ]
        return output

    def list_bot_versions(self, bot_id: str):
        """ List all Amazon Lex bot versions associated with the bot Id. """
        print(f"List of Lex bots versions for the bot ID {bot_id}:")
        versions = self.client.list_bot_versions(botId=bot_id)['botVersionSummaries']
        output = [ dict(version) for version in versions ]
        return output