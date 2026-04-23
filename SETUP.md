# 🚀 Quick Setup Guide

Get the AI Puzzle Game running in **15 minutes**!

## ✅ Prerequisites Check

Before starting, verify you have:

```bash
# Check Python (need 3.8+)
python --version

# Check Node.js (need 16+)
node --version

# Check npm
npm --version

# Check git
git --version
```

---

## 🚨 Windows Users - Read This First!

**Important:** This project uses TensorFlow which requires a **short directory path** on Windows.

### ✅ Recommended Installation Path:

```bash
C:\puzzle-game\
```

### ❌ Avoid Long Paths:

```bash
C:\Users\Name\Documents\University\Year3\Semester1\FinalProject\AI\puzzle-game\
```

### Why?

Windows has a 260-character path limit. TensorFlow's deep folder structure can exceed this limit, causing installation failures.

### If Installation Fails:

1. Move the project to `C:\puzzle-game\`
2. Delete the `backend\venv\` folder
3. Recreate virtual environment
4. Install dependencies again

---

## 📥 Step 1: Get the Code

```bash
# Clone repository
git clone https://github.com/yourusername/ai-puzzle-game.git

# Move to a short path (Windows users - IMPORTANT!)
# Option 1: Move to C:\
move ai-puzzle-game C:\puzzle-game
cd C:\puzzle-game

# Option 2: If you don't have admin rights
move ai-puzzle-game C:\Users\YourName\puzzle-game
cd C:\Users\YourName\puzzle-game

# Mac/Linux users - no need to move, just cd:
cd ai-puzzle-game
```

---

## 🐍 Step 2: Backend Setup (10 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows PowerShell:
venv\Scripts\Activate.ps1

# On Windows CMD:
venv\Scripts\activate.bat

# On Mac/Linux:
source venv/bin/activate

# You should see (venv) at the start of your prompt
```

### Install Dependencies

**⚠️ Important: Use direct installation (NOT requirements.txt on first install)**

```bash
# Update pip first
python -m pip install --upgrade pip setuptools wheel

# Install all dependencies (this takes 5-10 minutes ☕)
pip install Flask Flask-CORS python-dotenv gunicorn tensorflow opencv-python scikit-image Pillow numpy scipy scikit-learn PyWavelets requests urllib3
```

**Why not requirements.txt?** Some versions in requirements.txt may not work on all systems. Direct installation lets pip choose compatible versions.

### Configure Environment Variables

```bash
# Copy the example file
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env

# Open .env for editing
# Windows:
notepad .env

# Mac/Linux:
nano .env
```

**Edit `.env` and add your keys:**

```bash
# Required:
SECRET_KEY=your_secret_key_here_change_this
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here

# Optional (can leave as is):
UNSPLASH_SECRET_KEY=your_unsplash_secret_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

**How to get SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**How to get UNSPLASH_ACCESS_KEY:**

1. Go to: https://unsplash.com/developers
2. Sign up / Log in
3. Create a New Application
4. Copy your **Access Key**
5. Paste it in `.env`

**Free tier:** 50 requests per hour (enough for development!)

### Generate requirements.txt (for future use)

```bash
# After successful installation, create requirements.txt
pip freeze > requirements.txt
```

### Start Backend

```bash
python app.py
```

**You should see:**

```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

✅ **Backend is running!** Leave this terminal open.

---

## ⚛️ Step 3: Frontend Setup (5 minutes)

**⚠️ Open a NEW terminal window** (don't close the backend terminal!)

```bash
# Navigate to frontend directory
cd frontend

# Or if you're starting fresh:
cd C:\puzzle-game\frontend  # Windows
cd /path/to/puzzle-game/frontend  # Mac/Linux

# Install dependencies (this takes 2-3 minutes)
npm install
```

**You may see warnings like:**

```
npm warn deprecated ...
9 vulnerabilities (3 moderate, 6 high)
```

**This is normal!** These are just warnings about old packages. The project will work fine.

**❌ DO NOT run `npm audit fix --force`** - this may break the project!

### Configure Environment

```bash
# Copy the example file
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env
```

**The default `.env` should work as-is:**

```bash
REACT_APP_API_URL=http://localhost:5000/api
NODE_ENV=development
```

### Start Frontend

```bash
npm start
```

**The browser should open automatically to `http://localhost:3000`**

✅ **Frontend is running!**

---

## 🎮 Step 4: Play!

1. **Browser opens automatically** to `http://localhost:3000`
2. **Select a difficulty level** (Start with Beginner!)
3. **Wait for puzzle to generate** (5-10 seconds)
4. **Study the image** with the black square
5. **Select the piece** you think fits
6. **Click "Check Answer"**
7. **Watch the AI validate** your choice with confidence scores!

---

## 🛑 How to Stop the Servers

### In each terminal, press:

```
Ctrl + C
```

**Frontend may ask:** `Terminate batch job (Y/N)?`

- Type `Y` and press Enter

---

## 🔄 How to Start Again Later

### Backend (Terminal 1):

```bash
cd C:\puzzle-game\backend
venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate  # Mac/Linux
python app.py
```

### Frontend (Terminal 2):

```bash
cd C:\puzzle-game\frontend
npm start
```

---

## 🆘 Troubleshooting

### ❌ Backend: `ModuleNotFoundError: No module named 'tensorflow'`

**Solution:**

```bash
# Make sure venv is activated (you should see (venv) in prompt)
venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate  # Mac/Linux

# If still not working, reinstall:
pip install tensorflow
```

---

### ❌ Backend: `OSError: No such file or directory` (TensorFlow installation)

**Cause:** Path is too long (Windows)

**Solution:**

1. Move project to shorter path: `C:\puzzle-game\`
2. Delete `venv` folder
3. Recreate venv and reinstall dependencies

```bash
cd C:\puzzle-game\backend
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install Flask Flask-CORS python-dotenv gunicorn tensorflow opencv-python scikit-image Pillow numpy scipy scikit-learn PyWavelets requests urllib3
```

---

### ❌ Backend: `No module named 'models.feature_extraction'`

**Cause:** Import paths are incorrect

**Solution:** Edit `backend/models/cv_validator.py`

Change lines 8-12 from:

```python
from .feature_extraction import FeatureExtractor, MultiModelFeatureExtractor
from .color_analysis import ColorAnalyzer
from .texture_analysis import TextureAnalyzer
from .edge_detection import EdgeAnalyzer
from .semantic_analysis import SemanticAnalyzer
```

To:

```python
from utils.feature_extraction import FeatureExtractor, MultiModelFeatureExtractor
from utils.color_analysis import ColorAnalyzer
from utils.texture_analysis import TextureAnalyzer
from utils.edge_detection import EdgeAnalyzer
from utils.semantic_analysis import SemanticAnalyzer
```

---

### ❌ Backend: Port 5000 already in use

```bash
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

---

### ❌ Frontend: Port 3000 already in use

React will ask: `Would you like to run the app on another port instead?`

- Type `Y` and press Enter

Or kill the process:

```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
```

---

### ❌ Frontend: `npm install` fails

```bash
# Clear cache and try again
npm cache clean --force
rm -rf node_modules package-lock.json  # Mac/Linux
Remove-Item -Recurse -Force node_modules, package-lock.json  # Windows PowerShell
npm install
```

---

### ❌ VS Code shows import warnings (yellow squiggly lines)

**Example:** `Import "numpy" could not be resolved`

**Cause:** VS Code doesn't know where your venv is

**Solution:**

1. Press `Ctrl + Shift + P`
2. Type: `Python: Select Interpreter`
3. Choose: `.\venv\Scripts\python.exe` (or Python with 'venv')

**Note:** This doesn't affect the code running - it's just a VS Code display issue.

---

### ❌ Unsplash API not working / Rate limit

**Without API key:** The system uses fallback generated images automatically.

**With API key:**

- Free tier: 50 requests/hour
- If you hit the limit, wait an hour or use fallback images

---

## 📊 Verify Installation

### Check Backend:

```bash
cd backend
venv\Scripts\Activate.ps1  # Windows
python -c "import tensorflow, cv2, flask, numpy, scipy; print('✅ All packages work!')"
```

### Check Frontend:

```bash
cd frontend
npm list react react-dom
```

---

## 🎯 Quick Reference

### Daily Workflow:

**1. Start Backend (Terminal 1):**

```bash
cd C:\puzzle-game\backend
venv\Scripts\Activate.ps1
python app.py
```

**2. Start Frontend (Terminal 2):**

```bash
cd C:\puzzle-game\frontend
npm start
```

**3. Stop Both:**

- Press `Ctrl + C` in each terminal

---

## 📁 Project Structure

```
puzzle-game/
├── backend/           # Python/Flask backend
│   ├── venv/         # Virtual environment (you create this)
│   ├── models/       # Core logic
│   ├── utils/        # CV algorithms
│   ├── .env          # Your API keys (you create this)
│   └── app.py        # Main backend file
│
└── frontend/         # React frontend
    ├── node_modules/ # Dependencies (npm creates this)
    ├── src/          # React components
    ├── .env          # Configuration (you create this)
    └── package.json  # Dependencies list
```

---

## 🔑 Required Files You Must Create

1. ✅ `backend/.env` - Copy from `.env.example` and add keys
2. ✅ `frontend/.env` - Copy from `.env.example` (default works)
3. ✅ `backend/venv/` - Created with `python -m venv venv`
4. ✅ `frontend/node_modules/` - Created with `npm install`

---

## 📞 Need More Help?

- 📖 Read the full [README.md](README.md) for project details
- 🚀 Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- 📋 See [CHECKLIST.md](CHECKLIST.md) to verify everything works
- 🐛 Create an issue on GitHub
- 📧 Contact: your.email@example.com

---

## 🎓 For Instructors/Reviewers

### Quick Test Run:

```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\Activate.ps1
python app.py

# Terminal 2 - Frontend
cd frontend
npm start

# Browser opens to http://localhost:3000
# Try creating a puzzle at Beginner level
```

### Expected Behavior:

- Backend starts on port 5000 without errors
- Frontend opens browser on port 3000
- Can select difficulty and generate puzzle
- Can select piece and get AI validation with confidence scores

---

**Made with ❤️ for educational purposes**

**Happy Puzzling! 🧩**
