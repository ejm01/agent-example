## Overview
This project is an AI-powered email assistant for property managers. It:
- Connects to a Gmail inbox
- Triages unread messages
- Generates draft replies using an LLM (OpenAI GPT-4.1)
- Triggers relevant workflows (such as creating action items)

## Features
- **Connects to a Gmail inbox** using IMAP (via `imaplib`)
- **Fetches unread or recent messages**
- **Loads relevant tenant information** (mocked for demo purposes)
- **Generates draft replies** using OpenAI's GPT-4.1 LLM
- **Extracts and processes action items** (e.g., maintenance requests) as JSON
- **Sends email replies** to tenants

## Setup & Run Instructions
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install openai python-dotenv backoff
   ```
3. **Set up your `.env` file** with the following variables:
   ```env
   EMAIL_ADDRESS=your_gmail_address@gmail.com
   EMAIL_PASSWORD=your_gmail_password_or_app_password
   IMAP_SERVER=imap.gmail.com
   OPENAI_API_KEY=your_openai_api_key
   ```
   > **Note:** For Gmail, you may need to use an [App Password](https://support.google.com/accounts/answer/185833) if 2FA is enabled.
4. **Run the app**:
   ```bash
   python main.py
   ```

## Project Structure
- `main.py` — Entry point, runs the end-to-end cycle
- `email_client.py` — Handles IMAP connection, email fetching, and sending
- `email_handling.py` — Loads tenant info, generates LLM replies, processes workflows
- `post_processing.py` — Extracts draft replies and action items from LLM output


## Things to do in the future
- Use actual objects to represent tenants, actions, etc.
- Add persistence
- The classics: add error handling, logging, etc.
- Support HTML email parsing and attachments
- Integrate with a workflow system to create action items

## Assumptions
- All relevant tenant data is available or can be mocked
- The LLM can generate useful replies and action items from the email content
- The app is run with access to the relevant inbox

## AI Notes
- **LLM Used:** OpenAI GPT-4.1 via the `openai` Python SDK
- **Prompting:** The LLM is prompted to extract intent, generate a draft reply, and suggest an action item in JSON
- **Post-processing:** Regex is used to extract the draft reply and action item from the LLM output
- **Development:** I used cusor.

---
