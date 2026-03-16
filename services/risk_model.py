import joblib
import pandas as pd

model = joblib.load("models/credit_model.pkl")

def predict_risk(data):

    df = pd.DataFrame([data])

    prob = model.predict_proba(df)[0][1]

    if prob > 0.65:
        risk = "High"
    elif prob > 0.35:
        risk = "Medium"
    else:
        risk = "Low"

    return prob, risk