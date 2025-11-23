# IBM-Hackathon

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
