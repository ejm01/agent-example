import os
from typing import Dict, Any, Optional

import backoff
from openai import OpenAI, RateLimitError

from email_client import EmailClient
from post_processing import (
    extract_draft_reply,
    extract_action_item,
    process_action_item
)

# Mock tenant data for testing
MOCK_TENANTS = {
    "domostakehome01+ex1@gmail.com": {
        "name": "John Smith",
        "address": "100 Greenwich Ave",
        "apartment": "2A", 
        "phone": "212-555-0101"
    },
    "domostakehome01+ex2@gmail.com": {
        "name": "Mary Johnson",
        "address": "2000 Holland Av",
        "apartment": "1F",
        "phone": "212-555-0102"
    },
    "domostakehome01+ex3@gmail.com": {
        "name": "Robert Davis",
        "address": "789 Oak Avenue",
        "apartment": "4C",
        "phone": "212-555-0103"
    },
    "domostakehome01+ex4@gmail.com": {
        "name": "Wilkin Dan",
        "address": "123 Maple Street",
        "apartment": "1F",
        "phone": "212-555-0104"
    }
}

def get_tenant_info(email_address: str) -> Optional[Dict[str, Any]]:
    tenant = MOCK_TENANTS.get(email_address)
    if not tenant:
        print(f"Tenant not found: {email_address}")
        return None
    # This would be a call to persistence in real app
    # currently just get the mock data
    return tenant.copy()

# use exponential backoff for openai rate limit errors
@backoff.on_exception(backoff.expo, RateLimitError)
def chat_completions_with_backoff(client, **kwargs):
    try:
        return client.chat.completions.create(**kwargs)
    except Exception as e:
        print(f"[chat_completions_with_backoff] Exception: {e}")
        raise

def generate_reply_with_llm(subject: str, content: str, relevant_info: Dict[str, Any], openai_api_key: str) -> str:
    try:
        client = OpenAI(api_key=openai_api_key)
        prompt = f"""
You are a helpful property manager assistant. Here is an email from a tenant:

Subject: {subject}
Content: {content}

Relevant tenant info:
{relevant_info}

1. Extract the tenant's name, address, and apartment (if available).
2. Identify the main intent of the email (e.g., lockout, maintenance, rent, info request, callback).
3. Generate a plain-text, ready-to-send reply to the tenant.
4. Suggest an action item for the property manager as a JSON object.

Note: 
1. Please be aware that specific tenant information should only be given to the tenant themselves.
2. You may use the tenant's info as context to generate a solution.

Reply in this format:

Tenant: <name/address/apartment>
Intent: <intent>
Draft Reply: <reply>
Action Item: <json>
"""

        response = chat_completions_with_backoff(
            client,
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
        return reply
    except Exception as e:
        print(f"Error generating reply: {str(e)}")
        raise


def process_inbox_flow(email_client: EmailClient, openai_api_key: str, limit: int = 5) -> None:
    try:
        emails = email_client.get_emails(limit=limit)
        for email in emails:

            # Process email with LLM
            print(f"\nProcessing email from: {email['sender']}")
            tenant_info = get_tenant_info(email['sender'])
            if not tenant_info:
                print("No tenant data found for this email address.")
                continue
            print(f"Email content: {email.get('content')}")
            reply = generate_reply_with_llm(
                subject=email['subject'],
                content=email.get('content'),
                relevant_info=tenant_info,
                openai_api_key=openai_api_key
            )
            print("LLM Draft Reply and Action Item:\n", reply)

            # Extract and send email
            draft_reply = extract_draft_reply(reply)
            email_client.send_email(
                to_address=email['sender'],
                subject=f"Re: {email['subject']}",
                body=draft_reply
            )

            # Log the action
            action_item = extract_action_item(reply)
            process_action_item(action_item)
    except Exception as e:
        print(f"Error processing inbox: {str(e)}")
        raise