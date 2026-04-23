# AI Puzzle Game - Backend

## Overview

Flask-based REST API with advanced Computer Vision validation using TensorFlow, OpenCV, and multiple CV algorithms.

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Unsplash API keys:

- Get free API keys from: https://unsplash.com/developers
- Free tier: 50 requests per hour

### 3. Run Development Server

```bash
python app.py
```

Server will start at: `http://localhost:5000`

### 4. Run Production Server

```bash
gunicorn -c run.py app:app
```

## API Endpoints

### Health Check

```
GET /api/health
```

### Get Configuration

```
GET /api/config
```

### Create Puzzle

```
POST /api/puzzle/create
Content-Type: application/json

{
  "difficulty": 1-5,
  "use_random_image": true,
  "query": "nature" (optional)
}
```

### Validate Answer

```
POST /api/puzzle/validate
Content-Type: application/json

{
  "game_id": "uuid",
  "selected_index": 0-4,
  "selected_piece": "base64_image"
}
```

### Get Hint

```
POST /api/puzzle/hint
Content-Type: application/json

{
  "game_id": "uuid"
}
```

## Computer Vision Algorithms

### Validation Flow (every guess)

**Step 1 — Boundary ranking:** All 6 candidates scored by HSV histogram similarity to edge strips around the black square. User is correct if ranked #1.

**Step 2 — Comprehensive validation (always):** Runs on the user's piece every guess to produce the displayed confidence score.

| Algorithm             | Weight | Technique                               |
| --------------------- | ------ | --------------------------------------- |
| **Boundary**          | 35%    | HSV histogram boundary matching         |
| **Deep Feature (DL)** | 35%    | ResNet50 cosine similarity (PyTorch)    |
| **Color**             | 15%    | HSV histogram + K-Means dominant colors |
| **Texture**           | 10%    | LBP + GLCM                             |
| **Edge**              | 5%     | Canny / Sobel edge density              |

**Step 3 — Tiebreaker (when needed):** If the user's piece is within 0.02 of the top boundary score, comprehensive validation also runs on each competing piece to break the tie.

## Performance

| Step                   | Trigger                         | Speed                        |
| ---------------------- | ------------------------------- | ---------------------------- |
| Boundary ranking       | Every guess (all 6 candidates)  | < 1 sec                      |
| Comprehensive (x1)     | Every guess (user's piece)      | 2–4 sec                      |
| Comprehensive (x2+)    | Tie within 0.02 margin          | +2–4 sec per competing piece |

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
├── run.py               # Production runner
├── models/
│   ├── puzzle_generator.py
│   ├── image_processor.py
│   └── cv_validator.py
├── utils/
│   ├── feature_extraction.py
│   ├── color_analysis.py
│   ├── texture_analysis.py
│   ├── edge_detection.py
│   ├── semantic_analysis.py
│   └── unsplash_api.py
└── static/
    └── temp/            # Temporary files
```

## Testing

Run individual module tests:

```bash
python -m utils.feature_extraction
python -m utils.color_analysis
python -m utils.texture_analysis
python -m models.puzzle_generator
```

## Troubleshooting

### Unsplash API Issues

- Check your API key in `.env`
- Verify rate limits (50/hour free tier)
- System automatically falls back to generated images

### TensorFlow Issues

- Ensure TensorFlow 2.15+ is installed
- For CPU-only: `pip install tensorflow-cpu`
- For GPU support: Install CUDA + cuDNN

### Memory Issues

- Reduce image size in config
- Enable FAST_MODE
- Limit active_games storage

## License

Educational project for Computer Science final year
