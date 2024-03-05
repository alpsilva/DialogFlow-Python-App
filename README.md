# NLP Prototype

This prototype was made using Google's DialogFlow, following this tutorial: https://medium.com/google-cloud/working-with-dialogflow-cx-via-python-b44f6c2721e0.

## Relevant Documentation
- https://cloud.google.com/python/docs/reference/dialogflow-cx/latest/google.cloud.dialogflowcx_v3.services.agents.AgentsClient
- https://cloud.google.com/python/docs/reference/dialogflow-cx/latest/google.cloud.dialogflowcx_v3.services.sessions.SessionsClient#google_cloud_dialogflowcx_v3_services_sessions_SessionsClient_detect_intent

# Setting up Google Cloud Platform Credentials
1. Install and initialize [GCloud CLI.](https://cloud.google.com/sdk/docs/install)
2. Create your credential file:
```sh
gcloud auth application-default login
```

# Installing requirements
```sh
pip install -r requirements.txt
```

# Creating DialogFlow project into GCP
Simply run setup.py after altering the necessary parameters inside the code.
```sh
python3 setup.py
```
Note the auto-generated DialogFlow Agent Name. It must be inserted in the prototype file next.

# Running prototype
1. Change the AGENT_NAME variable to the auto-generated DialogFlow Agent Name in the last step.
2. Run prototype.py:
```sh
python3 prototype.py
```

# Roadmap
- [x] Infra as code
- [] Creation of more intents as code
- [] Improve confiability
- [] Integrate with chatbot
