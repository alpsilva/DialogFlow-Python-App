import boto3
from pprint import pprint

lex_client = boto3.client('lexv2-models')

def create_bot():
    pass

def delete_bot():
    pass

def list_bots():
    """ List all Amazon Lex bots in the region. """
    bots = lex_client.list_bots()['botSummaries']
    for bot in bots:
        pprint(bot)
        print()

list_bots()
