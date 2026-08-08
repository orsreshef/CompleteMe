# Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- An [Unsplash API key](https://unsplash.com/developers) (free)

---

## Windows: Use a Short Path

PyTorch/torchvision can fail to install when the project path is too long. Clone or move the project to a short path before starting:

```
C:\puzzle-game\
```

---

## Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate        # Mac/Linux

# Install dependencies (~5-10 min)
python -m pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
copy .env.example .env            # Windows
# cp .env.example .env            # Mac/Linux
```

Edit `backend/.env` and fill in:

```
SECRET_KEY=          # run: python -c "import secrets; print(secrets.token_hex(32))"
UNSPLASH_ACCESS_KEY= # from https://unsplash.com/developers
```

Start the backend:

```bash
python app.py
# Running on http://localhost:5000
```

---

## Frontend

Open a second terminal:

```bash
cd frontend
npm install

copy .env.example .env            # Windows
# cp .env.example .env            # Mac/Linux

npm start
# Opens http://localhost:3000
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'torch'`**
Make sure the virtual environment is activated — you should see `(venv)` in your prompt.

**PyTorch/torchvision install fails on Windows (`OSError: No such file or directory`)**
Path is too long. Move the project to `C:\puzzle-game\`, delete `backend\venv\`, and reinstall.

**Port already in use**
```bash
# Windows — find and kill the process:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```
