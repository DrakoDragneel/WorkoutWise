import numpy as np
import joblib
import json


# Load models and encoders
kmeans = joblib.load("models/kmeans_model.pkl")
scaler = joblib.load("models/scaler.pkl")
pca = joblib.load("models/pca.pkl")
le_gender = joblib.load("models/label_encoder_gender.pkl")
le_goal = joblib.load("models/label_encoder_goal.pkl")
le_direction = joblib.load("models/label_encoder_direction.pkl")
ohe_experience = joblib.load("models/onehot_encoder_experience.pkl")

# Load workout plans
with open("models/weekly_workout_plans.json") as f:
    plans = json.load(f)


def recommend_workout(data):
    gender = le_gender.transform([data["gender"]])[0]
    goal = le_goal.transform([data["goal"]])[0]
    direction = le_direction.transform([data["direction"]])[0]
    experience_ohe = ohe_experience.transform([[data["experience"]]]).toarray().flatten()

    eq = {
        "Has_No_Equipment": int("No Equipment" in data["equipment"]),
        "Has_Dumbbells": int("Dumbbells" in data["equipment"]),
        "Has_Stationary_Bike": int("Stationary Bike" in data["equipment"]),
        "Has_Resistance_Band": int("Resistance Band" in data["equipment"]),
        "Has_Yoga_Mat": int("Yoga Mat" in data["equipment"]),
    }
    total_equipment = sum(eq.values())
    bmi = data["weight"] / ((data["height"] / 100) ** 2)
    weight_diff = data["weight"] - data["goal_weight"]

    features = np.array([
        [
            gender, data["age"], data["height"], data["weight"], bmi, goal,
            data["goal_weight"], weight_diff, total_equipment, direction,
            *experience_ohe,
            eq["Has_No_Equipment"], eq["Has_Dumbbells"], eq["Has_Stationary_Bike"],
            eq["Has_Resistance_Band"], eq["Has_Yoga_Mat"]
        ]
    ])

    scaled = scaler.transform(features)
    reduced = pca.transform(scaled)
    cluster = int(kmeans.predict(reduced)[0])
    plan = plans[str(cluster)]

    return {
        "plan_name": plan["name"],
        "goal": plan["goal"],
        "weekly_plan": plan["plan"]
    }
