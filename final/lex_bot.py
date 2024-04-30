from datetime import datetime
from pprint import pprint
from time import sleep
import boto3
import json
from lex_bot_controller import LexBotController

class LexBot:
    def __init__(self, bot_id, bot_name, bot_alias_id, bot_alias_name, bot_locale) -> None:
        self.id = bot_id
        self.name = bot_name
        self.alias_id = bot_alias_id
        self.alias_name = bot_alias_name
        self.locale = bot_locale
        self.controller = LexBotController(bot_id, bot_name, bot_alias_id, bot_alias_name, bot_locale)

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

        new_version_id = self.controller.create_new_version(f"Version with intents uploaded on {now}")

        # Sleeps for 5 seconds in order for the new version to finish processing in the cloud.
        sleep(5)

        # Update alias to point to new version  
        self.controller.update_alias(new_version_id)

        for intent_name, intent_data in intents.items():            
            sample_utterances = [
                {'utterance': utterance}
                for utterance
                in intent_data['sampleUtterances']
            ]

            description = intent_data['description']
            
            # TODO: will throw an error if the intent already exists. In that case, should update instead.
            intent_id = self.controller.create_intent(intent_name, description, sample_utterances)
            print(f"Intent {intent_name} created with ID {intent_id}.")

            slots = intent_data['slots']
            slots_priorites = []

            for index, slot_data in enumerate(slots):
                slot_name = slot_data['name']
                slot_type = slot_data['slotType']
                slot_description = slot_data['description']
                value_elicitation_setting = slot_data['valueElicitationSetting']

                # TODO: will throw an error if the intent already exists. In that case, should update instead.
                slot_id = self.controller.create_slot(
                    intent_id, slot_name, slot_type, slot_description, value_elicitation_setting
                )
                print(f"Slot {slot_name} created with ID {slot_id} for Intent {intent_name}.")

                slots_priorites.append({
                    'priority': index,
                    'slotId': slot_id
                })

            print(f"Updating slot priorities for intent {intent_name}...")
            self.controller.update_intent(intent_id, intent_name, description, sample_utterances, slots_priorites)

        print(f"Intents uploaded to bot {self.bot_id} alias {self.bot_alias_id}. Proceeding to build alias...")

    def upload_intents_from_file(self, file_path: str):
        """ Consumes the json file and returns intents as a dict. """
        intents = {}

        with open(file_path, 'r') as json_file:
            intents = json.load(json_file)

        self._upload_intents(intents)