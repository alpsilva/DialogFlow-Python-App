# Amazon Lex Prototype

Built using official documentation for Amazon Lex V2:

- https://docs.aws.amazon.com/lexv2/latest/dg/gs-console.html
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lexv2-models.html

# Supported Language Codes
https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html

# How to run:

1. Configure your aws account credentials so boto3 can connect to the resources:
```sh
aws configure
```

2. Create the Lex Bot (TODO)
Run setup.py:
```sh
python3 setup.py
```

This script will create a Lex Bot and supply it with examples of intent.

3. Create a .env file in the folder "AmazonLex". Insert the following variables with values generated in the set up phase

| Variable                  | Value                             |
|---------------------------|-----------------------------------|
| BOT_ID                    | Your Lex Bot ID ID.               |
| BOT_ALIAS                 | Your Lex Bot Alias.               |
| BOT_LOCALE_ID             | Your Lex Bot language code.       |
| LEX_BOTS_IAM_ROLE_ARN     | Role ARN with Lex Access rights.  |



# Run Protot