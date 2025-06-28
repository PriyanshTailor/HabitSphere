import pandas as pd
import numpy as np

np.random.seed(42)
data_size = 5000

# Options for fields
age_groups = ["Teen", "Adult", "Senior"]
genders = ["Male", "Female", "Other"]
personality_types = ["Introvert", "Extrovert", "Ambivert"]
habit_names = [
    "Go for a run", "Read a book", "Meditate", "Practice guitar", "Write journal",
    "Do yoga", "Sketch something", "Cook a new recipe", "Walk the dog", "Study 1 hour"
]
motivation_levels = ["Low", "Medium", "High"]
past_consistency = ["Low", "Medium", "High"]

# Success logic
def simulate_success(row):
    score = 0
    if row['motivation_level'] == "High": score += 2
    if row['past_consistency'] == "High": score += 2
    if row['frequency_per_week'] >= 5: score += 1
    if row['duration_minutes'] >= 30: score += 1
    return "Very Likely" if score >= 5 else "Likely" if score >= 3 else "Unlikely"

# Generate data
df = pd.DataFrame({
    "age_group": np.random.choice(age_groups, data_size),
    "gender": np.random.choice(genders, data_size),
    "personality_type": np.random.choice(personality_types, data_size),
    "habit_name": np.random.choice(habit_names, data_size),
    "frequency_per_week": np.random.randint(1, 8, data_size),
    "duration_minutes": np.random.randint(5, 61, data_size),
    "motivation_level": np.random.choice(motivation_levels, data_size),
    "past_consistency": np.random.choice(past_consistency, data_size),
})

# Simulate label
df["success_likelihood"] = df.apply(simulate_success, axis=1)

# Save
df.to_csv("habit_success.csv", index=False)
print("✅ Dataset saved as 'habit_success.csv'")
