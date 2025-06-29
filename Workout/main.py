
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import json

# Load components
kmeans = joblib.load("kmeans_model.pkl")
scaler = joblib.load("scaler.pkl")
pca = joblib.load("pca.pkl")
le_gender = joblib.load("label_encoder_gender.pkl")
le_goal = joblib.load("label_encoder_goal.pkl")
le_direction = joblib.load("label_encoder_direction.pkl")
le_exp = joblib.load("label_encoder_experience.pkl")

with open("weekly_workout_plans_enhanced.json") as f:
    plans = json.load(f)

app = FastAPI()

class UserProfile(BaseModel):
    gender: str
    age: int
    height: float
    weight: float
    goal: str
    goal_weight: float
    experience: str
    equipment: list[str]

@app.post("/recommend")
def recommend(user: UserProfile):
    bmi = user.weight / ((user.height / 100) ** 2)
    weight_diff = user.weight - user.goal_weight
    direction = "Lose" if weight_diff > 0 else "Gain" if weight_diff < 0 else "Maintain"
    gender_encoded = le_gender.transform([user.gender])[0]
    goal_encoded = le_goal.transform([user.goal])[0]
    direction_encoded = le_direction.transform([direction])[0]
    exp_encoded = le_exp.transform([user.experience])[0]

    eq = {
        "Has_No_Equipment": int("No Equipment" in user.equipment),
        "Has_Dumbbells": int("Dumbbells" in user.equipment),
        "Has_Stationary_Bike": int("Stationary Bike" in user.equipment),
        "Has_Resistance_Band": int("Resistance Band" in user.equipment),
        "Has_Yoga_Mat": int("Yoga Mat" in user.equipment)
    }
    total_eq = sum(eq.values())

    features = [[
        gender_encoded, user.age, user.height, user.weight, bmi, goal_encoded,
        user.goal_weight, weight_diff, total_eq, direction_encoded, exp_encoded,
        eq["Has_No_Equipment"], eq["Has_Dumbbells"], eq["Has_Stationary_Bike"],
        eq["Has_Resistance_Band"], eq["Has_Yoga_Mat"]
    ]]

    scaled = scaler.transform(features)
    reduced = pca.transform(scaled)
    cluster = int(kmeans.predict(reduced)[0])
    plan = plans[str(cluster)]

    return {
        "cluster": cluster,
        "plan_name": plan["name"],
        "goal": plan["goal"],
        "weekly_plan": plan["plan"]
    }
