import mediapipe as mp
import cv2
import numpy as np
import pandas as pd
import pickle
import math
import collections  # 🔹 Added for smoothing buffers

# Drawing helpers
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Load trained model
with open(r"model/LR_model.pkl", "rb") as f:
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

# Helper Functions
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

# Constants
PREDICTION_PROB_THRESHOLD = 0.7
VISIBILITY_THRESHOLD = 0.6
FOOT_SHOULDER_RATIO_THRESHOLDS = [1.2, 2.8]
KNEE_FOOT_RATIO_THRESHOLDS = {
    "up": [0.5, 1.0],
    "middle": [0.7, 1.0],
    "down": [0.7, 1.1],
}

# Buffers for smoothing foot and knee placement outputs 🔹 Added
BUFFER_SIZE = 5  # Adjust for more or less smoothing
foot_buffer = collections.deque(maxlen=BUFFER_SIZE)
knee_buffer = collections.deque(maxlen=BUFFER_SIZE)

# Real-time video
cap = cv2.VideoCapture(0)  # 0 = Default webcam

counter = 0
current_stage = ""

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        image = cv2.resize(frame, (640, 480))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        results = pose.process(image_rgb)

        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            )

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

                # 🔹 Append to smoothing buffers
                foot_buffer.append(analyzed["foot_placement"])
                knee_buffer.append(analyzed["knee_placement"])

                # 🔹 Calculate smoothed (mode) statuses
                foot_status_mode = max(set(foot_buffer), key=foot_buffer.count) if foot_buffer else -1
                knee_status_mode = max(set(knee_buffer), key=knee_buffer.count) if knee_buffer else -1

                foot_status = ["Correct", "Too tight", "Too wide", "UNK"][foot_status_mode] if foot_status_mode != -1 else "UNK"
                knee_status = ["Correct", "Too tight", "Too wide", "UNK"][knee_status_mode] if knee_status_mode != -1 else "UNK"

                cv2.rectangle(image, (0, 0), (640, 60), (0, 0, 0), -1)
                cv2.putText(image, f"Reps: {counter} | Stage: {current_stage} | Prob: {pred_prob}", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(image, f"Foot: {foot_status} | Knee: {knee_status}", (10, 45),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 0), 2)

            except Exception as e:
                print(f"⚠️ Error: {e}")

        cv2.imshow("Squat Form Checker", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
