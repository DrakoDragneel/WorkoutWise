from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import shutil
import uuid
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import pickle
import math
import collections
import os

app = FastAPI()

# Load trained model
with open("model/LR_model.pkl", "rb") as f:
    count_model = pickle.load(f)

# Keypoints to track
IMPORTANT_LMS = [
    "NOSE", "LEFT_SHOULDER", "RIGHT_SHOULDER",
    "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE",
    "LEFT_ANKLE", "RIGHT_ANKLE"
]

headers = ["label"]
for lm in IMPORTANT_LMS:
    headers += [f"{lm.lower()}_x", f"{lm.lower()}_y", f"{lm.lower()}_z", f"{lm.lower()}_v"]

# Helper functions
mp_pose = mp.solutions.pose

def extract_important_keypoints(results) -> list:
    landmarks = results.pose_landmarks.landmark
    data = []
    for lm in IMPORTANT_LMS:
        keypoint = landmarks[mp_pose.PoseLandmark[lm].value]
        data.append([keypoint.x, keypoint.y, keypoint.z, keypoint.visibility])
    return np.array(data).flatten().tolist()

def calculate_distance(pointX, pointY) -> float:
    x1, y1 = pointX
    x2, y2 = pointY
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def analyze_foot_knee_placement(results, stage: str, foot_shoulder_ratio_thresholds, knee_foot_ratio_thresholds, visibility_threshold):
    analyzed_results = {"foot_placement": -1, "knee_placement": -1}
    landmarks = results.pose_landmarks.landmark

    if any([
        landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].visibility < visibility_threshold,
        landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].visibility < visibility_threshold,
        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility < visibility_threshold,
        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility < visibility_threshold,
    ]):
        return analyzed_results

    shoulder_width = calculate_distance(
        [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    )

    foot_width = calculate_distance(
        [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y]
    )

    foot_shoulder_ratio = round(foot_width / shoulder_width, 1)
    min_r, max_r = foot_shoulder_ratio_thresholds
    analyzed_results["foot_placement"] = (
        0 if min_r <= foot_shoulder_ratio <= max_r else 1 if foot_shoulder_ratio < min_r else 2
    )

    knee_width = calculate_distance(
        [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
    )

    knee_foot_ratio = round(knee_width / foot_width, 1)
    stage_min, stage_max = knee_foot_ratio_thresholds.get(stage, (0, 100))
    if stage_min <= knee_foot_ratio <= stage_max:
        analyzed_results["knee_placement"] = 0
    elif knee_foot_ratio < stage_min:
        analyzed_results["knee_placement"] = 1
    else:
        analyzed_results["knee_placement"] = 2

    return analyzed_results

@app.get("/")
def root():
    return {"message": "Squat Form API is running"}

# To be expanded: endpoint for real-time video or analysis
@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    # Save the uploaded video to a temporary file
    temp_filename = f"temp_{uuid.uuid4().hex}.mp4"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load the video
    cap = cv2.VideoCapture(temp_filename)

    # Initialize
    counter = 0
    current_stage = ""
    PREDICTION_PROB_THRESHOLD = 0.7
    VISIBILITY_THRESHOLD = 0.6
    FOOT_SHOULDER_RATIO_THRESHOLDS = [1.2, 2.8]
    KNEE_FOOT_RATIO_THRESHOLDS = {
        "up": [0.5, 1.0],
        "middle": [0.7, 1.0],
        "down": [0.7, 1.1],
    }

    foot_buffer = collections.deque(maxlen=5)
    knee_buffer = collections.deque(maxlen=5)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                try:
                    row = extract_important_keypoints(results)
                    X = pd.DataFrame([row], columns=headers[1:])
                    predicted_class = count_model.predict(X)[0]
                    predicted_class = "down" if predicted_class == 0 else "up"
                    pred_prob = round(count_model.predict_proba(X)[0].max(), 2)

                    if predicted_class == "down" and pred_prob >= PREDICTION_PROB_THRESHOLD:
                        current_stage = "down"
                    elif current_stage == "down" and predicted_class == "up" and pred_prob >= PREDICTION_PROB_THRESHOLD:
                        current_stage = "up"
                        counter += 1

                    analyzed = analyze_foot_knee_placement(
                        results, current_stage,
                        FOOT_SHOULDER_RATIO_THRESHOLDS,
                        KNEE_FOOT_RATIO_THRESHOLDS,
                        VISIBILITY_THRESHOLD
                    )
                    foot_buffer.append(analyzed["foot_placement"])
                    knee_buffer.append(analyzed["knee_placement"])

                except Exception as e:
                    print(f"⚠️ Error in frame: {e}")
                    continue

    cap.release()
    os.remove(temp_filename)

    # Final result
    foot_mode = max(set(foot_buffer), key=foot_buffer.count) if foot_buffer else -1
    knee_mode = max(set(knee_buffer), key=knee_buffer.count) if knee_buffer else -1

    foot_status = ["Correct", "Too tight", "Too wide", "UNK"][foot_mode] if foot_mode != -1 else "UNK"
    knee_status = ["Correct", "Too tight", "Too wide", "UNK"][knee_mode] if knee_mode != -1 else "UNK"

    return {
        "message": "Video processed successfully",
        "total_reps": counter,
        "foot_status": foot_status,
        "knee_status": knee_status
    }
# use this after executing this script :    uvicorn main:app --reload   to run the server
# and then you can use a tool like Postman or cURL to test the /upload          
# go on this URL http://127.0.0.1:8000/docs 