import cv2
import mediapipe as mp
import pickle
import pandas as pd
import numpy as np
from collections import deque
import time

# Load model and scaler
with open("model/LR_model.pkl", "rb") as f:
    sklearn_model = pickle.load(f)

with open("model/input_scaler.pkl", "rb") as f2:
    input_scaler = pickle.load(f2)

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Class map
def get_class(pred):
    return {0: "C", 1: "H", 2: "L"}.get(pred)

# Important landmark extractor (68 features)
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

# Initialize webcam
cap = cv2.VideoCapture(0)

# Settings
prediction_threshold = 0.6
lineancy_buffer_size = 5
prediction_history = deque(maxlen=lineancy_buffer_size)
last_status = None
correct_start = incorrect_start = None
correct_time = 0
incorrect_time = 0

# Pose detection
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Camera error.")
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = pose.process(image_rgb)
        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            # mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            try:
                row = extract_important_keypoints(results)
                X = pd.DataFrame([row])
                X_scaled = pd.DataFrame(input_scaler.transform(X))

                pred = sklearn_model.predict(X_scaled)[0]
                prob = sklearn_model.predict_proba(X_scaled)[0]
                label = get_class(pred)

                if prob[np.argmax(prob)] >= prediction_threshold:
                    prediction_history.append(label)

                # Apply buffer logic
                if len(prediction_history) == lineancy_buffer_size:
                    majority = max(set(prediction_history), key=prediction_history.count)

                    # Only update if status changes
                    if majority != last_status:
                        last_status = majority
                        if majority == "C":
                            correct_start = time.time()
                            incorrect_time += (time.time() - incorrect_start) if incorrect_start else 0
                            incorrect_start = None
                        else:
                            incorrect_start = time.time()
                            correct_time += (time.time() - correct_start) if correct_start else 0
                            correct_start = None

                # Live timer update
                if last_status == "C" and correct_start:
                    elapsed = time.time() - correct_start
                    correct_total = correct_time + elapsed
                else:
                    correct_total = correct_time

                if last_status in ["H", "L"] and incorrect_start:
                    elapsed = time.time() - incorrect_start
                    incorrect_total = incorrect_time + elapsed
                else:
                    incorrect_total = incorrect_time

                # 🖥️ Overlay on frame
                cv2.rectangle(image, (0, 0), (350, 100), (0, 0, 0), -1)
                cv2.putText(image, f"Form: {last_status or 'Analyzing...'}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(image, f"Correct Time: {int(correct_total)}s", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(image, f"Incorrect Time: {int(incorrect_total)}s", (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 2)

            except Exception as e:
                print("Error during prediction:", e)

        else:
            cv2.putText(image, "No human detected", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Plank Form Detection with Timer", image)

        if cv2.waitKey(10) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
