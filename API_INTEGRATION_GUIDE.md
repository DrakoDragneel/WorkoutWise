# API Implementation & Flutter Integration Guide (Real-Time)

## Overview
This document explains the implementation of the backend APIs for real-time exercise form correction and their integration into a Flutter app. It covers endpoint usage, authentication, request/response formats, and best practices for connecting your Flutter frontend to the backend for live camera feedback.

---

## 1. API Endpoints (Real-Time Frame Analysis)

### 1.1 Health Check
- **Endpoint:** `GET /health`
- **Purpose:** Check if the backend is running and healthy.
- **Response:**
  ```json
  { "status": "ok", "message": "API is healthy", "timestamp": "..." }
  ```

### 1.2 Plank Frame Analysis
- **Endpoint:** `POST /plank/analyze-frame`
- **Headers:**
  - `X-User-Id: <supabase_user_id>`
- **Request:**
  - `multipart/form-data` with a `file` field containing a single image frame (e.g., JPEG/PNG from camera)
- **Response:**
  ```json
  {
    "form_status": "correct", // or "incorrect", "high", "low"
    "rep_count": 5,
    "details": {}
  }
  ```
- **Notes:**
  - Call this endpoint for each frame (or every Nth frame) from the live camera feed.
  - `form_status` gives instant feedback for the current frame.
  - `rep_count` is the running count (if implemented).

### 1.3 Squat Frame Analysis
- **Endpoint:** `POST /squat/analyze-frame`
- **Headers:**
  - `X-User-Id: <supabase_user_id>`
- **Request:**
  - `multipart/form-data` with a `file` field containing a single image frame
- **Response:**
  ```json
  {
    "form_status": "correct", // or "incorrect"
    "rep_count": 7,
    "details": {}
  }
  ```
- **Notes:**
  - Call this endpoint for each frame (or every Nth frame) from the live camera feed.

---

## 2. Authentication & Security
- The backend expects a valid Supabase user ID in the `X-User-Id` header for each request.
- The Flutter app should authenticate users using Supabase Auth and pass the user ID with every API call.
- For production, restrict CORS to your Flutter app domain.

---

## 3. Flutter Integration Example (Real-Time)

### 3.1 Sending Camera Frames for Analysis
```dart
import 'package:http/http.dart' as http;
import 'package:camera/camera.dart';

Future<void> analyzeFrame(XFile frame, String supabaseUserId) async {
  final bytes = await frame.readAsBytes();
  final request = http.MultipartRequest(
    'POST',
    Uri.parse('http://<your-backend>/plank/analyze-frame'),
  );
  request.headers['X-User-Id'] = supabaseUserId;
  request.files.add(http.MultipartFile.fromBytes('file', bytes, filename: 'frame.jpg'));
  final response = await request.send();
  if (response.statusCode == 200) {
    final respStr = await response.stream.bytesToString();
    print(respStr); // Parse and use the result for live feedback
  } else {
    print('Error: ${response.statusCode}');
  }
}
```
- Call this function for each frame (or every Nth frame) from the camera stream.
- Use the response to update the UI in real time.

---

## 4. Best Practices
- Throttle requests (e.g., send every 3rd or 5th frame) to balance performance and feedback speed.
- Always check the `/health` endpoint before starting a session.
- Handle errors gracefully in the Flutter app (e.g., show user-friendly messages).
- Secure the backend by restricting CORS and validating user IDs.
- Log all API requests and errors for monitoring and debugging.

---

## 5. Troubleshooting
- If you get CORS errors, ensure the backend allows your Flutter app’s domain.
- If you get 500 errors, check backend logs for details.
- Ensure the image frame is valid and in a supported format (e.g., JPEG/PNG).

---

For further questions, contact the backend developer.
