# test_model.py
import pandas as pd
import joblib

# Load model and encoders
model = joblib.load("model/habit_success_model/model.pkl")
ohe = joblib.load("model/habit_success_model/ohe_encoder.pkl")
target_encoder = joblib.load("model/habit_success_model/target_encoder.pkl")

# Sample input (you can replace this dynamically)
sample_input = {
    "age_group": "Adult",
    "gender": "Female",
    "personality_type": "Introvert",
    "habit_name": "Go for a run",
    "frequency_per_week": 5,
    "duration_minutes": 30,
    "motivation_level": "High",
    "past_consistency": "Medium"
}

# Prepare and encode input
input_df = pd.DataFrame([sample_input])
input_encoded = ohe.transform(input_df)

# Predict
pred = model.predict(input_encoded)[0]
label = target_encoder.inverse_transform([pred])[0]

print("🎯 Predicted Success Likelihood:", label)
