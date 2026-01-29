# 🧩 COMPLETE ME

> **Computer Science Final Year Project**  
> An intelligent puzzle game for children that uses Computer Vision to automatically validate puzzle piece selections.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green)](https://opencv.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

---

## 📖 Overview

**COMPLETE ME** transforms traditional children's puzzles into an autonomous digital experience. Instead of requiring parental supervision, the system uses advanced Computer Vision algorithms to validate whether a child has selected the correct puzzle piece.

### 🎯 The Problem

#### Traditional Physical Puzzles

**❌ Parental Dependency**
- Require constant adult supervision for validation
- Parents aren't always available for immediate feedback

**❌ Severely Limited Visual Content**
- Only 10-30 fixed images per puzzle box
- Limited fixed images for all online puzzle games
- Children quickly lose interest in repetitive themes
- Cannot match the child's current interests (dinosaurs today, space tomorrow)
- No variety or surprise element

**Result:** Children lose engagement and miss learning opportunities.

### 💡 The Solution

#### COMPLETE ME: Unlimited Possibilities

**✅ Autonomous AI Validation**
- Instant feedback without parental oversight
- Progressive difficulty adaptation (Beginner → Expert)
- Real-time performance tracking

**✅ Infinite Visual Library**
- 🌍 **Millions of images** from Unsplash's vast collection
- 🔍 **Smart search** - find specific interests ("puppies", "rockets", "rainbow")
- 📂 **Curated categories** - Animals, Nature, Space, Cars, Food, Toys, Flowers
- 🎲 **"Surprise Me" mode** - fresh, random content every time
- 🎨 **Never the same puzzle twice** - endless variety keeps children engaged
- 🛡️ **Child-safe filtering** - all content verified for appropriateness

**Result:** Children stay engaged, explore diverse interests, and maximize learning.

--- 

## ✨ Key Features

### 🎮 Gameplay
- **4 Difficulty Levels** - Beginner (2 pieces) → Expert (32 pieces)
- **Flexible Missing Pieces** - Choose 1-4 pieces to find
- **Three Image Selection Modes:**
  - 🔍 **Search** - Find specific topics (e.g., "cats", "space")
  - 🎲 **Surprise Me** - Random high-quality images
  - 📂 **Categories** - Curated topics (Animals, Nature, Space, Cars, etc.)

### 🤖 AI Validation
The system employs **three Computer Vision layers** for robust validation:

| Layer | Algorithm | Purpose |
|-------|-----------|---------|
| **Edge Detection** | Canny, Sobel | Analyzes boundary continuity |
| **Color Analysis** | HSV Histograms | Compares color distribution |
| **Texture Analysis** | LBP, Gabor Filters | Verifies pattern consistency |

**Optional Enhancement:** Deep Learning validation using PyTorch (ResNet50/VGG16) for semantic analysis.

### 👤 User Management
- **Secure Authentication** - JWT-based login system
- **Guest Mode** - Play without registration
- **Profile System** - Customizable avatars and progress tracking
- **Game History** - View last 10+ completed puzzles

### 🎨 Child-Friendly Interface
- High-contrast colors and large buttons
- Minimal text, icon-driven design
- Smooth animations and visual feedback
- Victory celebrations with confetti

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Client Layer (Frontend)                  │
│          HTML5 • CSS3 • JavaScript • Fetch API           │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (JSON)
┌────────────────────────▼────────────────────────────────┐
│                 Server Layer (Backend)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │     Flask    │  │   OpenCV     │  │   Unsplash   │  │
│  │  Web Server  │  │ CV Validator │  │     API      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ SQL Queries
┌────────────────────────▼────────────────────────────────┐
│              Data Layer (PostgreSQL)                     │
│        Users • Game_History • Authentication             │
└─────────────────────────────────────────────────────────┘
```

### Architecture Highlights
- **Client-Server Pattern** - Clear separation of concerns
- **RESTful API** - Stateless communication
- **Security First** - Rate limiting, input sanitization, JWT authentication

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python** | Core language |
| **Flask** | Web framework |
| **PostgreSQL** | Database (local installation) |
| **OpenCV** | Computer Vision algorithms |
| **PyTorch** | Deep Learning (optional) |
| **bcrypt** | Password hashing |
| **JWT** | Authentication tokens |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure |
| **CSS3** | Styling & animations |
| **JavaScript (ES6)** | Interactivity |
| **Fetch API** | HTTP client |

### External APIs
| Service | Purpose | Tier |
|---------|---------|------|
| **Unsplash API** | Child-safe images | Free (50 requests/hour) |

---

## 📁 Project Structure

```
complete-me/
│
├── backend/                      # Flask server
│   ├── models/                   # Core business logic
│   │   ├── authentication.py     # User auth & JWT
│   │   ├── game_management.py    # Game sessions & scoring
│   │   ├── image_processor.py    # Image fetching & masking
│   │   └── cv_validator.py       # Computer Vision validation
│   │
│   ├── utils/                    # CV algorithms
│   │   ├── edge_detection.py     # Canny, Sobel
│   │   ├── color_analysis.py     # HSV histograms
│   │   └── texture_analysis.py   # LBP, Gabor filters
│   │
│   ├── static/                   # Static files
│   │   └── temp/                 # Temporary image storage
│   │
│   ├── app.py                    # Main Flask application
│   ├── config.py                 # Configuration settings
│   ├── requirements.txt          # Python dependencies
│   └── .env              # Environment template
│
├── frontend/                     # Web interface
│   ├── index.html                # Main HTML file
│   ├── styles/                   # CSS files
│   │   ├── main.css
│   │   ├── game.css
│   │   └── animations.css
│   │
│   ├── scripts/                  # JavaScript files
│   │   ├── api.js                # API communication
│   │   ├── game.js               # Game logic
│   │   └── ui.js                 # UI interactions
│   │
│   └── assets/                   # Images & icons
│
├── database/                     # Database scripts
│   ├── schema.sql                # PostgreSQL schema
│
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites
- **Python** 
- **PostgreSQL**
- **Git**
- **Unsplash API Key** ([Get one free](https://unsplash.com/developers))
```

### Database Setup
```bash
# Install PostgreSQL 

# Create database
createdb complete_me

# Run schema
psql complete_me < database/schema.sql
```

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your UNSPLASH_ACCESS_KEY

# Run server
python app.py
```

✅ Backend running at: `http://localhost:5000`

### 4. Frontend Setup
```bash
cd frontend

python -m http.server 8000
```

✅ Frontend running at: `http://localhost:8000`

---

## 📡 API Endpoints

### Authentication
```http
POST /api/register      # Create new account
POST /api/login         # Login & get JWT
POST /api/logout        # Logout
```

### Game Flow
```http
GET  /api/random-image                  # Fetch random image
GET  /api/category-image/<category>     # Fetch category image
POST /api/generate-puzzle               # Create puzzle with masking
POST /api/validate                      # Validate selected piece
GET  /api/hint                          # Get color-based hint
```

### User Management
```http
GET  /api/user/profile      # Get user profile
GET  /api/user/history      # Get game history
PUT  /api/user/avatar       # Update avatar
```
---

## 🔒 Security Features

### Authentication
- **JWT Tokens** - Dual-token architecture (access + refresh)
- **HTTP-Only Cookies** - Prevents XSS token theft
- **bcrypt Hashing** - Industry-standard password protection

### Input Protection
- **SQL Injection Prevention** - Parameterized queries
- **XSS Prevention** - Input sanitization
- **CSRF Protection** - Token-based validation

### Rate Limiting
- **Login Attempts** - Max 5 per 15 minutes
- **API Requests** - Max 50 per hour
- **Unsplash Alignment** - Respects free tier limits

### Content Safety
- **Child-Safe Filter** - All Unsplash requests use `content_filter=high`
- **Category Curation** - Pre-approved topic list
- **Input Validation** - Sanitized search queries

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_id INTEGER DEFAULT 1,
    total_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Game_History Table
```sql
CREATE TABLE game_history (
    game_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    image_url TEXT NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL,
    grid_size INTEGER NOT NULL,
    num_missing_pieces INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    score_earned INTEGER,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend && python app.py

# Frontend
cd frontend && python -m http.server 8000
```
---

## 👥 Authors

**Or Reshef S** 
**Gal Azoulay**
**Final Year Project** - Computer Science  

---

---

<p align="center">
  <strong>Made with ❤️ for children's learning and development</strong>
</p>

<p align="center">
  <sub>Computer Science Final Year Project</sub>
</p>

<p align="center">
  <a href="#-complete-me">Back to Top ↑</a>
</p>
