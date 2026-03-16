import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

KEY1 = os.getenv("OPENROUTER_KEY_1")
KEY2 = os.getenv("OPENROUTER_KEY_2")

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def test_model(api_key, model):

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "HEX Credit Test"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Explain credit risk in one short paragraph."
            }
        ],
        "reasoning": {"enabled": True}
    }

    response = requests.post(
        API_URL,
        headers=headers,
        data=json.dumps(payload)
    )

    print("\n==============================")
    print("MODEL:", model)
    print("STATUS:", response.status_code)

    try:
        data = response.json()
        print("RESPONSE:\n", data["choices"][0]["message"]["content"])
    except:
        print("RAW RESPONSE:\n", response.text)


# ------------------------------------------------
# RUN TESTS
# ------------------------------------------------

print("\nTesting Trinity Model")

test_model(
    KEY1,
    "arcee-ai/trinity-large-preview:free"
)

print("\nTesting GPT OSS Model")

test_model(
    KEY2,
    "openai/gpt-oss-120b:free"
)