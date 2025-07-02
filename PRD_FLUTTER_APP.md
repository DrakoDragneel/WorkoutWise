# Product Requirements Document (PRD): WorkoutWise Flutter App

## 1. Overview
WorkoutWise is a mobile application that enables users to receive real-time feedback on their exercise form (plank and squat), rep counting, and progress tracking. The app uses a Python FastAPI backend for video analysis and Supabase for authentication and user data storage.

---

## 2. Target Users
- Fitness enthusiasts
- Home workout users
- Personal trainers and their clients

---

## 3. Core Features
1. **User Authentication**
   - Email/password sign-up and login (Supabase Auth)
2. **Exercise Detection & Correction**
   - Real-time video upload for plank and squat
   - Receive feedback on form and rep count
3. **Progress Tracking**
   - Store and display user workout history
   - Visualize progress over time
4. **User Profile**
   - View and edit profile details
5. **Health & Status**
   - Show backend API health status

---

## 4. User Stories
- As a user, I want to sign up and log in securely.
- As a user, I want to upload exercise videos and get instant feedback.
- As a user, I want to see my rep count and form feedback after each session.
- As a user, I want to view my workout history and progress.
- As a user, I want to know if the backend is online before uploading videos.

---

## 5. App Flow
1. **Splash Screen** → **Login/Signup** → **Home**
2. **Home:**
   - Start new workout (choose plank or squat)
   - Upload/record video
   - View feedback/results
   - View workout history
   - Profile/settings

---

## 6. Supabase Schema

### 6.1 Users Table (Supabase Auth default)
- Managed by Supabase Auth (email, password, id, created_at, etc.)

### 6.2 Workouts Table
| Column         | Type        | Description                       |
| --------------| ----------- | --------------------------------- |
| id            | uuid        | Primary key                       |
| user_id       | uuid        | Foreign key to auth.users         |
| exercise_type | text        | 'plank' or 'squat'                |
| video_url     | text        | (optional) Supabase Storage link  |
| result_json   | jsonb       | Raw API result for this workout   |
| created_at    | timestamptz | Timestamp                         |

#### SQL for Workouts Table
```sql
create table workouts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  exercise_type text not null check (exercise_type in ('plank', 'squat')),
  video_url text,
  result_json jsonb not null,
  created_at timestamptz not null default now()
);
```

### 6.3 (Optional) Profile Table
| Column      | Type        | Description           |
| ----------- | ----------- | --------------------- |
| id         | uuid        | Primary key           |
| user_id    | uuid        | Foreign key to users  |
| display_name | text      | User's display name   |
| avatar_url | text        | Profile picture URL   |

#### SQL for Profile Table
```sql
create table profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  display_name text,
  avatar_url text
);
```

---

## 7. API Integration
- See `API_INTEGRATION_GUIDE.md` for endpoint details and usage.
- Store each workout result in the `workouts` table after receiving API feedback.

---

## 8. Non-Functional Requirements
- Responsive UI for all major devices
- Secure storage of user data
- Error handling for API/network failures
- Fast feedback (API response < 10s for typical videos)

---

## 9. Future Enhancements
- Real-time video streaming and feedback
- More exercise types
- Social features (leaderboards, sharing)
- Push notifications for workout reminders

---

## 10. Milestones
1. Backend API ready and deployed
2. Supabase schema set up
3. Flutter app: Auth, video upload, API integration
4. Progress tracking and history
5. Polish, test, and deploy
