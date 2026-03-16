import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"

PRIMARY_MODEL = "arcee-ai/trinity-large-preview:free"
BACKUP_MODEL = "openrouter/hunter-alpha"

API_KEYS = [
    os.getenv("OPENROUTER_KEY_1"),
    os.getenv("OPENROUTER_KEY_2")
]

API_KEYS = [k for k in API_KEYS if k]


def build_prompt(customer, loans):

    total_loans = len(loans)
    total_exposure = sum(l["loan_amount"] for l in loans)

    loan_summary = ""

    for loan in loans:

        loan_summary += f"""
Loan ID: {loan['loan_id']}
Loan Amount: ₹{loan['loan_amount']}
Risk: {loan['risk']}
Default Probability: {loan['probability']}%
Status: {loan['status']}
"""

    return f"""
You are a senior relationship manager at a bank.

Evaluate the customer's overall financial relationship with the bank.

Rules:
- Always use ₹
- Never use $
- Think like a portfolio manager
- Focus on risk, relationship quality and exposure

Customer Profile:

Customer Name: {customer['customer_name']}
Credit Score: {customer['credit_score']}
Relationship Years: {customer['relationship_years']}

Total Loans: {total_loans}
Total Exposure: ₹{total_exposure}

Loan Portfolio:

{loan_summary}

Return output EXACTLY in this format:

Customer Risk Profile:
(one sentence summary)

Positive Indicators:
• point
• point
• point

Potential Concerns:
• point
• point
• point

Relationship Recommendation:
(one clear sentence)
"""


def call_model(prompt, model, key):

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role":"system","content":"You are a banking portfolio analyst."},
            {"role":"user","content":prompt}
        ],
        "temperature":0.3,
        "reasoning":{"enabled":True}
    }

    response = requests.post(API_URL,headers=headers,json=payload,timeout=25)

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    text = data["choices"][0]["message"]["content"]

    return text.replace("$","₹").replace("**","")


def generate_customer_review(customer, loans):

    prompt = build_prompt(customer, loans)

    for key in API_KEYS:

        try:
            return call_model(prompt, PRIMARY_MODEL, key)

        except:
            try:
                return call_model(prompt, BACKUP_MODEL, key)
            except:
                continue

    return "AI customer analysis unavailable."