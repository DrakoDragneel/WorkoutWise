# WorkoutWise

A multi-module Python project for exercise form correction and personalized workout recommendations using computer vision and machine learning.

## Project Structure

```
WorkoutWise/
├── requirements.txt
├── FORM CORRECTION/
│   ├── PLANK/
│   │   ├── plank_api.py
│   │   ├── PLANK_withTimer.py
│   │   ├── requirement.txt.txt
│   │   ├── Dataset/
│   │   ├── model/
│   │   └── Training/
│   └── SQUAT/
│       ├── main.py
│       ├── SQUAT.py
│       ├── requirements.txt
│       ├── Dataset/
│       ├── model/
│       └── Training/
└── Workout Exercise Model/
    ├── app.py
    ├── recommender.py
    ├── Data set/
    └── models/
```

## Modules Overview

### 1. FORM CORRECTION

#### PLANK
- **Purpose:** Detects and evaluates plank exercise form using webcam or video input.
- **Key Scripts:**
  - `plank_api.py`: FastAPI backend for analyzing plank videos. Run with `uvicorn plank_api:app --reload`.
  - `PLANK_withTimer.py`: Real-time plank form detection with timer using webcam.
- **Models:** Trained scikit-learn models and scalers in `model/`.
- **Datasets:** CSVs for training/testing in `Dataset/`.
- **Requirements:** See `requirement.txt.txt` for dependencies (install in the PLANK folder).

#### SQUAT
- **Purpose:** Detects and evaluates squat form, counts reps, and analyzes foot/knee placement.
- **Key Scripts:**
  - `main.py`: FastAPI backend for squat video analysis. Run with `uvicorn main:app --reload`.
  - `SQUAT.py`: Real-time squat form detection and rep counter using webcam.
- **Models:** Trained models in `model/`.
- **Datasets:** CSVs for training/testing in `Dataset/`.
- **Requirements:** See `requirements.txt` in the SQUAT folder (install in the SQUAT folder).

### 2. Workout Exercise Model
- **Purpose:** Recommends personalized workout plans based on user input.
- **Key Scripts:**
  - `app.py`: Flask API for workout recommendations. Run with `python app.py`.
  - `recommender.py`: Core logic for generating recommendations.
- **Models:** Pre-trained clustering and encoding models in `models/`.
- **Datasets:** Synthetic fitness data in `Data set/`.

## Setup & Installation

1. **Clone the repository and navigate to the root directory.**
2. **Create a virtual environment with Python 3.10:**
   ```
   py -3.10 -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install root requirements:**
   ```
   pip install -r requirements.txt
   ```
4. **Install submodule requirements:**
   - For PLANK:
     ```
     pip install -r "FORM CORRECTION/PLANK/requirement.txt.txt"
     ```
   - For SQUAT:
     ```
     pip install -r "FORM CORRECTION/SQUAT/requirements.txt"
     ```

## Running the Applications

### Plank Form Correction API
```bash
cd "FORM CORRECTION/PLANK"
uvicorn plank_api:app --reload
# Visit http://127.0.0.1:8000/docs for API documentation
```

### Plank Real-Time Detection
```bash
cd "FORM CORRECTION/PLANK"
python PLANK_withTimer.py
```

### Squat Form Correction API
```bash
cd "FORM CORRECTION/SQUAT"
uvicorn main:app --reload
# Visit http://127.0.0.1:8000/docs for API documentation
```

### Squat Real-Time Detection
```bash
cd "FORM CORRECTION/SQUAT"
python SQUAT.py
```

### Workout Recommendation API
```bash
cd "Workout Exercise Model"
python app.py
# POST to /recommend with user data
```

## Datasets & Models
- Each module contains its own datasets and pre-trained models.
- Datasets are in CSV format, and models are stored as `.pkl` files.

## Requirements
- Python 3.10
- See each module's requirements file for dependencies.

## License
Specify your license here (e.g., MIT, Apache 2.0).

## Author
Add your name and contact information here.
