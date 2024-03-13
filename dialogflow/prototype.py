from google.cloud.dialogflowcx_v3 import SessionsClient, AgentsClient
from google.cloud.dialogflowcx_v3.types import session
from dotenv import load_dotenv
import os

load_dotenv()

from setup import PROJECT_ID, LOCATION, LANGUAGE
# Defined when creating a new agent.
# Do not confuse with display name that is given by you.
AGENT_NAME = os.getenv('DIALOGFLOW_AGENT_NAME') # This is auto-generated during the setup phase.

def compose_agent(project_id: str, location_id: str, agent_id: str):
    agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"
    return agent

def detect_intent_text(agent, session_id, text, language_code):
    """Returns the result of detect intent with text as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    session_path = f"{agent}/sessions/{session_id}"
    print(f"Session path: {session_path}\n")
    client_options = None
    agent_components = AgentsClient.parse_agent_path(agent)
    location_id = agent_components["location"]
    if location_id != "global":
        api_endpoint = f"{location_id}-dialogflow.googleapis.com:443"
        print(f"API Endpoint: {api_endpoint}\n")
        client_options = {"api_endpoint": api_endpoint}
    session_client = SessionsClient(client_options=client_options)

    text_input = session.TextInput(text=text)
    query_input = session.QueryInput(text=text_input, language_code=language_code)
    request = session.DetectIntentRequest(
        session=session_path, query_input=query_input
    )
    response = session_client.detect_intent(request=request)

    user_intent = response.query_result.intent.display_name
    intent_detection_confidance = response.query_result.intent_detection_confidence
    intent_detection_confidance = round(float(intent_detection_confidance), 2)

    print(f"Query text: {response.query_result.text}")
    response_messages = [
        " ".join(msg.text.text) for msg in response.query_result.response_messages
    ]
    
    print("=" * 20)
    print(f"user intent: {user_intent}")
    print(f"intent detection confidance: {intent_detection_confidance}")
    
    print(f"Response text: {' '.join(response_messages)}\n")

user_input = "Hambúrguer"

# You also need a session ID.
# A session represents a conversation between a Dialogflow agent and an end-user.
# You create a unique session ID at the beginning of a conversation and use it for
# each turn of the conversation. For the purpose of trying the API, you can use any
# string ID that is at most 36 bytes, like "test-session-123".
# After integration, this should be something unique to each user and easily identifiable,
# such as the user's phone number.
session_id = "f66ac8ec-02ee-4774-bce6-aa588104d82b" #generated with uuid lib.

agent = compose_agent(PROJECT_ID, LOCATION, AGENT_NAME)
detect_intent_texts(agent, session_id, user_input, LANGUAGE)
