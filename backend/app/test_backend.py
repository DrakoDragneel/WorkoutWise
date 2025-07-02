import os
import io
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Helper to get a sample image (replace with a real test image path or bytes)
def get_sample_image_bytes():
    # For demo: create a blank image using numpy and encode as JPEG
    import numpy as np
    import cv2
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, buf = cv2.imencode('.jpg', img)
    return buf.tobytes()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_plank_analyze_frame():
    img_bytes = get_sample_image_bytes()
    response = client.post(
        "/plank/analyze-frame",
        files={"file": ("frame.jpg", img_bytes, "image/jpeg")},
        headers={"X-User-Id": "test-user"}
    )
    assert response.status_code == 200
    assert "form_status" in response.json()
    assert "rep_count" in response.json()

def test_squat_analyze_frame():
    img_bytes = get_sample_image_bytes()
    response = client.post(
        "/squat/analyze-frame",
        files={"file": ("frame.jpg", img_bytes, "image/jpeg")},
        headers={"X-User-Id": "test-user"}
    )
    assert response.status_code == 200
    assert "form_status" in response.json()
    assert "rep_count" in response.json()
