import boto3
class LexBotController:
    def __init__(self, bot_id, bot_name, bot_alias_id, bot_alias_name, bot_locale) -> None:
        self.client = boto3.client('lexv2-models')
        self.id = bot_id
        self.name = bot_name
        self.alias_id = bot_alias_id
        self.alias_name = bot_alias_name
        self.locale = bot_locale
        self.version = "DRAFT" # Study how to best represent a bot version here.
        self.validator

    def get_client(self):
        return self.client
    
    def get_status(self):
        """
        Returns the status of the bot in the cloud.
        status can be on of:
        'Creating'|'Available'|'Inactive'|'Deleting'|'Failed'|'Versioning'|'Importing'|'Updating'
        """
        bot_info = self.client.describe_bot(botId=self.id)
        return bot_info['botStatus']

    def build(self):
        """ Requests a build of the bot and waits for it to finish. """
        self.client.build_bot_locale(
            botId=self.id,
            botVersion=self.version,
            localeId=self.locale
        )

        wait_time = 5
        print("Build requested. Checking status...")
        status = "Updating"
        while status == "Updating":
            status = self.get_status()
            print(f"Current status: {status}. Checking again in {wait_time} seconds...")
        
        print(f"Build finished with status: {status}")

    def create_new_version(self, version_description: str):
        """ creates a new version of the bot and return the version id. """ 
        response = self.client.create_bot_version(
            botId=self.id,
            botVersionLocaleSpecification={
                self.locale: {
                    'sourceBotVersion': self.version
                }
            },
            description=version_description
        )

        return response['botVersion']

    def list_versions(self):
        """ List all Amazon Lex bot versions associated with this bot ID. """
        versions = self.client.list_bot_versions(botId=self.id)['botVersionSummaries']
        output = [ dict(version) for version in versions ]
        return output

    def update_alias(self, version_id: str):
        """ updates the alias to point to the version_id """
        self.client.update_bot_alias(
            botId=self.id,
            botAliasId=self.alias_id,
            botAliasName=self.alias_name,
            botVersion=version_id,
            botAliasLocaleSettings={
                self.locale: {
                    'enabled': True,
                }
            },
        )

    def list_aliases(self):
        """ List all Amazon Lex bots aliases associated with this bot ID. """
        aliases = self.client.list_bot_aliases(botId=self.id)['botAliasSummaries']
        output = [ dict(alias) for alias in aliases ]
        return output
    
    def create_intent(self, intent_name: str, description: dict, sample_utterances: list):
        """ creates a new intent in the bot and returns the intent id. """
        response = self.client.create_intent(
            botId=self.id,
            botVersion=self.version,
            localeId=self.locale,
            intentName=intent_name,
            description=description,
            sampleUtterances=sample_utterances,
        )

        return response['intentId']
    
    def update_intent(self, intent_name: str, description: dict, sample_utterances: list, slot_priorities: list = None):
        """ Updates an intent in the bot. """
        update_dict = {
            'botId': self.id,
            'botVersion': self.version,
            'localeId': self.locale,
            'intentName': intent_name,
            'description': description,
            'sampleUtterances': sample_utterances,
        }

        if slot_priorities:
            update_dict['slotPriorities'] = slot_priorities
        
        self.client.update_intent(**update_dict)

    def list_intents(self):
        """ List all Amazon Lex intents associated with this bot. """
        intents = self.client.list_intents(
            botId=self.id,
            botVersion = self.version,
            localeId=self.locale
        )['intentSummaries']
        output = [ dict(version) for version in intents ]
        return output


    def create_slot(self, intent_id: str, name: str, type_id: str, description: str, value_elicitation_setting: dict):
        """ creates a new slot in the bot, for the given intent, and returns the slot id. """
        response = self.client.create_slot(
            botId=self.id,
            botVersion=self.version,
            localeId=self.locale,
            intentId=intent_id,
            slotName=name,
            slotTypeId=type_id,
            description=description,
            valueElicitationSetting=value_elicitation_setting
        )

        return response['slotId']
    
    def update_slot(self, intent_id: str, name: str, type_id: str, description: str, value_elicitation_setting: dict):
        """ Updates a slot in the bot. """
        update_dict = {
            'botId':self.id,
            'botVersion':self.version,
            'localeId':self.locale,
            'intentId':intent_id,
            'slotName':name,
            'slotTypeId':type_id,
            'description':description,
            'valueElicitationSetting':value_elicitation_setting
        }

        self.client.update_slot(**update_dict)