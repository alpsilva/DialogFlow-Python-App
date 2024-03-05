# Importing the required Libraries from dialogflowcx_v3
from google.cloud.dialogflowcx_v3 import AgentsClient, ExportAgentRequest
from google.cloud.dialogflowcx_v3.types.agent import Agent

"""
Create Dialogflow CX Agent with the Parameters provided:
 - project_id - Google Cloud Project in which the Agent will be created
 - location - Region where the Agent will reside
 - name - Name of the Agent
 - agent_name - Display Name of the Agent
 - language_code - The Language in which the Agent will be created.
 - time_zone - Time zome followed by the agent
The function returns the Agent created as an object of type 
google.cloud.dialogflowcx_v3.types.Agent
It contains the system generated name of the agent with the format 
- projects/<project_id>/locations/<location>/agents/<Unique ID for agent>
"""
def create_agent(project_id:str, location:str, agent_name:str, language_code:str, time_zone:str):
    parent = f"projects/{project_id}/locations/{location}"
    agents_client = AgentsClient()

    agent = Agent(
        name=agent_name,
        display_name=agent_name,
        default_language_code=language_code,
        time_zone=time_zone
    )

    response=agents_client.create_agent(request={"agent": agent, "parent": parent})
    return response

"""
Delete the Dialogflow CX Agent with the Parameters provided:
 - agent_name - System generated unique name of the Agent of the format 
 - projects/<project_id>/locations/<location>/agents/<Unique ID created for the agent>
The function returns None
"""
def delete_agent(agent_name:str):
    agents_client = AgentsClient()
    response = agents_client.delete_agent(name=agent_name)


"""
List all the Dialogflow CX Agents in the Project and location. 
The Parameters required are:
 - project_id - Agents of this Google Cloud Project will be listed
 - location - Agents of this Region will be listed
The function returns the list of Agent created as an object of type 
google.cloud.dialogflowcx_v3.services.agents.pagers.ListAgentsPager
"""
def list_agents(project_id:str, location:str):
    parent = f"projects/{project_id}/locations/{location}"
    agents_client = AgentsClient()

    response = agents_client.list_agents(parent=parent)
    return response


"""
Exports the Dialogflow CX Agent with the Parameters provided:
 - agent_name - System generated unique name of the Agent of the format 
 - projects/<project_id>/locations/<location>/agents/<Unique ID created for the agent>
The function returns the long running operation as an object of type 
google.api_core.operation.Operation
The result of the operation is an object of type 
google.cloud.dialogflowcx_v3.types.agent.ExportAgentResponse
"""
def export_agent(agent_name:str):
    agents_client = AgentsClient()
    request = ExportAgentRequest(name=agent_name)

    export_operation = agents_client.export_agent(request=request)
    print("Waiting for the Operation to complete")

    response = export_operation.result()
    return response