from fastapi import FastAPI, File, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import mediapipe as mp
import pickle
import pandas as pd
import numpy as np
from collections import deque
import tempfile
import os
import uuid
import shutil
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger("workoutwise-api")

# Enable CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load model and scaler once at startup
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
with open(os.path.join(MODEL_DIR, "LR_model.pkl"), "rb") as f:
    sklearn_model = pickle.load(f)
with open(os.path.join(MODEL_DIR, "input_scaler.pkl"), "rb") as f2:
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

# SQUAT-specific keypoints and helpers
SQUAT_IMPORTANT_LMS = [
    "NOSE", "LEFT_SHOULDER", "RIGHT_SHOULDER",
    "LEFT_HIP", "RIGHT_HIP", "LEFT_KNEE", "RIGHT_KNEE",
    "LEFT_ANKLE", "RIGHT_ANKLE"
]
SQUAT_HEADERS = ["label"] + [f"{lm.lower()}_{axis}" for lm in SQUAT_IMPORTANT_LMS for axis in ["x","y","z","v"]]

def extract_squat_keypoints(results):
    landmarks = results.pose_landmarks.landmark
    data = []
    for lm in SQUAT_IMPORTANT_LMS:
        keypoint = landmarks[mp_pose.PoseLandmark[lm].value]
        data.append([keypoint.x, keypoint.y, keypoint.z, keypoint.visibility])
    return np.array(data).flatten().tolist()

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
    def calculate_distance(pointX, pointY):
        x1, y1 = pointX
        x2, y2 = pointY
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
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

@app.get("/health")
def health_check():
    """Health check endpoint for uptime monitoring."""
    logger.info("Health check requested.")
    return {"status": "ok", "message": "API is healthy", "timestamp": __import__('datetime').datetime.utcnow().isoformat()}

@app.post("/plank/analyze")
async def analyze_plank(file: UploadFile = File(...), x_user_id: str = Header(...)):
    logger.info(f"Plank analysis requested by user: {x_user_id}")
    """Analyze a plank exercise video/image. Returns rep count, form feedback, and details."""
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
                    logger.error(f"Plank analysis error: {e}")
                    continue

    cap.release()
    os.remove(tmp_path)

    total_frames = correct_time + incorrect_time
    video_duration_sec = int(frame_count / fps) if fps else 0

    # Normalize time to match actual duration
    total_estimated_duration = correct_time + incorrect_time
    if total_estimated_duration > 0:
        scaling_factor = video_duration_sec / total_estimated_duration if video_duration_sec else 1
        correct_sec = int(correct_time * scaling_factor)
        incorrect_sec = int(incorrect_time * scaling_factor)
    else:
        correct_sec = 0
        incorrect_sec = 0

    return JSONResponse({
        "correct_form_time_seconds": correct_sec,
        "incorrect_form_time_seconds": incorrect_sec,
        "rep_count": 0,  # Rep counting not implemented in this logic
        "details": {}
    })

@app.post("/squat/analyze")
async def analyze_squat(file: UploadFile = File(...), x_user_id: str = Header(...)):
    logger.info(f"Squat analysis requested by user: {x_user_id}")
    temp_filename = f"temp_{uuid.uuid4().hex}.mp4"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    cap = cv2.VideoCapture(temp_filename)
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
    foot_buffer = deque(maxlen=5)
    knee_buffer = deque(maxlen=5)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            if results.pose_landmarks:
                try:
                    row = extract_squat_keypoints(results)
                    X = pd.DataFrame([row], columns=SQUAT_HEADERS[1:])
                    predicted_class = sklearn_model.predict(X)[0]
                    predicted_class = "down" if predicted_class == 0 else "up"
                    pred_prob = round(sklearn_model.predict_proba(X)[0].max(), 2)
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
                    logger.error(f"Squat analysis error: {e}")
                    continue
    cap.release()
    os.remove(temp_filename)
    foot_mode = max(set(foot_buffer), key=foot_buffer.count) if foot_buffer else -1
    knee_mode = max(set(knee_buffer), key=knee_buffer.count) if knee_buffer else -1
    foot_status = ["Correct", "Too tight", "Too wide", "UNK"][foot_mode] if foot_mode != -1 else "UNK"
    knee_status = ["Correct", "Too tight", "Too wide", "UNK"][knee_mode] if knee_mode != -1 else "UNK"
    return JSONResponse({
        "rep_count": counter,
        "foot_status": foot_status,
        "knee_status": knee_status,
        "details": {}
    })

@app.post("/plank/analyze-frame")
async def analyze_plank_frame(file: UploadFile = File(...), x_user_id: str = Header(...)):
    logger.info(f"Plank frame analysis requested by user: {x_user_id}")
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    frame = cv2.imread(tmp_path)
    os.remove(tmp_path)
    if frame is None:
        logger.error("Could not read image frame for plank analysis.")
        return JSONResponse({"error": "Invalid image frame."}, status_code=400)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(image_rgb)
    if results.pose_landmarks:
        try:
            row = extract_important_keypoints(results)
            X = pd.DataFrame([row])
            X_scaled = pd.DataFrame(input_scaler.transform(X))
            pred = sklearn_model.predict(X_scaled)[0]
            label = get_class(pred)
            # For demo: rep_count is always 0 (implement stateful counting in app if needed)
            return JSONResponse({
                "form_status": label,  # "C" (correct), "H" (high), "L" (low)
                "rep_count": 0,
                "details": {}
            })
        except Exception as e:
            logger.error(f"Plank frame analysis error: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    else:
        return JSONResponse({"form_status": "no_person", "rep_count": 0, "details": {}}, status_code=200)

@app.post("/squat/analyze-frame")
async def analyze_squat_frame(file: UploadFile = File(...), x_user_id: str = Header(...)):
    logger.info(f"Squat frame analysis requested by user: {x_user_id}")
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    frame = cv2.imread(tmp_path)
    os.remove(tmp_path)
    if frame is None:
        logger.error("Could not read image frame for squat analysis.")
        return JSONResponse({"error": "Invalid image frame."}, status_code=400)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(image_rgb)
    if results.pose_landmarks:
        try:
            row = extract_squat_keypoints(results)
            X = pd.DataFrame([row], columns=SQUAT_HEADERS[1:])
            predicted_class = sklearn_model.predict(X)[0]
            label = "down" if predicted_class == 0 else "up"
            # For demo: rep_count is always 0 (implement stateful counting in app if needed)
            return JSONResponse({
                "form_status": label,  # "up", "down"
                "rep_count": 0,
                "details": {}
            })
        except Exception as e:
            logger.error(f"Squat frame analysis error: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
    else:
        return JSONResponse({"form_status": "no_person", "rep_count": 0, "details": {}}, status_code=200)
