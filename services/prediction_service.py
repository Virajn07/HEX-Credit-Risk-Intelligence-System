import pandas as pd
import joblib
import numpy as np

model = joblib.load("models/credit_model.pkl")
training_columns = joblib.load("models/training_columns.pkl")


def predict_risk(loan_data):

    df = pd.DataFrame([loan_data])

    # Map RM dataset fields to ML model fields
    df["loan_amnt"] = df["loan_amount"]
    df["annual_inc"] = df["annual_income"]
    df["installment"] = df["existing_emi"]
    df["revol_bal"] = df["credit_card_balance"]

    # Safe placeholders for LendingClub style features
    df["open_acc"] = 5
    df["total_acc"] = 15
    df["delinq_2yrs"] = df.get("missed_payments_last_12m", 0)

    # ========================
    # Feature Engineering
    # ========================

    df["loan_to_income_ratio"] = df["loan_amnt"] / (df["annual_inc"] + 1)

    df["monthly_income"] = df["annual_inc"] / 12

    df["emi_to_income_ratio"] = df["installment"] / (df["monthly_income"] + 1)

    # FIXED: better credit utilization signal
    df["credit_utilization_ratio"] = df["revol_bal"] / (df["annual_inc"] + 1)

    df["avg_credit_per_account"] = df["revol_bal"] / (df["open_acc"] + 1)

    df["delinq_ratio"] = df["delinq_2yrs"] / (df["total_acc"] + 1)

    df["log_income"] = np.log1p(df["annual_inc"])

    # ========================
    # Encode categorical
    # ========================
    df = pd.get_dummies(df)

    # Align columns with training
    df = df.reindex(columns=training_columns, fill_value=0)

    # ========================
    # Prediction
    # ========================
    probability = model.predict_proba(df)[0][1]

    # Slightly calibrated risk bands
    if probability > 0.18:
        risk = "High"
    elif probability > 0.08:
        risk = "Medium"
    else:
        risk = "Low"

    return probability, risk