
import joblib
import json
import pandas as pd
from sklearn.metrics import silhouette_score, davies_bouldin_score

# Load models and encoders
kmeans = joblib.load("kmeans_model.pkl")
scaler = joblib.load("scaler.pkl")
pca = joblib.load("pca.pkl")
le_gender = joblib.load("label_encoder_gender.pkl")
le_goal = joblib.load("label_encoder_goal.pkl")
le_direction = joblib.load("label_encoder_direction.pkl")

# Load plans
with open("weekly_workout_plans.json") as f:
    plans = json.load(f)

# Sample user input
user = {
    "gender": "Male",
    "age": 30,
    "height": 175,
    "weight": 85,
    "goal": "Build Muscle",
    "goal_weight": 80,
    "equipment": ["Dumbbells", "Yoga Mat"]
}

# Preprocess
bmi = user["weight"] / ((user["height"] / 100) ** 2)
gender_encoded = le_gender.transform([user["gender"]])[0]
goal_encoded = le_goal.transform([user["goal"]])[0]
direction = "Lose" if user["goal_weight"] < user["weight"] else "Gain" if user["goal_weight"] > user["weight"] else "Maintain"
direction_encoded = le_direction.transform([direction])[0]

eq = {
    "Has_No_Equipment": int("No Equipment" in user["equipment"]),
    "Has_Dumbbells": int("Dumbbells" in user["equipment"]),
    "Has_Stationary_Bike": int("Stationary Bike" in user["equipment"]),
    "Has_Resistance_Band": int("Resistance Band" in user["equipment"]),
    "Has_Yoga_Mat": int("Yoga Mat" in user["equipment"])
}
weight_diff = user["weight"] - user["goal_weight"]
total_equipment = sum(eq.values())

features = [[
    gender_encoded, user["age"], user["height"], user["weight"], bmi,
    goal_encoded, user["goal_weight"], weight_diff, total_equipment,
    direction_encoded,
    eq["Has_No_Equipment"], eq["Has_Dumbbells"], eq["Has_Stationary_Bike"],
    eq["Has_Resistance_Band"], eq["Has_Yoga_Mat"]
]]

scaled = scaler.transform(features)
pca_features = pca.transform(scaled)
cluster = int(kmeans.predict(pca_features)[0])
plan = plans[str(cluster)]

print(f"✅ Predicted Cluster: {cluster}")
print(f"Plan Name: {plan['name']}")
print(f"Goal: {plan['goal']}")
print("\nWeekly Plan:")
for day, exercises in plan["plan"].items():
    print(f"{day}:")
    for ex in exercises:
        if isinstance(ex, dict):
            print(f"  - {ex['name']} ({ex['type']}, {ex['difficulty']}): {ex['reps']}")
        else:
            print(f"  - {ex}")

# Evaluate on full dataset
print("\n--- Model Evaluation ---")
df = pd.read_csv("synthetic_fitness_data_1000.csv")
df["Goal_Direction"] = df.apply(lambda row: "Lose" if row["Goal_Weight_kg"] < row["Weight_kg"] else "Gain" if row["Goal_Weight_kg"] > row["Weight_kg"] else "Maintain", axis=1)
df["Weight_Diff"] = df["Weight_kg"] - df["Goal_Weight_kg"]
df["Total_Equipment"] = df[["Has_No_Equipment", "Has_Dumbbells", "Has_Stationary_Bike", "Has_Resistance_Band", "Has_Yoga_Mat"]].sum(axis=1)
df["Gender"] = le_gender.transform(df["Gender"])
df["Fitness_Goal"] = le_goal.transform(df["Fitness_Goal"])
df["Goal_Direction"] = le_direction.transform(df["Goal_Direction"])

X = df[[
    "Gender", "Age", "Height_cm", "Weight_kg", "BMI", "Fitness_Goal",
    "Goal_Weight_kg", "Weight_Diff", "Total_Equipment", "Goal_Direction",
    "Has_No_Equipment", "Has_Dumbbells", "Has_Stationary_Bike",
    "Has_Resistance_Band", "Has_Yoga_Mat"
]]
X_scaled = scaler.transform(X)
X_pca = pca.transform(X_scaled)
labels = kmeans.predict(X_pca)

sil_score = silhouette_score(X_pca, labels)
db_score = davies_bouldin_score(X_pca, labels)
print(f"Silhouette Score: {sil_score:.3f} (higher is better)")
print(f"Davies-Bouldin Index: {db_score:.3f} (lower is better)")
