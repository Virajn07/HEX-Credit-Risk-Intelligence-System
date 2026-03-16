def generate_counterfactuals(loan):

    suggestions = []

    risk = loan.get("risk","Low")

    # Do NOT generate restructuring for low risk loans
    if risk == "Low":
        return []

    loan_amount = loan.get("loan_amount",0)
    income = loan.get("annual_income",1)
    emi = loan.get("existing_emi",0)
    credit_score = loan.get("credit_score",650)
    relationship_years = loan.get("relationship_years",0)
    investment_value = loan.get("investment_value",0)

    monthly_income = income / 12

    # Safe EMI rule (bank standard)
    safe_emi_limit = monthly_income * 0.35

    emi_capacity = max(0, safe_emi_limit - emi)

    # tenure logic
    tenure = 36

    if relationship_years > 8:
        tenure = 48

    if relationship_years > 12:
        tenure = 60

    # Revised loan calculation
    if emi_capacity > 0:
        revised_loan = int(emi_capacity * tenure)
    else:
        revised_loan = int(loan_amount * 0.75)

    # Always reduce exposure
    revised_loan = min(revised_loan, int(loan_amount * 0.85))

    estimated_emi = int(revised_loan / tenure)

    suggestions.append(
        f"Recommended revised loan amount: ₹{revised_loan:,} instead of ₹{loan_amount:,}."
    )

    suggestions.append(
        f"Suggested repayment tenure: {tenure} months."
    )

    suggestions.append(
        f"Estimated EMI: ₹{estimated_emi:,} per month."
    )

    emi_ratio = int((estimated_emi/monthly_income)*100)

    suggestions.append(
        f"Revised EMI represents approximately {emi_ratio}% of monthly income, aligning with standard banking affordability thresholds."
    )

    if relationship_years > 5:
        suggestions.append(
            f"Customer maintains a strong {relationship_years}-year relationship with the bank, improving credit confidence."
        )

    if investment_value > 150000:
        suggestions.append(
            "Investment holdings with the bank strengthen financial stability and repayment capacity."
        )

    if credit_score < 700:
        suggestions.append(
            "Moderate credit score suggests slightly conservative loan structuring."
        )

    suggestions.append(
        "Restructuring the loan improves repayment affordability and reduces default risk exposure."
    )

    return suggestions