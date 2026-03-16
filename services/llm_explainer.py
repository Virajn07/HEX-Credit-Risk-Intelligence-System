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


# ------------------------------------------------
# CLEAN RESPONSE
# ------------------------------------------------

def clean_response(text):

    if not text:
        return "AI response unavailable."

    text = text.replace("$","₹")
    text = text.replace("**","")

    return text.strip()


# ------------------------------------------------
# LOAN ANALYSIS PROMPT
# ------------------------------------------------

def build_loan_prompt(loan):

    return f"""
You are a senior banking credit risk analyst.

You assist relationship managers in evaluating loan applications.

IMPORTANT RULES:
- Always use ₹ (Indian Rupees), NEVER use $.
- Be concise and professional.
- Think like a bank credit committee member.

Loan Details:

Credit Score: {loan.get("credit_score")}
Annual Income: ₹{loan.get("annual_income")}
Loan Amount: ₹{loan.get("loan_amount")}
Existing EMI: ₹{loan.get("existing_emi")}
Account Balance: ₹{loan.get("account_balance")}
Investment Value: ₹{loan.get("investment_value")}
Relationship Years: {loan.get("relationship_years")}
Predicted Default Probability: {loan.get("probability")}%

Return output EXACTLY in this format:

Risk Summary:
(one sentence)

Key Strengths:
• point
• point
• point

Risk Drivers:
• point
• point
• point

Final Recommendation:
(one sentence)
"""


# ------------------------------------------------
# CHATBOT PROMPT
# ------------------------------------------------

def build_chat_prompt(question, portfolio_context):

    return f"""
You are an AI assistant for relationship managers working at a commercial bank.

Your job is to answer questions about:

• loan portfolio risk
• customer quality
• lending strategy
• credit policy
• financial risk analysis

Rules:

- Always answer as a banking professional
- Always use ₹ for currency
- Never use $
- Be analytical and structured
- If question is general, still answer in banking context

Portfolio Context:

{portfolio_context}

Relationship Manager Question:

{question}

Provide structured answer in this format:

Answer:
(concise explanation)

Key Insights:
• insight
• insight
• insight

Recommendation:
(actionable advice)
"""


# ------------------------------------------------
# LLM CALL
# ------------------------------------------------

def call_model(prompt, model, key):

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "HEX Credit System"
    }

    payload = {
        "model": model,
        "messages": [
            {"role":"system","content":"You are a professional banking analyst."},
            {"role":"user","content":prompt}
        ],
        "temperature":0.3,
        "reasoning":{"enabled":True}
    }

    response = requests.post(API_URL,headers=headers,json=payload,timeout=25)

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    return clean_response(data["choices"][0]["message"]["content"])


# ------------------------------------------------
# LOAN ANALYSIS FUNCTION
# ------------------------------------------------

def generate_loan_explanation(loan):

    prompt = build_loan_prompt(loan)

    for key in API_KEYS:

        try:
            return call_model(prompt, PRIMARY_MODEL, key)

        except Exception as e:

            print("Primary model failed:", e)

            try:
                return call_model(prompt, BACKUP_MODEL, key)

            except Exception as e:
                print("Backup model failed:", e)

    return "AI explanation could not be generated."


# ------------------------------------------------
# PORTFOLIO CHATBOT
# ------------------------------------------------

def generate_portfolio_answer(question, portfolio_context):

    prompt = build_chat_prompt(question, portfolio_context)

    for key in API_KEYS:

        try:
            return call_model(prompt, PRIMARY_MODEL, key)

        except Exception as e:

            print("Primary chatbot model failed:", e)

            try:
                return call_model(prompt, BACKUP_MODEL, key)

            except Exception as e:
                print("Backup chatbot model failed:", e)

    return "AI assistant unavailable."
def generate_portfolio_answer(question, context):

    prompt = f"""
You are an AI banking portfolio assistant helping a Relationship Manager (RM).

You analyze the bank's loan portfolio and answer RM questions clearly.

Rules:
• Always use Indian Rupees (₹)
• Never use $
• Answer in structured professional language
• Use portfolio data when relevant
• Do NOT return loan risk template format

Portfolio Context:

{context}

RM Question:
{question}

Provide a clear analytical answer.
"""

    for key in API_KEYS:

        try:
            return call_model(prompt, PRIMARY_MODEL, key)

        except Exception as e:

            print("Primary model failed:", e)

            try:
                return call_model(prompt, BACKUP_MODEL, key)

            except Exception as e:

                print("Backup model failed:", e)

    return "AI assistant could not generate an answer."