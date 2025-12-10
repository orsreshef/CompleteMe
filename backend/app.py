"""
Main Flask Application
API endpoints for the puzzle game
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import cv2
import io
import base64
import os
import traceback
from PIL import Image

from config import get_config, Config
from models.puzzle_generator import PuzzleGenerator
from models.image_processor import ImageProcessor
from models.cv_validator import CVValidator, FastCVValidator
from utils.unsplash_api import UnsplashAPI


# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(get_config(env))

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
puzzle_generator = PuzzleGenerator()
image_processor = ImageProcessor()
unsplash_api = UnsplashAPI()

# Initialize validator based on config
if app.config['FAST_MODE']:
    validator = FastCVValidator()
    print("⚡ Using Fast Validator")
else:
    validator = CVValidator(
        use_ensemble=app.config['USE_ENSEMBLE_VALIDATION'],
        verbose=True
    )
    print("🎯 Using Comprehensive Validator")

# Storage for active games (in production, use Redis or database)
active_games = {}


def image_to_base64(image):
    """
    Convert numpy image to base64 string

    Args:
        image: numpy array (BGR)

    Returns:
        base64 encoded string
    """
    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Convert to PIL Image
    pil_image = Image.fromarray(image_rgb)

    # Save to bytes buffer
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)

    # Encode to base64
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return f"data:image/png;base64,{img_base64}"


def base64_to_image(base64_string):
    """
    Convert base64 string to numpy image

    Args:
        base64_string: base64 encoded image

    Returns:
        numpy array (BGR)
    """
    # Remove data URL prefix if present
    if 'base64,' in base64_string:
        base64_string = base64_string.split('base64,')[1]

    # Decode base64
    img_bytes = base64.b64decode(base64_string)

    # Convert to numpy array
    nparr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return image


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'message': 'AI Puzzle Game API is running',
        'version': '1.0.0',
        'unsplash_available': not unsplash_api.use_fallback
    }), 200


@app.route('/api/config', methods=['GET'])
def get_client_config():
    """
    Get configuration for the client
    """
    return jsonify({
        'difficulty_levels': Config.DIFFICULTY_LEVELS,
        'max_image_size': Config.MAX_IMAGE_DIMENSION,
        'decoy_count': Config.DECOY_COUNT,
        'validation_threshold': Config.VALIDATION_THRESHOLD
    }), 200


@app.route('/api/puzzle/create', methods=['POST'])
def create_puzzle():
    """
    Create a new puzzle game

    Request body (JSON):
    {
        "image": "base64_encoded_image" (optional),
        "difficulty": 1-5,
        "use_random_image": true/false
    }

    Returns:
    {
        "game_id": "unique_id",
        "puzzle_image": "base64_encoded",
        "options": ["base64_encoded", ...],
        "difficulty": {...},
        "message": "Puzzle created successfully"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get difficulty level
        difficulty = data.get('difficulty', 1)

        if difficulty not in Config.DIFFICULTY_LEVELS:
            return jsonify({'error': f'Invalid difficulty level: {difficulty}'}), 400

        # Get or generate image
        use_random = data.get('use_random_image', True)

        if use_random or 'image' not in data:
            # Use random image from Unsplash
            print("📸 Fetching random image from Unsplash...")
            image = unsplash_api.get_random_image(
                query=data.get('query', None),
                orientation='landscape'
            )

            if image is None:
                return jsonify({'error': 'Failed to fetch random image'}), 500

        else:
            # Use uploaded image
            print("📤 Using uploaded image...")
            image_data = data['image']
            image = base64_to_image(image_data)

            if image is None:
                return jsonify({'error': 'Invalid image data'}), 400

        # Create puzzle
        print(f"🎮 Creating puzzle with difficulty {difficulty}...")
        puzzle_data = puzzle_generator.create_puzzle(
            image, difficulty_level=difficulty)

        # Generate unique game ID
        import uuid
        game_id = str(uuid.uuid4())

        # Store game data
        active_games[game_id] = {
            'original_image': puzzle_data['original_image'],
            'missing_piece': puzzle_data['missing_piece'],
            'missing_position': puzzle_data['missing_position'],
            'correct_index': puzzle_data['correct_index'],
            'difficulty': difficulty,
            'attempts': 0
        }

        # Convert images to base64 for response
        puzzle_image_b64 = image_to_base64(puzzle_data['puzzle_image'])
        options_b64 = [image_to_base64(option)
                       for option in puzzle_data['options']]

        # Prepare response
        response = {
            'game_id': game_id,
            'puzzle_image': puzzle_image_b64,
            'options': options_b64,
            'difficulty': {
                'level': difficulty,
                'name': puzzle_data['difficulty_name'],
                'pieces': puzzle_data['num_pieces']
            },
            'grid': {
                'rows': puzzle_data['grid_rows'],
                'cols': puzzle_data['grid_cols']
            },
            'message': 'Puzzle created successfully!'
        }

        print(f"✅ Puzzle created with game_id: {game_id}")

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Error creating puzzle: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/puzzle/validate', methods=['POST'])
def validate_answer():
    """
    Validate user's answer using Computer Vision

    Request body (JSON):
    {
        "game_id": "unique_id",
        "selected_index": 0-4
    }

    Returns:
    {
        "is_correct": true/false,
        "confidence": 0.0-1.0,
        "validation_details": {...},
        "message": "Correct!" or "Try again!",
        "correct_index": (only if wrong)
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get game ID and selected index
        game_id = data.get('game_id')
        selected_index = data.get('selected_index')

        if not game_id or selected_index is None:
            return jsonify({'error': 'Missing game_id or selected_index'}), 400

        # Get game data
        if game_id not in active_games:
            return jsonify({'error': 'Invalid game_id or game expired'}), 404

        game_data = active_games[game_id]
        game_data['attempts'] += 1

        print(f"🔍 Validating answer for game {game_id}...")
        print(f"   Selected index: {selected_index}")
        print(f"   Attempt: {game_data['attempts']}")

        # Get the selected piece (need to recreate options to match index)
        # For now, we'll use CV validation instead of simple index matching

        # We need the selected piece image from client
        selected_piece_b64 = data.get('selected_piece')

        if not selected_piece_b64:
            return jsonify({'error': 'Missing selected_piece image'}), 400

        selected_piece = base64_to_image(selected_piece_b64)

        # Get original correct piece
        correct_piece = game_data['missing_piece']

        # Use Computer Vision to validate
        print("🤖 Running Computer Vision validation...")

        if app.config['FAST_MODE']:
            is_match, confidence = validator.validate(
                correct_piece, selected_piece)
            validation_details = {}
        else:
            is_match, confidence, validation_details = validator.validate_comprehensive(
                correct_piece,
                selected_piece
            )

        print(f"   Result: {'✅ CORRECT' if is_match else '❌ WRONG'}")
        print(f"   Confidence: {confidence:.3f}")

        # Prepare response
        response = {
            'is_correct': bool(is_match),
            'confidence': float(confidence),
            'attempt_number': game_data['attempts'],
            'validation_details': {
                'features_score': validation_details.get('features', {}).get('score', 0.0),
                'color_score': validation_details.get('color', {}).get('score', 0.0),
                'texture_score': validation_details.get('texture', {}).get('score', 0.0),
                'edge_score': validation_details.get('edges', {}).get('score', 0.0),
                'semantic_score': validation_details.get('semantic', {}).get('score', 0.0)
            }
        }

        if is_match:
            response['message'] = '🎉 Correct! Well done!'
            # Clean up game data after success
            # del active_games[game_id]  # Optional: keep for statistics
        else:
            response['message'] = '❌ Not quite right. Try again!'
            response['hint'] = self._generate_hint(
                confidence, validation_details)

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Error validating answer: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def _generate_hint(confidence, details):
    """
    Generate helpful hint based on validation results

    Args:
        confidence: overall confidence score
        details: detailed validation results

    Returns:
        hint string
    """
    if confidence > 0.60:
        return "You're close! Look more carefully at the colors and patterns."
    elif confidence > 0.40:
        return "That piece is somewhat similar, but not quite right."
    else:
        return "That piece is very different. Try another one!"


@app.route('/api/puzzle/hint', methods=['POST'])
def get_hint():
    """
    Get a hint for the puzzle

    Request body (JSON):
    {
        "game_id": "unique_id"
    }

    Returns:
    {
        "hint": "Hint message",
        "hint_type": "color/texture/position"
    }
    """
    try:
        data = request.get_json()
        game_id = data.get('game_id')

        if not game_id or game_id not in active_games:
            return jsonify({'error': 'Invalid game_id'}), 404

        game_data = active_games[game_id]
        missing_piece = game_data['missing_piece']

        # Analyze the missing piece
        avg_color = missing_piece.mean(axis=(0, 1))

        # Determine dominant color
        color_names = ['blue', 'green', 'red']
        dominant_color_idx = np.argmax(avg_color)
        dominant_color = color_names[dominant_color_idx]

        # Generate hint
        hints = [
            f"Look for a piece with more {dominant_color} tones.",
            "Try to match the colors around the missing area.",
            "Think about what would fit naturally in this spot."
        ]

        hint = hints[game_data['attempts'] % len(hints)]

        return jsonify({
            'hint': hint,
            'hint_type': 'color',
            'attempts': game_data['attempts']
        }), 200

    except Exception as e:
        print(f"❌ Error generating hint: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """
    Get game statistics

    Returns:
    {
        "active_games": 10,
        "total_validations": 100,
        "api_status": "healthy"
    }
    """
    return jsonify({
        'active_games': len(active_games),
        'unsplash_available': not unsplash_api.use_fallback,
        'validator_type': 'fast' if app.config['FAST_MODE'] else 'comprehensive',
        'api_status': 'healthy'
    }), 200


@app.route('/api/puzzle/cleanup', methods=['POST'])
def cleanup_game():
    """
    Clean up a finished game

    Request body (JSON):
    {
        "game_id": "unique_id"
    }
    """
    try:
        data = request.get_json()
        game_id = data.get('game_id')

        if game_id and game_id in active_games:
            del active_games[game_id]
            return jsonify({'message': 'Game cleaned up successfully'}), 200
        else:
            return jsonify({'message': 'Game not found or already cleaned up'}), 200

    except Exception as e:
        print(f"❌ Error cleaning up game: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🎮 AI Puzzle Game - Backend Server")
    print("=" * 60)
    print(f"Environment: {env}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print(
        f"Unsplash API: {'✅ Available' if not unsplash_api.use_fallback else '⚠️ Using Fallback'}")
    print(
        f"Validator: {'⚡ Fast Mode' if app.config['FAST_MODE'] else '🎯 Comprehensive Mode'}")
    print("=" * 60)
    print("\n🚀 Starting server...\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
