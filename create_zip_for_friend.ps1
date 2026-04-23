# ========================================
# Create ZIP for Friend - With .env files
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Creating Project ZIP for Friend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# נקי קבצים מיותרים
Write-Host "🧹 Step 1: Cleaning project..." -ForegroundColor Yellow
Write-Host ""

# מחק venv
if (Test-Path "backend\venv") {
    Remove-Item -Recurse -Force backend\venv
    Write-Host "   ✅ Deleted: backend\venv" -ForegroundColor Green
}

# מחק node_modules
if (Test-Path "frontend\node_modules") {
    Remove-Item -Recurse -Force frontend\node_modules
    Write-Host "   ✅ Deleted: frontend\node_modules" -ForegroundColor Green
}

# מחק __pycache__
Remove-Item -Recurse -Force backend\__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force backend\models\__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force backend\utils\__pycache__ -ErrorAction SilentlyContinue
Write-Host "   ✅ Deleted: __pycache__ folders" -ForegroundColor Green

# נקה temp folder
if (Test-Path "backend\static\temp\*") {
    Remove-Item backend\static\temp\* -ErrorAction SilentlyContinue
    Write-Host "   ✅ Cleaned: backend\static\temp" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Cleaning complete!" -ForegroundColor Green
Write-Host ""

# בדוק שיש .env files
Write-Host "🔍 Step 2: Checking .env files..." -ForegroundColor Yellow
Write-Host ""

$backendEnvExists = Test-Path "backend\.env"
$frontendEnvExists = Test-Path "frontend\.env"

if ($backendEnvExists) {
    Write-Host "   ✅ Found: backend\.env (will be included)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Warning: backend\.env not found!" -ForegroundColor Red
    Write-Host "      Your friend will need to create it manually" -ForegroundColor Yellow
}

if ($frontendEnvExists) {
    Write-Host "   ✅ Found: frontend\.env (will be included)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Warning: frontend\.env not found!" -ForegroundColor Red
    Write-Host "      Your friend will need to create it manually" -ForegroundColor Yellow
}

Write-Host ""

# יצירת ZIP
Write-Host "📦 Step 3: Creating ZIP file..." -ForegroundColor Yellow
Write-Host ""

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$zipName = "ai-puzzle-game-for-friend-$timestamp.zip"

# צור ZIP
Compress-Archive -Path . -DestinationPath "..\$zipName" -Force

Write-Host "✅ ZIP created successfully!" -ForegroundColor Green
Write-Host ""

# הצג מידע
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   📦 ZIP READY!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Location: $(Resolve-Path "..\$zipName")" -ForegroundColor White
Write-Host ""
Write-Host "📊 What's included:" -ForegroundColor Yellow
Write-Host "   ✅ All source code" -ForegroundColor Green
Write-Host "   ✅ .env files (with your API keys)" -ForegroundColor Green
Write-Host "   ✅ .env.example files" -ForegroundColor Green
Write-Host "   ✅ requirements.txt" -ForegroundColor Green
Write-Host "   ✅ package.json" -ForegroundColor Green
Write-Host "   ✅ All documentation (README, SETUP, etc.)" -ForegroundColor Green
Write-Host ""
Write-Host "❌ What's NOT included:" -ForegroundColor Yellow
Write-Host "   ❌ backend\venv (your friend will recreate)" -ForegroundColor Red
Write-Host "   ❌ frontend\node_modules (your friend will install)" -ForegroundColor Red
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   📧 INSTRUCTIONS FOR YOUR FRIEND" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Send this ZIP and tell your friend:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Extract to: C:\puzzle-game\" -ForegroundColor White
Write-Host "2. Backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python -m venv venv" -ForegroundColor Gray
Write-Host "   venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   pip install Flask Flask-CORS python-dotenv gunicorn tensorflow opencv-python scikit-image Pillow numpy scipy scikit-learn PyWavelets requests urllib3" -ForegroundColor Gray
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Frontend (new terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Ready to share!" -ForegroundColor Green
Write-Host ""