from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
from dotenv import load_dotenv

from services.prediction_service import predict_risk
from services.llm_explainer import generate_loan_explanation
from services.counterfactual_engine import generate_counterfactuals
from services.customer_ai_review import generate_customer_review
from flask import Response
from services.llm_explainer import generate_portfolio_answer
load_dotenv()

app = Flask(__name__)

# ------------------------------------------------
# SAFE TYPE CONVERSION
# ------------------------------------------------

def to_float(x):
    try:
        return float(x)
    except:
        return 0.0


def to_int(x):
    try:
        return int(x)
    except:
        return 0


# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

df = pd.read_csv("data/loan_applications2.csv")

loans = []
customer_loans = {}

customer_app_counts = df["customer_id"].value_counts().to_dict()

# ------------------------------------------------
# BUILD LOAN OBJECTS
# ------------------------------------------------

for _, row in df.iterrows():

    loan = row.to_dict()

    probability, _ = predict_risk(loan)
    probability = to_float(probability) * 100

    income = to_float(loan.get("annual_income", 1))
    loan_amount = to_float(loan.get("loan_amount", 1))
    emi = to_float(loan.get("existing_emi", 0))

    credit_score = to_float(loan.get("credit_score", 650))
    relationship_years = to_float(loan.get("relationship_years", 0))

    loan["loan_income_ratio"] = round(loan_amount/(income+1),2)

    loan["emi_income_ratio"] = round(
        emi/((income/12)+1),2
    )

    loan["customer_total_apps"] = to_int(
        customer_app_counts.get(loan["customer_id"],1)
    )

    # POLICY ADJUSTMENTS

    if relationship_years > 5:
        probability *= 0.85

    if credit_score > 750:
        probability *= 0.7

    if credit_score < 550:
        probability *= 1.4

    probability = max(0,min(probability,95))

    loan["probability"] = round(probability,2)

    # PRIORITY SCORE

    credit_norm = credit_score/900

    priority_score = (
        0.35*credit_norm +
        0.25*(relationship_years/10) +
        0.20*(to_float(loan.get("investment_value",0))/200000) +
        0.10*(to_float(loan.get("account_balance",0))/200000) +
        0.10*((100-probability)/100)
    )

    loan["priority_score"] = round(priority_score,3)

    loan["status"] = "Pending"

    loans.append(loan)

    cid = loan["customer_id"]
    customer_loans.setdefault(cid,[]).append(loan)

# ------------------------------------------------
# SORT LOANS
# ------------------------------------------------

loans = sorted(loans,key=lambda x:x["probability"],reverse=True)

loan_lookup = {loan["loan_id"]:loan for loan in loans}

total_loans = len(loans)

# ------------------------------------------------
# RISK CLASSIFICATION
# ------------------------------------------------

high_cut = int(total_loans*0.15)
medium_cut = int(total_loans*0.40)

for i,loan in enumerate(loans):

    if i < high_cut:
        loan["risk"] = "High"

    elif i < medium_cut:
        loan["risk"] = "Medium"

    else:
        loan["risk"] = "Low"

# ------------------------------------------------
# DASHBOARD STATS
# ------------------------------------------------

def compute_dashboard_stats():

    high_risk = sum(1 for l in loans if l["risk"]=="High")
    medium_risk = sum(1 for l in loans if l["risk"]=="Medium")
    low_risk = sum(1 for l in loans if l["risk"]=="Low")

    approved = sum(1 for l in loans if l["status"]=="Approved")
    held = sum(1 for l in loans if l["status"]=="On Hold")
    rejected = sum(1 for l in loans if l["status"]=="Rejected")

    portfolio_health = int(
        (low_risk + (medium_risk*0.5)) /
        (total_loans+1) * 100
    )

    if portfolio_health > 75:
        portfolio_label = "EXCELLENT"
    elif portfolio_health > 55:
        portfolio_label = "STABLE"
    else:
        portfolio_label = "RISKY"

    return (
        high_risk,
        medium_risk,
        low_risk,
        approved,
        held,
        rejected,
        portfolio_health,
        portfolio_label
    )

# ------------------------------------------------
# EASY APPROVAL
# ------------------------------------------------

easy_loans = [l for l in loans if l["risk"]=="Low"][:5]

# ------------------------------------------------
# PRIORITY CUSTOMERS
# ------------------------------------------------

priority_customers = {}

for loan in loans:

    if loan["credit_score"] > 720 and loan["relationship_years"] > 5:

        cid = loan["customer_id"]
        priority_customers.setdefault(cid,loan)

priority_customers = list(priority_customers.values())[:5]

priority_ids = {c["customer_id"] for c in priority_customers}

priority_risky_loans = [
    l for l in loans
    if l["customer_id"] in priority_ids and l["risk"]=="High"
][:5]

# ------------------------------------------------
# CHART DATA
# ------------------------------------------------

cluster_data = []

for loan in loans:
    cluster_data.append({
        "x": to_float(loan["credit_score"]),
        "y": to_float(loan["loan_amount"])
    })

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------

@app.route("/")
def dashboard():

    (
        high_risk,
        medium_risk,
        low_risk,
        approved,
        held,
        rejected,
        portfolio_health,
        portfolio_label
    ) = compute_dashboard_stats()

    return render_template(
        "index.html",
        total_loans=total_loans,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        approved_loans=approved,
        held_loans=held,
        rejected_loans=rejected,
        portfolio_health=portfolio_health,
        portfolio_label=portfolio_label,
        priority_customers=priority_customers,
        easy_loans=easy_loans,
        priority_risky_loans=priority_risky_loans,
        cluster_data=cluster_data
    )

# ------------------------------------------------
# APPLICATIONS
# ------------------------------------------------

@app.route("/applications")
def applications():

    return render_template(
        "applications.html",
        loans=loans
    )

# ------------------------------------------------
# LOAN ACTIONS
# ------------------------------------------------

@app.route("/approve/<int:loan_id>")
def approve_loan(loan_id):

    loan = loan_lookup.get(loan_id)

    if loan:
        loan["status"] = "Approved"

    return redirect("/applications")


@app.route("/hold/<int:loan_id>")
def hold_loan(loan_id):

    loan = loan_lookup.get(loan_id)

    if loan:
        loan["status"] = "On Hold"

    return redirect("/applications")


@app.route("/reject/<int:loan_id>")
def reject_loan(loan_id):

    loan = loan_lookup.get(loan_id)

    if loan:
        loan["status"] = "Rejected"

    return redirect("/applications")

# ------------------------------------------------
# LOAN DETAIL
# ------------------------------------------------

@app.route("/loan/<int:loan_id>")
def loan_detail(loan_id):

    loan = loan_lookup.get(loan_id)

    if not loan:
        return "Loan not found"

    llm_explanation = generate_loan_explanation(loan)

    counterfactuals = generate_counterfactuals(loan)

    try:
        from services.shap_explainer import generate_shap_explanation
        shap_values = generate_shap_explanation(loan)
    except Exception as e:
        print("SHAP ERROR:", e)
        shap_values = []

    return render_template(
        "loan_detail.html",
        loan=loan,
        risk=loan["risk"],
        probability=loan["probability"],
        llm_explanation=llm_explanation,
        counterfactuals=counterfactuals,
        shap_values=shap_values
    )

# ------------------------------------------------
# CUSTOMERS
# ------------------------------------------------

@app.route("/customers")
def customers():

    customer_summary = {}

    for loan in loans:

        cid = loan["customer_id"]

        if cid not in customer_summary:

            customer_summary[cid] = {
                "customer_id": cid,
                "name": loan["customer_name"],
                "credit_score": loan["credit_score"],
                "relationship_years": loan["relationship_years"],
                "total_loans": 0,
                "total_exposure": 0
            }

        customer_summary[cid]["total_loans"] += 1
        customer_summary[cid]["total_exposure"] += loan["loan_amount"]

    customers = list(customer_summary.values())

    return render_template(
        "customers.html",
        customers=customers
    )

# ------------------------------------------------
# CUSTOMER PROFILE
# ------------------------------------------------

@app.route("/customer/<string:customer_id>")
def customer_profile(customer_id):

    loans_list = customer_loans.get(customer_id)

    if not loans_list:
        return "Customer not found"

    customer = loans_list[0]

    total_exposure = sum(l["loan_amount"] for l in loans_list)

    ai_customer_review = generate_customer_review(customer, loans_list)

    return render_template(
        "customer_profile.html",
        customer=customer,
        loans=loans_list,
        total_exposure=total_exposure,
        ai_customer_review=ai_customer_review
    )

# ------------------------------------------------
# AI CHATBOT
# ------------------------------------------------
@app.route("/ai_chat", methods=["POST"])
def ai_chat():

    try:

        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"answer": "Please ask a question."})

        (
            high_risk,
            medium_risk,
            low_risk,
            approved,
            held,
            rejected,
            portfolio_health,
            portfolio_label
        ) = compute_dashboard_stats()

        # Portfolio analytics
        avg_credit_score = sum(l["credit_score"] for l in loans) / len(loans)
        total_exposure = sum(l["loan_amount"] for l in loans)
        avg_loan_size = total_exposure / len(loans)

        # ------------------------------------------------
        # TOP RISKY LOANS
        # ------------------------------------------------

        risky_loans = sorted(
            loans,
            key=lambda x: x["probability"],
            reverse=True
        )[:5]

        risky_section = ""

        for loan in risky_loans:

            risky_section += f"""
Loan ID: {loan['loan_id']}
Customer: {loan['customer_name']}
Credit Score: {loan['credit_score']}
Loan Amount: ₹{loan['loan_amount']}
Default Probability: {loan['probability']}%
Risk Level: {loan['risk']}
"""

        # ------------------------------------------------
        # BEST CUSTOMERS
        # ------------------------------------------------

        best_customers = sorted(
            loans,
            key=lambda x: (x["credit_score"], x["relationship_years"]),
            reverse=True
        )[:5]

        best_section = ""

        for c in best_customers:

            best_section += f"""
Customer: {c['customer_name']}
Credit Score: {c['credit_score']}
Relationship Years: {c['relationship_years']}
Loan Amount: ₹{c['loan_amount']}
Risk Level: {c['risk']}
"""

        # ------------------------------------------------
        # CONTEXT
        # ------------------------------------------------

        portfolio_context = f"""
BANK CREDIT PORTFOLIO OVERVIEW

Total Loans: {total_loans}

Risk Distribution:
High Risk Loans: {high_risk}
Medium Risk Loans: {medium_risk}
Low Risk Loans: {low_risk}

Loan Decisions:
Approved Loans: {approved}
Loans On Hold: {held}
Rejected Loans: {rejected}

Portfolio Metrics:
Average Credit Score: {avg_credit_score:.0f}
Average Loan Size: ₹{avg_loan_size:,.0f}
Total Portfolio Exposure: ₹{total_exposure:,.0f}

Portfolio Health Score: {portfolio_health}
Portfolio Rating: {portfolio_label}

--------------------------------

TOP RISKY LOANS

{risky_section}

--------------------------------

BEST CUSTOMERS

{best_section}

--------------------------------

IMPORTANT RULES

• All currency must be in ₹ (Indian Rupees)
• Never use $
• Answer like a professional banking portfolio analyst
"""

        # Call AI chatbot
        answer = generate_portfolio_answer(question, portfolio_context)

        return jsonify({"answer": answer})

    except Exception as e:

        print("CHATBOT ERROR:", e)

        return jsonify({
            "answer": "AI assistant temporarily unavailable."
        })

@app.route("/loan_report/<int:loan_id>")
def loan_report(loan_id):

    loan = loan_lookup.get(loan_id)

    if not loan:
        return "Loan not found"

    report = f"""
HEX CREDIT SYSTEM
Loan Evaluation Report

Customer: {loan['customer_name']}
Loan ID: {loan['loan_id']}

Loan Amount: ₹{loan['loan_amount']}
Income: ₹{loan['annual_income']}
Credit Score: {loan['credit_score']}

Risk Level: {loan['risk']}
Default Probability: {loan['probability']}%

Status: {loan['status']}

AI Credit Analysis
------------------

{generate_loan_explanation(loan)}

Generated by HEX-Credit AI
"""

    return Response(
        report,
        mimetype="text/plain",
        headers={
            "Content-Disposition":
            f"attachment;filename=loan_report_{loan_id}.txt"
        }
    )
@app.route("/customer_report/<string:customer_id>")
def customer_report(customer_id):

    loans_list = customer_loans.get(customer_id)

    if not loans_list:
        return "Customer not found"

    customer = loans_list[0]

    total_exposure = sum(l["loan_amount"] for l in loans_list)

    report = f"""
HEX CREDIT SYSTEM
Customer Portfolio Report

Customer Name: {customer['customer_name']}
Customer ID: {customer_id}

Credit Score: {customer['credit_score']}
Relationship Years: {customer['relationship_years']}

Account Balance: ₹{customer['account_balance']}
Investment Value: ₹{customer['investment_value']}

Total Loans: {len(loans_list)}
Total Exposure: ₹{total_exposure}

Loan Details
------------

"""

    for loan in loans_list:

        report += f"""
Loan ID: {loan['loan_id']}
Loan Amount: ₹{loan['loan_amount']}
Risk: {loan['risk']}
Probability: {loan['probability']}%
Status: {loan['status']}
"""

    return Response(
        report,
        mimetype="text/plain",
        headers={
            "Content-Disposition":
            f"attachment;filename=customer_report_{customer_id}.txt"
        }
    )
# ------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)