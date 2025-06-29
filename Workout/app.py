
import streamlit as st
import joblib
import json

# Load model and tools
kmeans = joblib.load("kmeans_model.pkl")
scaler = joblib.load("scaler.pkl")
pca = joblib.load("pca.pkl")
le_gender = joblib.load("label_encoder_gender.pkl")
le_goal = joblib.load("label_encoder_goal.pkl")
le_direction = joblib.load("label_encoder_direction.pkl")

# Load workout plans
with open("weekly_workout_plans.json") as f:
    plans = json.load(f)

st.title("🏋️‍♂️ Workout Recommendation App (Enhanced Model)")

with st.form("user_input_form"):
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.slider("Age", 16, 60, 30)
    height = st.slider("Height (cm)", 140, 210, 175)
    weight = st.slider("Weight (kg)", 40, 150, 75)
    goal = st.selectbox("Fitness Goal", ["Lose Weight", "Build Muscle", "Get Fit"])
    goal_weight = st.slider("Goal Weight (kg)", 40, 150, 70)
    equipment = st.multiselect(
        "Available Equipment",
        ["No Equipment", "Dumbbells", "Stationary Bike", "Resistance Band", "Yoga Mat"]
    )
    submitted = st.form_submit_button("Get Recommendation")

if submitted:
    # Derived values
    bmi = weight / ((height / 100) ** 2)
    weight_diff = weight - goal_weight
    direction = "Lose" if goal_weight < weight else "Gain" if goal_weight > weight else "Maintain"
    direction_encoded = le_direction.transform([direction])[0]
    gender_encoded = le_gender.transform([gender])[0]
    goal_encoded = le_goal.transform([goal])[0]
    eq = {
        "Has_No_Equipment": int("No Equipment" in equipment),
        "Has_Dumbbells": int("Dumbbells" in equipment),
        "Has_Stationary_Bike": int("Stationary Bike" in equipment),
        "Has_Resistance_Band": int("Resistance Band" in equipment),
        "Has_Yoga_Mat": int("Yoga Mat" in equipment)
    }
    total_equipment = sum(eq.values())

    features = [[
        gender_encoded, age, height, weight, bmi, goal_encoded,
        goal_weight, weight_diff, total_equipment, direction_encoded,
        eq["Has_No_Equipment"], eq["Has_Dumbbells"], eq["Has_Stationary_Bike"],
        eq["Has_Resistance_Band"], eq["Has_Yoga_Mat"]
    ]]

    X_scaled = scaler.transform(features)
    X_pca = pca.transform(X_scaled)
    cluster = int(kmeans.predict(X_pca)[0])
    plan = plans[str(cluster)]

    st.success(f"✅ You are matched with: {plan['name']}")
    st.caption(plan['goal'])

    st.subheader("🗓️ Weekly Plan")
    for day, exercises in plan["plan"].items():
        st.markdown(f"**{day}**")
        for ex in exercises:
            if isinstance(ex, dict):
                st.markdown(f"- {ex['name']} ({ex['type']}, {ex['difficulty']}): {ex['reps']}")
            else:
                st.markdown(f"- {ex}")
