from datetime import datetime
from pprint import pprint
from time import sleep
import boto3
import json

class LexBot:
    def __init__(self, bot_id, bot_name, bot_alias_id, bot_alias_name, bot_locale) -> None:
        self.client = boto3.client('lexv2-models')
        self.id = bot_id
        self.name = bot_name
        self.alias_id = bot_alias_id
        self.alias_name = bot_alias_name
        self.locale = bot_locale
        self.version = "DRAFT" # Study how to best represent a bot version here.

    def get_status(self):
        """
        Returns the status of the bot in the cloud.
        status can be on of:
        'Creating'|'Available'|'Inactive'|'Deleting'|'Failed'|'Versioning'|'Importing'|'Updating'
        """
        bot_info = self.client.describe_bot(botId=self.id)
        return bot_info['botStatus']

    def detect_intent_text(self, session_id, text):
        """
        Returns the result of detect intent with text as input.

        Using the same `session_id` between requests allows keeping context of the conversations.
        Each user should have it's own session id.
        """
        # Submit the text 'I would like to see a dentist'
        response = self.client.recognize_text(
            botId=self.id,
            botAliasId=self.alias_name,
            localeId=self.locale,
            sessionId=session_id,
            text=text
        )

        pprint(response)
        
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

    def _upload_intents(self, intents: dict):
        """ Uploads the intents in the dict to the Amazon Lex bot identified by the bot id and alias id. """
        now = str(datetime.now())

        # Create new bot version
        response = self.client.create_bot_version(
            botId=self.id,
            botVersionLocaleSpecification={
                self.locale: {
                    'sourceBotVersion': self.version
                }
            },
            description=f"Version with intents uploaded on {now}"
        )

        new_version_id = response['botVersion']

        # Sleeps for 5 seconds in order for the new version to finish processing in the cloud.
        sleep(5)

        # Update alias to point to new version  
        response = self.client.update_bot_alias(
            botId=self.id,
            botAliasId=self.alias_id,
            botAliasName=self.alias_name,
            botVersion=new_version_id,
            botAliasLocaleSettings={
                self.locale: {
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
                intent_response = self.client.create_intent(
                    botId=self.id,
                    botVersion=self.version,
                    localeId=self.locale,
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
                    slot_response = self.client.create_slot(
                        botId=self.id,
                        botVersion=self.version,
                        localeId=self.locale,
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
                update_response = self.client.update_intent(
                    botId=self.id,
                    botVersion=self.version,
                    localeId=self.locale,
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
            


        print(f"Intents uploaded to bot {self.bot_id} alias {self.bot_alias_id}. Proceeding to build alias...")

        build_response = self.client.build_bot_locale(
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

    def upload_intents_from_file(self, file_path: str):
        """ Consumes the json file and returns intents as a dict. """
        intents = {}

        with open(file_path, 'r') as json_file:
            intents = json.load(json_file)

        self._upload_intents(intents)

    def list_intents(self):
        """ List all Amazon Lex intents associated with this bot. """
        intents = self.client.list_intents(
            botId=self.id,
            botVersion = self.version,
            localeId=self.locale
        )['intentSummaries']
        output = [ dict(version) for version in intents ]
        return output

    def list_aliases(self):
        """ List all Amazon Lex bots aliases associated with this bot ID. """
        aliases = self.client.list_bot_aliases(botId=self.id)['botAliasSummaries']
        output = [ dict(alias) for alias in aliases ]
        return output
    
    def update_alias(self, new_version_id: str):
        """ Update the alias to point to a new version. """
        # https://docs.aws.amazon.com/lexv2/latest/dg/versions-aliases.html
        #TODO
        pass

    def list_versions(self):
        """ List all Amazon Lex bot versions associated with this bot ID. """
        versions = self.client.list_bot_versions(botId=self.id)['botVersionSummaries']
        output = [ dict(version) for version in versions ]
        return output
    
    def create_new_version(self):
        """ creates a new bot version. """
        #TODO
        pass