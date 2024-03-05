import agent_operations
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
LOCATION = "global"
AGENT_DISPLAY_NAME = "DialogFlowPythonAppPrototype"
LANGUAGE = "pt-br"
TIME_ZONE = "America/Buenos_Aires"

if __name__ == "__main__":
	# Create Agent and specify the project, location, agent_name, language, and time zone parameters
	agent_response = agent_operations.create_agent(
		PROJECT_ID,
		LOCATION,
		AGENT_DISPLAY_NAME,
		LANGUAGE,
		TIME_ZONE)
	print(agent_response)

	# The system generated agent name is the name key in the agent response returned
	# agent_name = agent_response.name

	# List all the agent in the specified project and location
	agent_list = agent_operations.list_agents(PROJECT_ID, LOCATION)
	print(agent_list)

	# # Export the agent specified by its system generated agent name
	# agent_export_response = agent_operations.export_agent(agent_name)
	# print(agent_export_response)

	# # Delete the agent specified by its system generated agent name
	# agent_operations.delete_agent(agent_name)