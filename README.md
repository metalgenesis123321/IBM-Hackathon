# IBM-Hackathon
A FastAPI backend (main.py) was built to connect securely with IBM Watsonx.ai, using environment variables stored in a .env file for the API key, endpoint, and project ID.
The parser processes meeting transcripts and extracts structured actions, decisions, and tasks in JSON format, validated against the meeting_action_schema.json.
This forms the core logic that allows the Autonomous Chief of Staff system to interpret meeting discussions and convert them into actionable workflow items ready for orchestration and automation.
This project uses environment variables to securely connect with IBM Watsonx.ai.
All sensitive credentials are stored in a .env file and should never be committed to GitHub.

1️⃣ Create a .env file

Inside your project root (or inside the backend/ folder), create a file named .env and add the following lines:

WATSONX_APIKEY=your_real_api_key_here
WATSONX_ENDPOINT=https://api.us-south.watsonx.ai
WATSONX_PROJECT_ID=your_real_project_id_here

2️⃣ Update main.py

In backend/main.py, replace any hard-coded project_id value with environment-based variables.
Your code should look like this:

from dotenv import load_dotenv
import os

load_dotenv()  # Loads values from .env file

api_key = os.getenv("WATSONX_APIKEY")
endpoint_url = os.getenv("WATSONX_ENDPOINT")
project_id = os.getenv("WATSONX_PROJECT_ID")


This ensures your Watsonx credentials and endpoint configuration are securely loaded at runtime rather than hard-coded in the source.

3️⃣ Add .env to .gitignore

To prevent accidental commits of sensitive information, make sure your .gitignore file includes:

.env

🧪 Running the Service

Install dependencies

pip install fastapi uvicorn requests python-dotenv jsonschema


Start the FastAPI server

uvicorn backend.main:app --reload --port 8000


Test the /parse endpoint

Open your browser at http://127.0.0.1:8000/docs

Use the sample request body:

{
  "meeting_id": "demo-001",
  "transcript": "[Meeting Title: Client Onboarding Sync]..."
}


You should receive structured JSON actions extracted from the transcript.

🧰 File Structure
project/
├─ backend/
│  ├─ main.py                    # FastAPI app
│  ├─ meeting_action_schema.json # Schema for validation
│  ├─ watsonx_client.py          # Watsonx.ai API integration
├─ openapi/
│  └─ nlp_parser_openapi.yaml    # API specification
└─ README.md

Example:
Schema
{
  "meeting_id": "demo-001",
  "transcript": "[Meeting Title: Client Onboarding Sync]\n[Date: Nov 21, 2025]\n[Participants: Alice (Project Manager), Bob (Developer), Carol (Client Success)]\n\n---\n\nAlice: Thanks everyone for joining. First, we need to send the signed contract to the client today. I’ll handle that—I'll email the final contract PDF to client@acme.com by end of day.\n\nBob: Great. I’ll open a Jira ticket for the onboarding dashboard issue we discussed last week. I’ll tag it under project ONB and assign it to myself for implementation by Monday.\n\nCarol: Perfect. Let’s set up a follow-up meeting next Wednesday at 10 a.m. to review the dashboard progress and confirm the client’s access setup.\n\nAlice: Awesome, that sounds good. Once I’ve sent the contract, I’ll add the confirmation to our shared drive.\n\n---\n\n[End of Meeting Transcript]"
}

Response
{
  "meeting_id": "Client Onboarding Sync",
  "source_text": "[Meeting Title: Client Onboarding Sync]\n[Date: Nov 21, 2025]\n[Participants: Alice (Project Manager), Bob (Developer), Carol (Client Success)]\n\n---\nAlice: Thanks everyone for joining. First, we need to send the signed contract to the client today. I’ll handle that—I'll email the final contract PDF to client@acme.com by end of day.\n\nBob: Great. I’ll open a Jira ticket for the onboarding dashboard issue we discussed last week. I’ll tag it under project ONB and assign it to myself for implementation by Monday.\n\nCarol: Perfect. Let’s set up a follow-up meeting next Wednesday at 10 a.m. to review the dashboard progress and confirm the client’s access setup.\n\nAlice: Awesome, that sounds good. Once I’ve sent the contract, I’ll add the confirmation to our shared drive.\n\n---\n[End of Meeting Transcript]",
  "generated_at": "2025-11-21T00:00:00",
  "actions": [
    {
      "id": "action-1",
      "text": "Send signed contract to client",
      "type": "action",
      "confidence": 0.9,
      "assignees": [
        {
          "name": "Alice",
          "email": "",
          "role": "Project Manager"
        }
      ],
      "due_date": "2025-11-21",
      "priority": "high",
      "source_span": {
        "start_char": 174,
        "end_char": 243,
        "speaker": "Alice"
      },
      "context": "Thanks everyone for joining. First, we need to send the signed contract to the client today.",
      "tags": [],
      "metadata": {}
    },
    {
      "id": "action-2",
      "text": "Open Jira ticket for onboarding dashboard issue",
      "type": "action",
      "confidence": 0.8,
      "assignees": [
        {
          "name": "Bob",
          "email": "",
          "role": "Developer"
        }
      ],
      "due_date": "2025-11-25",
      "priority": "medium",
      "source_span": {
        "start_char": 291,
        "end_char": 394,
        "speaker": "Bob"
      },
      "context": "Great. I’ll open a Jira ticket for the onboarding dashboard issue we discussed last week.",
      "tags": [],
      "metadata": {}
    },
    {
      "id": "action-3",
      "text": "Set up follow-up meeting",
      "type": "action",
      "confidence": 0.7,
      "assignees": [
        {
          "name": "Carol",
          "email": "",
          "role": "Client Success"
        }
      ],
      "due_date": "2025-11-27",
      "priority": "low",
      "source_span": {
        "start_char": 432,
        "end_char": 494,
        "speaker": "Carol"
      },
      "context": "Perfect. Let’s set up a follow-up meeting next Wednesday at 10 a.m.",
      "tags": [],
      "metadata": {}
    },
    {
      "id": "action-4",
      "text": "Add contract confirmation to shared drive",
      "type": "action",
      "confidence": 0.6,
      "assignees": [
        {
          "name": "Alice",
          "email": "",
          "role": "Project Manager"
        }
      ],
      "due_date": "2025-11-21",
      "priority": "low",
      "source_span": {
        "start_char": 522,
        "end_char": 559,
        "speaker": "Alice"
      },
      "context": "Awesome, that sounds good. Once I’ve sent the contract, I’ll add the confirmation to our shared drive.",
      "tags": [],
      "metadata": {}
    }
  ]
}
