from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, os, json, time
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
load_dotenv()  # loads .env file automatically


_cached_token = {"value": None, "expiry": 0}


def get_cached_iam_token(api_key):
    now = time.time()
    if _cached_token["value"] and now < _cached_token["expiry"]:
        return _cached_token["value"]


    url = "https://iam.cloud.ibm.com/identity/token"
    resp = requests.post(
        url,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()


    token = resp.json()["access_token"]
    _cached_token["value"] = token
    _cached_token["expiry"] = now + 55 * 60  # cache for 55 minutes
    return token


# Load your schema (use uploaded path)
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "meeting_action_schema.json")


with open(SCHEMA_PATH) as f:
    SCHEMA = json.load(f)


app = FastAPI()


class ParseRequest(BaseModel):
    meeting_id: str
    transcript: str
    source_text: str = None


# helper: call watsonx.ai prompt endpoint (replace with your endpoint/project)
def call_watsonx(prompt, iam_token, endpoint_url, project_id):
    # Correct watsonx.ai text-chat endpoint from Prompt Lab
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"


    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}"
    }


    body = {
        "messages": [
            {
                "role": "system",
                "content": "You extract meeting actions as JSON. Respond only with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        # 👇 Use your actual project ID from watsonx.ai Prompt Lab
        "project_id": "a17cc766-44a8-40b9-ab15-a6762c3b8c4e",
        # 👇 You can use the same model you saw in Prompt Lab
        "model_id": "meta-llama/llama-3-3-70b-instruct",
        "max_tokens": 2000,
        "temperature": 0.2,
        "top_p": 1
    }


    # Send request
    r = requests.post(url, headers=headers, json=body)
    print("WATSONX URL:", url)
    print("STATUS:", r.status_code)
    print("BODY:", r.text)


    r.raise_for_status()
    return r.json()




@app.post("/parse")
async def parse(req: ParseRequest):
    # Basic sanity
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Empty transcript")


    # Build prompt (concise)
    prompt = f"""
You are a parser that extracts meeting actions as JSON array `actions` following this schema:
{json.dumps(SCHEMA['properties']['actions'], indent=2)}


Return ONLY the JSON object with keys: meeting_id, source_text, generated_at, actions
Transcript:
\"\"\"{req.transcript}\"\"\"
"""


    # get tokens from env (set in .env or env)
    api_key = os.getenv("WATSONX_APIKEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="WATSONX_APIKEY not set in env")
    endpoint_url = os.getenv("WATSONX_ENDPOINT")
    project_id = os.getenv("WATSONX_PROJECT_ID")


    iam = get_cached_iam_token(api_key)
    model_resp = call_watsonx(prompt, iam, endpoint_url, project_id)


    # --- begin: extract assistant message text from the chat response ---
    try:
        assistant_text = model_resp["choices"][0]["message"]["content"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected model response structure")


    # remove ``` fences if present and any surrounding whitespace
    import re
    assistant_text = assistant_text.strip()
    assistant_text = re.sub(r"^```(?:[\s\S]*?\n)?", "", assistant_text)  # remove opening ``` and optional language
    assistant_text = re.sub(r"```$", "", assistant_text).strip()        # remove trailing ```


    # now parse JSON from assistant_text
    try:
        parsed = json.loads(assistant_text)
    except Exception:
        # fallback: extract first {...} block
        m = re.search(r'(\{[\s\S]*\})', assistant_text)
        if m:
            parsed = json.loads(m.group(1))
        else:
            raise HTTPException(status_code=500, detail="Model output not valid JSON")
    # --- end extraction ---


    # Add top-level fields if missing
    parsed.setdefault("meeting_id", req.meeting_id)
    parsed.setdefault("source_text", req.source_text or req.transcript)
    parsed.setdefault("generated_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


    # Validate using your schema
    try:
        validate(instance=parsed, schema=SCHEMA)
    except ValidationError as e:
        # show the specific validation message to help debug
        raise HTTPException(status_code=500, detail=f"Validation error: {e.message}")


    return parsed


