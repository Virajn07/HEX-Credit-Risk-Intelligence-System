from services.llm_explainer import generate_loan_explanation


# TEST LOAN 1
loan1 = {
    "credit_score": 720,
    "annual_income": 1200000,
    "loan_amount": 232986,
    "existing_emi": 25000,
    "account_balance": 100000,
    "investment_value": 50000,
    "relationship_years": 6,
    "probability": 20
}

# TEST LOAN 2
loan2 = {
    "credit_score": 540,
    "annual_income": 450000,
    "loan_amount": 450000,
    "existing_emi": 32000,
    "account_balance": 5000,
    "investment_value": 0,
    "relationship_years": 1,
    "probability": 65
}

print("\n==============================")
print("TEST CASE 1 (Moderate Risk)")
print("==============================\n")

result1 = generate_loan_explanation(loan1)
print(result1)


print("\n==============================")
print("TEST CASE 2 (High Risk)")
print("==============================\n")

result2 = generate_loan_explanation(loan2)
print(result2)