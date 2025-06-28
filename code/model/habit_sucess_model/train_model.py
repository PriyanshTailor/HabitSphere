# train_model.py
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("habit_success.csv").dropna()

# Separate features and target
X = df.drop(columns=["success_likelihood"])
y = df["success_likelihood"]

# One-hot encode features
ohe = OneHotEncoder(sparse=False, handle_unknown="ignore")
X_encoded = ohe.fit_transform(X)

# Encode target
target_encoder = LabelEncoder()
y_encoded = target_encoder.fit_transform(y)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y_encoded, test_size=0.2, stratify=y_encoded, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=500, max_depth=20, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print("✅ Accuracy:", round(acc * 100, 2), "%")
print(classification_report(y_test, y_pred, target_names=target_encoder.classes_))

# Save model and encoders
output_dir = "model/habit_success_model"
os.makedirs(output_dir, exist_ok=True)
joblib.dump(model, f"{output_dir}/model.pkl")
joblib.dump(ohe, f"{output_dir}/ohe_encoder.pkl")
joblib.dump(target_encoder, f"{output_dir}/target_encoder.pkl")
