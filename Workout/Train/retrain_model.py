
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Load dataset
df = pd.read_csv("synthetic_fitness_data_1000.csv")

# Feature engineering
df["Weight_Diff"] = df["Weight_kg"] - df["Goal_Weight_kg"]
df["Total_Equipment"] = (
    df["Has_No_Equipment"] +
    df["Has_Dumbbells"] +
    df["Has_Stationary_Bike"] +
    df["Has_Resistance_Band"] +
    df["Has_Yoga_Mat"]
)
df["Goal_Direction"] = df.apply(
    lambda row: "Lose" if row["Goal_Weight_kg"] < row["Weight_kg"]
    else "Gain" if row["Goal_Weight_kg"] > row["Weight_kg"]
    else "Maintain", axis=1)

# Encode categorical variables
le_gender = LabelEncoder()
le_goal = LabelEncoder()
le_direction = LabelEncoder()
df["Gender"] = le_gender.fit_transform(df["Gender"])
df["Fitness_Goal"] = le_goal.fit_transform(df["Fitness_Goal"])
df["Goal_Direction"] = le_direction.fit_transform(df["Goal_Direction"])

# One-hot encode Experience_Level
ohe_exp = OneHotEncoder(sparse_output=False)
exp_ohe = ohe_exp.fit_transform(df[["Experience_Level"]])
exp_ohe_df = pd.DataFrame(exp_ohe, columns=ohe_exp.get_feature_names_out(["Experience_Level"]))
df = pd.concat([df.reset_index(drop=True), exp_ohe_df], axis=1)

# Features for clustering
features = [
    "Gender", "Age", "Height_cm", "Weight_kg", "BMI", "Fitness_Goal",
    "Goal_Weight_kg", "Weight_Diff", "Total_Equipment", "Goal_Direction",
    "Has_No_Equipment", "Has_Dumbbells", "Has_Stationary_Bike",
    "Has_Resistance_Band", "Has_Yoga_Mat"
] + list(exp_ohe_df.columns)

X = df[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Apply PCA to retain 95% variance
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X_scaled)

# Try different cluster sizes
best_k = None
best_score = -1
best_model = None

for k in range(3, 8):
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X_pca)
    score = silhouette_score(X_pca, labels)
    print(f"k={k} → Silhouette Score: {score:.3f}")
    if score > best_score:
        best_k = k
        best_score = score
        best_model = kmeans

print(f"\n✅ Best k = {best_k} with Silhouette Score = {best_score:.3f}")

# Save model and encoders
joblib.dump(best_model, "kmeans_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(pca, "pca.pkl")
joblib.dump(le_gender, "label_encoder_gender.pkl")
joblib.dump(le_goal, "label_encoder_goal.pkl")
joblib.dump(le_direction, "label_encoder_direction.pkl")
joblib.dump(ohe_exp, "onehot_encoder_experience.pkl")
