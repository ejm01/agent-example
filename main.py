import os
from dotenv import load_dotenv
from email_client import EmailClient
from email_handling import process_inbox_flow
from openai import OpenAI
load_dotenv()

def main():
    email_address = os.getenv('EMAIL_ADDRESS_TEST')
    password = os.getenv('EMAIL_PASSWORD_TEST')
    imap_server = os.getenv('IMAP_SERVER_TEST')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if not all([email_address, password, imap_server]):
        print("Please set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables")
        return

    client = EmailClient(email_address, password, imap_server)  
    client.connect()  
    process_inbox_flow(client, openai_api_key)


if __name__ == "__main__":
    main()
