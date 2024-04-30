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

    def detect_intent(self, session_id, text):
        """
        Returns the result of detect intent with text as input.

        Using the same `session_id` between requests allows keeping context of the conversations.
        Each user should have it's own session id.
        """
        response = self.client.recognize_text(
            botId=self.id,
            botAliasId=self.alias_name,
            localeId=self.locale,
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
    
    def list_intents(self):
        """ List all Amazon Lex intents associated with this bot, in this intent. """
        intents = self.client.list_intents(
            botId=self.id,
            botVersion = self.version,
            localeId=self.locale
        )['intentSummaries']
        output = [ dict(intent) for intent in intents ]
        return output

    def intent_exists(self, name: str):
        """ Checks if the intent exists in the bot. Returns id if True, None if False """
        intents = self.list_intents()
        output = None
        for intent in intents:
            if intent['intentName'] == name:
                output = intent['intentId']

        return output

    def upsert_intent(self, name: str, description: dict, sample_utterances: list):
        """ Inserts (or updates if already exists) intent in the bot and returns the intent id. """
        intent_id = self.intent_exists(name)

        if intent_id:
            self.update_intent(name, description, sample_utterances)
        else:
            intent_id = self.insert_intent(name, description, sample_utterances)

        return intent_id
        
    def insert_intent(self, name: str, description: dict, sample_utterances: list):
        """ inserts a new intent in the bot and returns the intent id. """
        response = self.client.create_intent(
            botId=self.id,
            botVersion=self.version,
            localeId=self.locale,
            intentName=name,
            description=description,
            sampleUtterances=sample_utterances,
        )

        return response['intentId']
    
    def update_intent(self, name: str, description: dict, sample_utterances: list, slot_priorities: list = None):
        """ Updates an intent in the bot. """
        update_dict = {
            'botId': self.id,
            'botVersion': self.version,
            'localeId': self.locale,
            'intentName': name,
            'description': description,
            'sampleUtterances': sample_utterances,
        }

        if slot_priorities:
            update_dict['slotPriorities'] = slot_priorities
        
        self.client.update_intent(**update_dict)

    def list_slots(self, intent_id):
        """ List all Amazon Lex slots associated with this bot, in this intent. """
        slots = self.client.list_slots(
            botId=self.id,
            botVersion = self.version,
            localeId=self.locale,
            intentId=intent_id
        )['slotSummaries']
        output = [ dict(slot) for slot in slots ]
        return output

    def slot_exists(self, name: str):
        """ Checks if the slot exists in the bot. Returns id if True, None if False """
        slots = self.list_slots()
        output = None
        for slot in slots:
            if slot['slotName'] == name:
                output = slot['slotId']

        return output

    def upsert_slot(self, intent_id: str, name: str, type_id: str, description: str, value_elicitation_setting: dict):
        """ Inserts (or updates if already exists) slot in the bot, for the given intent, and returns the slot id. """
        slot_id = self.slot_exists(name)

        if slot_id:
            self.update_slot(intent_id, name, type_id, description, value_elicitation_setting)
        else:
            slot_id = self.insert_slot(intent_id, name, type_id, description, value_elicitation_setting)

        return slot_id

    def insert_slot(self, intent_id: str, name: str, type_id: str, description: str, value_elicitation_setting: dict):
        """ inserts a new slot in the bot, for the given intent, and returns the slot id. """
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