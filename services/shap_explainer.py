import pandas as pd
import numpy as np
import shap
import joblib


# -----------------------------------------
# LOAD MODEL + TRAINING FEATURES
# -----------------------------------------

model = joblib.load("models/credit_model.pkl")
training_columns = joblib.load("models/training_columns.pkl")

explainer = shap.TreeExplainer(model)


# -----------------------------------------
# SHAP EXPLANATION FUNCTION
# -----------------------------------------

def generate_shap_explanation(loan):

    try:

        # Convert loan dictionary → dataframe
        df = pd.DataFrame([loan])

        # -----------------------------------------
        # MAP DATASET FIELDS → MODEL FEATURES
        # -----------------------------------------

        df["loan_amnt"] = df.get("loan_amount", 0)
        df["annual_inc"] = df.get("annual_income", 0)
        df["installment"] = df.get("existing_emi", 0)
        df["revol_bal"] = df.get("credit_card_balance", 0)

        # Default placeholders for missing training fields

        df["open_acc"] = 5
        df["total_acc"] = 15
        df["delinq_2yrs"] = 0

        # -----------------------------------------
        # FEATURE ENGINEERING
        # -----------------------------------------

        df["loan_to_income_ratio"] = df["loan_amnt"] / (df["annual_inc"] + 1)

        df["monthly_income"] = df["annual_inc"] / 12

        df["emi_to_income_ratio"] = df["installment"] / (df["monthly_income"] + 1)

        df["credit_utilization_ratio"] = df["revol_bal"] / (df["annual_inc"] + 1)

        df["log_income"] = np.log1p(df["annual_inc"])

        # -----------------------------------------
        # ENCODING
        # -----------------------------------------

        df = pd.get_dummies(df)

        # Align with training columns
        df = df.reindex(columns=training_columns, fill_value=0)

        # -----------------------------------------
        # COMPUTE SHAP VALUES
        # -----------------------------------------

        shap_values = explainer.shap_values(df)

        # For binary classification models
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap_values = shap_values[0]

        # Pair feature + importance
        shap_pairs = list(zip(training_columns, shap_values))

        # Sort by absolute importance
        shap_pairs = sorted(
            shap_pairs,
            key=lambda x: abs(x[1]),
            reverse=True
        )

        # -----------------------------------------
        # RETURN TOP FEATURES
        # -----------------------------------------

        results = []

        for feature, value in shap_pairs[:5]:

            results.append({
                "feature": feature.replace("_", " ").title(),
                "impact": float(value)
            })

        return results

    except Exception as e:

        # If SHAP fails, return empty list
        print("SHAP ERROR:", e)

        return []