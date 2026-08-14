# AI-Powered Interactive Puzzle Game for Children

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://reactjs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-ResNet50-orange)](https://pytorch.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-Educational-purple)](LICENSE)

> **Computer Science Final Year Project**
> An intelligent puzzle game that uses advanced Computer Vision and Deep Learning to validate puzzle piece selections in real-time.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Computer Vision Algorithms](#computer-vision-algorithms)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Problems Encountered and Solved](#problems-encountered-and-solved)
- [Performance](#performance)
- [Deployment](#deployment)
- [License](#license)

---

## Overview

This project transforms traditional children's puzzles into an intelligent, interactive digital experience. Instead of parental supervision, an advanced Computer Vision system automatically validates whether a child has selected the correct puzzle piece.

### Problem Statement

Traditional physical puzzles require constant parental supervision for validation. This project creates an autonomous system that:

- Eliminates the need for parental oversight
- Provides instant feedback with confidence scores
- Adapts difficulty progressively (5 levels)
- Tracks learning progress with per-user game history

### Solution

A full-stack application combining:

- **Boundary-matching CV** as the primary validation strategy, with deep learning tiebreakers
- **JWT-authenticated user accounts** with persistent game history
- **Beautiful React UI** designed for children, with drag-and-drop interaction
- **Parallel image fetching** for fast puzzle creation

---

## Features

### Game Features

- **5 Difficulty Levels** — Beginner (2 pieces) through Expert (32 pieces)
- **Multi-region puzzles** — Choose 1–4 missing regions per puzzle
- **Drag-and-drop interface** — Drag pieces from the options grid into the black squares
- **Random Images** — Fresh, kid-friendly, colorful images every game via Unsplash
- **Custom Image Upload** — Upload your own image (PNG/JPG/GIF/WebP, max 16 MB)
- **Instant Validation** — AI validates in seconds with confidence scoring
- **Hint System** — Context-aware hints (enabled once only one piece remains)
- **Confetti animation** on puzzle completion
- **Scoring** — Up to 100 points per puzzle; score decreases with each wrong attempt

### User Features

- **Account registration** with avatar selection (5 avatars)
- **JWT-based authentication** with HTTP-only cookies and automatic token refresh
- **Guest mode** — play without an account
- **Edit Profile** — change avatar, change password, or delete account
- **Game History** — view all past games with image, difficulty, score, and timestamp
- **Total score** shown in the user bar across all pages

### AI Features

- **Boundary Matching** (primary) — HSV histogram analysis of color strips adjacent to each black square
- **Ranking-based validation** — all 6 candidate pieces are ranked; top-ranked is correct
- **Tiebreaker validation** — when scores are close, comprehensive analysis kicks in (ResNet50 semantic features + LBP texture + color + edge detection)
- **Confidence Scoring** — 0–100% certainty per placement

### UI/UX Features

- **React Router navigation** — multi-page SPA with clean URL routing
- **Pink/lavender color scheme** with smooth Framer Motion transitions
- **Shared UserBar** with hamburger menu on all post-login pages
- **Toast notifications** for real-time feedback
- **Responsive design** targeting desktop and tablet

---

## Technology Stack

### Backend

| Technology              | Purpose                              | Version  |
| ----------------------- | ------------------------------------ | -------- |
| **Python**              | Core language                        | 3.8+     |
| **Flask**               | Web framework                        | 3.1.2    |
| **Flask-CORS**          | Cross-origin resource sharing        | 6.0.1    |
| **Flask-SQLAlchemy**    | ORM / database layer                 | 3.1+     |
| **Flask-JWT-Extended**  | JWT authentication                   | 4.7+     |
| **Flask-Bcrypt**        | Password hashing                     | 1.0+     |
| **Flask-Limiter**       | Rate limiting                        | 3.8+     |
| **PyTorch**             | ResNet50 deep learning               | 2.9.1    |
| **Torchvision**         | Pre-trained model weights            | 0.24.1   |
| **OpenCV**              | Computer vision                      | 4.12.0   |
| **NumPy**               | Numerical computing                  | 2.2.6    |
| **Pillow**              | Image manipulation                   | 12.0.0   |
| **scikit-image**        | Image processing / LBP               | 0.25.2   |
| **scikit-learn**        | ML utilities / distance metrics      | 1.7.2    |
| **SciPy**               | Signal processing / distance metrics | 1.16.3   |
| **Requests**            | HTTP client (Unsplash API)           | 2.32.5   |
| **psycopg2-binary**     | PostgreSQL adapter                   | 2.9+     |
| **python-dotenv**       | Environment variable management      | 1.2.1    |
| **Gunicorn**            | Production WSGI server               | 23.0.0   |

### Frontend

| Technology             | Purpose             | Version  |
| ---------------------- | ------------------- | -------- |
| **React**              | UI framework        | 18.2.0   |
| **React Router DOM**   | Client-side routing | 7.13.1   |
| **Framer Motion**      | Animations          | 10.16.16 |
| **React Toastify**     | Toast notifications | 9.1.3    |
| **React Confetti**     | Celebration effects | 6.1.0    |
| **Axios**              | HTTP client         | 1.6.2    |

### Database

| Technology       | Purpose                        |
| ---------------- | ------------------------------ |
| **PostgreSQL**   | Persistent storage             |
| **SQLAlchemy**   | ORM models (User, GameHistory) |

### External APIs

| Service      | Purpose                           | Tier           |
| ------------ | --------------------------------- | -------------- |
| **Unsplash** | Random kid-friendly puzzle images | Free (50/hour) |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       Frontend (React)                           │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐   │
│   │ Welcome  │ │  Login / │ │  Game    │ │History │ │ Edit   │   │
│   │ Screen   │ │  Signup  │ │  Board   │ │ Screen │ │Profile │   │
│   └──────────┘ └──────────┘ └──────────┘ └────────┘ └────────┘   │
└──────────────────────────────┬───────────────────────────────────┘
                               │ REST API (JSON, HTTP-only cookies)
┌──────────────────────────────▼───────────────────────────────────┐
│                      Backend (Flask)                             │
│  ┌─────────────────────────┐   ┌──────────────────────────────┐  │
│  │   app.py (puzzle routes)│   │  routes/auth.py (auth routes │  │
│  │  /puzzle/create         │   │  /auth/register  /auth/login │  │
│  │  /puzzle/validate       │   │  /auth/me        /auth/logout│  │
│  │  /puzzle/hint           │   │  /auth/history               │  │
│  └───────────┬─────────────┘   │  /auth/update-avatar         │  │
│              │                 │  /auth/change-password       │  │
│  ┌───────────▼─────────────┐   │  /auth/delete-account        │  │
│  │    Puzzle Generator     │   └──────────────┬───────────────┘  │
│  │  (parallel image fetch) │                  │                  │
│  └───────────┬─────────────┘   ┌──────────────▼───────────────┐  │
│              │                 │  PostgreSQL (via SQLAlchemy) │  │
│  ┌───────────▼─────────────┐   │  User | GameHistory tables   │  │
│  │      CV Validator       │   └──────────────────────────────┘  │
│  │  Boundary Matching (HSV)│                                     │
│  │  ResNet50 (tiebreaker)  │                                     │
│  │  LBP / Color / Edge     │                                     │
│  └─────────────────────────┘                                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Computer Vision Algorithms

### Validation Flow (every guess)

Every time the user places a piece, the following runs in order:

**Step 1 — Boundary Ranking (all 6 candidates)**
The system extracts thin color strips from the four edges surrounding the black square and computes HSV histogram similarity for every candidate piece. All 6 are ranked; the user is correct if their piece ranks #1.

```python
# Simplified boundary matching
border = extract_border_strip(puzzle_image, zone)
piece_edge = extract_piece_edge(candidate_piece)
score = cv2.compareHist(border_hist, edge_hist, cv2.HISTCMP_CORREL)
```

**Step 2 — Comprehensive Validation (user's piece, always)**
Runs on every guess to produce the confidence score shown in the UI:

| Algorithm          | Weight | Technique                               |
| ------------------ | ------ | --------------------------------------- |
| **Boundary**       | 35%    | HSV histogram boundary matching         |
| **Feature (DL)**   | 35%    | ResNet50 cosine similarity (PyTorch)    |
| **Color**          | 15%    | HSV histogram + K-Means dominant colors |
| **Texture**        | 10%    | LBP (Local Binary Patterns)             |
| **Edge**           | 5%     | Canny / Sobel edge density              |

**Step 3 — Tiebreaker (only when needed)**
If the user's piece did not rank #1 but is within 0.02 of the top score (e.g. uniform regions like clear sky or white walls), comprehensive validation also runs on each competing piece. The user wins the tie if their comprehensive score is higher.

### Why Ranking Instead of Thresholding?

Earlier versions used fixed confidence thresholds to accept/reject. This caused false positives when all decoys were visually similar, and false negatives when the correct piece had low absolute similarity. Ranking is immune to this: the correct piece just needs to beat the decoys, regardless of absolute scores.

---

## Quick Start

### Prerequisites

```bash
python --version   # 3.8+ required
node --version     # 16+ required
npm --version
```

> **Windows users:** Keep the project in a short path (e.g., `C:\puzzle-game\`) to avoid the 260-character path limit that can break deep dependency installs.

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-puzzle-game.git
cd ai-puzzle-game
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env: add UNSPLASH_ACCESS_KEY and DATABASE_URL
```

Key `.env` variables:

```
UNSPLASH_ACCESS_KEY=your_unsplash_key
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/puzzle_game_db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

```bash
python app.py
```

Backend runs at `http://localhost:5000`

### 3. Frontend setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`

---

## Installation

### Get an Unsplash API Key

1. Go to [https://unsplash.com/developers](https://unsplash.com/developers)
2. Sign up and create a new application
3. Copy your **Access Key** into `backend/.env`

Free tier: 50 requests/hour. The game biases queries toward bright, colorful, kid-friendly images.

### Database Setup

```bash
# With PostgreSQL running locally:
createdb puzzle_game_db

# Flask-SQLAlchemy creates tables automatically on first run
python app.py
```

---

## API Documentation

### Base URL

```
http://localhost:5000/api
```

### Puzzle Endpoints

#### Health Check

```http
GET /api/health
```

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "validator_type": "boundary_ranking"
}
```

#### Create Puzzle

```http
POST /api/puzzle/create
Content-Type: application/json

{
  "difficulty": 3,
  "num_regions": 2,
  "use_random_image": true
}
```

```json
{
  "game_id": "uuid-here",
  "puzzle_image": "data:image/png;base64,...",
  "options": ["data:image/png;base64,..."],
  "difficulty": { "level": 3, "name": "Medium", "pieces": 8 },
  "grid": { "rows": 2, "cols": 4 },
  "missing_zones": [3, 6]
}
```

#### Validate Answer

```http
POST /api/puzzle/validate
Content-Type: application/json

{
  "game_id": "uuid",
  "zone_index": 0,
  "option_index": 2
}
```

```json
{
  "is_correct": true,
  "confidence": 0.91,
  "attempt_number": 1,
  "validation_details": {
    "boundary_score": 0.88,
    "feature_score": 0.94,
    "color_score": 0.87,
    "texture_score": 0.89,
    "edge_score": 0.85
  }
}
```

#### Get Active Game Stats

```http
GET /api/stats
```

```json
{
  "active_games": 3,
  "memory_usage": "~12 MB"
}
```

#### Clean Up Finished Game

```http
POST /api/puzzle/cleanup
Content-Type: application/json

{ "game_id": "uuid" }
```

```json
{ "message": "Game cleaned up" }
```

#### Get Hint

```http
POST /api/puzzle/hint
Content-Type: application/json

{ "game_id": "uuid", "zone_index": 0 }
```

```json
{
  "hint": "Look for a piece with warm orange tones along the left edge.",
  "hint_type": "color"
}
```

### Auth Endpoints

All auth routes are under `/api/auth/`. Tokens are stored in HTTP-only cookies.

| Endpoint                  | Method | Auth Required | Purpose                             |
| ------------------------- | ------ | ------------- | ----------------------------------- |
| `/auth/register`          | POST   | No            | Create account (username, email, password, avatar_id) |
| `/auth/login`             | POST   | No            | Login; sets JWT cookies (rate limited: 5/15 min) |
| `/auth/logout`            | POST   | No            | Clear JWT cookies                   |
| `/auth/refresh`           | POST   | Refresh token | Refresh access token                |
| `/auth/me`                | GET    | Yes           | Get current user profile            |
| `/auth/update-avatar`     | PATCH  | Yes           | Change avatar (1–5)                 |
| `/auth/change-password`   | PATCH  | Yes           | Change password (requires current)  |
| `/auth/delete-account`    | DELETE | Yes           | Delete account and all history      |
| `/auth/history`           | GET    | Yes           | Get game history (newest first)     |

---

## Project Structure

```
ai-puzzle-game/
│
├── backend/
│   ├── app.py                    # Main Flask app + puzzle endpoints
│   ├── config.py                 # Configuration (difficulty levels, JWT, etc.)
│   ├── extensions.py             # Flask extensions (db, jwt, bcrypt, limiter)
│   ├── run.py                    # Production runner
│   │
│   ├── models/
│   │   ├── user.py               # User ORM model
│   │   ├── game_history.py       # GameHistory ORM model
│   │   ├── puzzle_generator.py   # Puzzle creation + parallel image fetching
│   │   ├── image_processor.py    # Image manipulation utilities
│   │   └── cv_validator.py       # Validation orchestration
│   │
│   ├── routes/
│   │   └── auth.py               # All authentication endpoints
│   │
│   └── utils/
│       ├── boundary_matcher.py   # Primary CV: HSV boundary matching
│       ├── feature_extraction.py # ResNet50 deep features (tiebreaker)
│       ├── texture_analysis.py   # LBP texture analysis
│       ├── edge_detection.py     # Canny / Hausdorff edge matching
│       └── unsplash_api.py       # Unsplash image fetching
│
└── frontend/
    └── src/
        ├── App.jsx               # Router + top-level state machine
        ├── services/
        │   └── api.js            # Unified fetch wrapper (credentials: include)
        └── components/
            ├── WelcomeScreen/    # Home: difficulty & region select, user info
            ├── LoginScreen/      # Email/password login
            ├── SignupScreen/     # Registration + avatar picker
            ├── UserBar/          # Shared header with hamburger menu
            ├── GameBoard/        # Main game: drag-drop, validate, hints
            ├── OptionsGrid/      # Draggable candidate piece cards
            ├── PuzzleImage/      # Puzzle display with drop-zone overlays
            ├── ImageSelector/    # Random vs. custom image choice
            ├── LoadingScreen/    # Spinner during puzzle creation
            ├── ValidationModal/  # Results: correctness, confidence, breakdown
            ├── HistoryScreen/    # Past games list with stats
            └── EditProfileScreen/# Avatar change, password change, account delete
```

---

## Problems Encountered and Solved

### Problem: Long Loading Time When Creating a Puzzle

**The problem:**
When starting a new puzzle with `use_random_image: true`, the backend had to fetch multiple images from the Unsplash API — one main image plus 5 decoy images (one per decoy piece). These requests were made **sequentially**, one after another, meaning each HTTP round-trip had to complete before the next one started. With 6 requests at ~1–2 seconds each over the network, users were waiting **6–10 seconds** on the loading screen just to see the puzzle. This was especially frustrating on slower connections.

**The solution (`feature/parallel-image-fetch`):**
We refactored `puzzle_generator.py` to fetch all images **concurrently** using Python's `ThreadPoolExecutor`. The main image and all decoy images are dispatched simultaneously, and the code waits for all of them to finish before proceeding.

```python
from concurrent.futures import ThreadPoolExecutor

def prefetch_all_images(self, num_decoys):
    with ThreadPoolExecutor(max_workers=1 + num_decoys) as executor:
        main_future = executor.submit(get_random_image)
        decoy_futures = [executor.submit(get_random_image) for _ in range(num_decoys)]

        main_image, main_url = main_future.result()
        decoy_images = [f.result() for f in decoy_futures]

    return main_image, main_url, decoy_images
```

**Result:**
Puzzle creation time dropped by approximately **50%**. What previously took 6–10 seconds now completes in 2–4 seconds, because the 6 network requests run in parallel rather than in series. The loading screen is now a brief moment rather than a noticeable wait.

---

## Performance

### Puzzle Creation Speed

| Method         | Images Fetched | Typical Time |
| -------------- | -------------- | ------------ |
| Sequential     | 6 (1 + 5)      | 6–10 sec     |
| **Parallel**   | 6 (1 + 5)      | **2–4 sec**  |

### Validation Speed

| Step                   | Trigger                          | Speed   |
| ---------------------- | -------------------------------- | ------- |
| **Boundary ranking**   | Every guess (all 6 candidates)   | < 1 sec |
| **Comprehensive (x1)** | Every guess (user's piece)       | 2–4 sec |
| **Comprehensive (x2+)**| Tie within 0.02 margin           | +2–4 sec per competing piece |

### Scoring

| Outcome  | Score Formula                          | Range     |
| -------- | -------------------------------------- | --------- |
| Correct  | `max(10, 100 - 10 * (attempts - 1))`   | 10–100 pts|
| Incorrect| 0 points                               | 0 pts     |

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full guide.

### Production Checklist

- [ ] Set `DEBUG=False` and `FLASK_ENV=production`
- [ ] Use a strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Set `JWT_COOKIE_SECURE=True` (HTTPS only)
- [ ] Configure `CORS_ORIGINS` to your frontend domain
- [ ] Use a managed PostgreSQL instance
- [ ] Run backend with Gunicorn behind a reverse proxy (nginx)
- [ ] Set Unsplash API key in environment
- [ ] Enable rate limiting for auth endpoints

---

## License

This project is licensed under the **Educational License** — see [LICENSE](LICENSE) for details.

- Educational use: allowed
- Personal projects: allowed
- Portfolio showcase: allowed
- Commercial use: requires attribution

---

<p align="center">
  <strong>Made with care for educational purposes</strong><br/>
  <sub>Computer Science Final Year Project — 2024–2025</sub>
</p>

<p align="center">
  <a href="#ai-powered-interactive-puzzle-game-for-children">Back to Top</a>
</p>
