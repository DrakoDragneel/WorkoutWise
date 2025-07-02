# WorkoutWise

A minimal, production-ready Python backend for exercise form correction using computer vision and machine learning. Designed for integration with a Flutter app (with Supabase authentication).

## Project Structure

```
backend/
    app/
        main.py           # FastAPI backend (all endpoints)
        models/
            plank_input_scaler.pkl
            plank_LR_model.pkl
            squat_LR_model.pkl
requirements.txt
README.md
```

## Features
- Plank and squat form analysis from video (API endpoints)
- Rep counting and form feedback
- Health check endpoint for uptime monitoring
- Logging for API requests and errors
- CORS enabled for Flutter integration

## Setup & Installation

1. **Create a virtual environment (Python 3.10 recommended):**
   ```
   py -3.10 -m venv venv
   .\venv\Scripts\activate
   ```
2. **Install requirements:**
   ```
   pip install -r requirements.txt
   ```
3. **Run the API:**
   ```
   uvicorn backend.app.main:app --reload
   ```
4. **Access API docs:**
   - Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Endpoints

### Health Check
- **GET** `/health`
- **Response:** `{ "status": "ok", "message": "API is healthy", ... }`

### Plank Analysis
- **POST** `/plank/analyze`
- **Headers:** `X-User-Id: <supabase_user_id>`
- **Request:** `multipart/form-data` with `file` (video)
- **Response:**
  ```json
  {
    "correct_form_time_seconds": 30,
    "incorrect_form_time_seconds": 10,
    "rep_count": 0,
    "details": {}
  }
  ```

### Squat Analysis
- **POST** `/squat/analyze`
- **Headers:** `X-User-Id: <supabase_user_id>`
- **Request:** `multipart/form-data` with `file` (video)
- **Response:**
  ```json
  {
    "rep_count": 15,
    "foot_status": "Correct",
    "knee_status": "Too tight",
    "details": {}
  }
  ```

## Example Usage (Flutter)
```dart
final request = http.MultipartRequest('POST', Uri.parse('http://<your-backend>/plank/analyze'));
request.headers['X-User-Id'] = supabaseUserId;
request.files.add(await http.MultipartFile.fromPath('file', videoPath));
final response = await request.send();
```

## Logging
- All API requests and errors are logged to the console.

## License
Specify your license here (e.g., MIT, Apache 2.0).

## Author
Add your name and contact information here.
