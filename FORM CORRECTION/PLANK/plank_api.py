from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import mediapipe as mp
import pickle
import pandas as pd
import numpy as np
from collections import deque
import tempfile
import time

app = FastAPI()

# Load model and scaler
with open("model/LR_model.pkl", "rb") as f:
    sklearn_model = pickle.load(f)
with open("model/input_scaler.pkl", "rb") as f2:
    input_scaler = pickle.load(f2)

mp_pose = mp.solutions.pose

def get_class(pred):
    return {0: "C", 1: "H", 2: "L"}.get(pred)

def extract_important_keypoints(results):
    keypoints = []
    landmarks = results.pose_landmarks.landmark
    IMPORTANT_LMS = [
        "NOSE", "LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ELBOW", "RIGHT_ELBOW",
        "LEFT_WRIST", "RIGHT_WRIST", "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE",
        "LEFT_ANKLE", "RIGHT_ANKLE", "LEFT_HEEL", "RIGHT_HEEL", "LEFT_FOOT_INDEX", "RIGHT_FOOT_INDEX"
    ]
    for lm in IMPORTANT_LMS:
        landmark = landmarks[mp_pose.PoseLandmark[lm].value]
        keypoints.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
    return keypoints

@app.post("/analyze_plank_video")
async def analyze_video(file: UploadFile = File(...)):
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    cap = cv2.VideoCapture(tmp_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    prediction_threshold = 0.6
    lineancy_buffer_size = 5
    prediction_history = deque(maxlen=lineancy_buffer_size)
    last_status = None
    correct_time = 0
    incorrect_time = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                try:
                    row = extract_important_keypoints(results)
                    X = pd.DataFrame([row])
                    X_scaled = pd.DataFrame(input_scaler.transform(X))
                    pred = sklearn_model.predict(X_scaled)[0]
                    prob = sklearn_model.predict_proba(X_scaled)[0]
                    label = get_class(pred)

                    if prob[np.argmax(prob)] >= prediction_threshold:
                        prediction_history.append(label)

                    if len(prediction_history) == lineancy_buffer_size:
                        majority = max(set(prediction_history), key=prediction_history.count)

                        if majority == "C":
                            correct_time += 1
                        elif majority in ["H", "L"]:
                            incorrect_time += 1

                except Exception as e:
                    print("Prediction error:", e)

    cap.release()

    total_frames = correct_time + incorrect_time
    video_duration_sec = int(frame_count / fps)

    # Normalize time to match actual duration
    total_estimated_duration = correct_time + incorrect_time
    if total_estimated_duration > 0:
        scaling_factor = video_duration_sec / total_estimated_duration
        correct_sec = int(correct_time * scaling_factor)
        incorrect_sec = int(incorrect_time * scaling_factor)
    else:
        correct_sec = 0
        incorrect_sec = 0

    return JSONResponse({
        "correct_form_time_seconds": correct_sec,
        "incorrect_form_time_seconds": incorrect_sec
    })

# after running this , run this command in TerMinaLLL : uvicorn plank_api:app --reload
# to start the server
# 1270.0.0.1:8000/docs GO ON THIS server to test the API