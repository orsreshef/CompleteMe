"""
Main Flask Application - UPDATED VERSION
API endpoints for the puzzle game with Boundary Matching
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
from models.cv_validator import CVValidator
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

# Initialize validator
validator = CVValidator()
print("🎯 Using Boundary Matching Validator")

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


def extract_boundary_colors(puzzle_image, missing_position, boundary_width=10):
    """
    Extract colors from the boundaries around the black square

    Args:
        puzzle_image: The image with black square
        missing_position: Dict with x, y, width, height
        boundary_width: How many pixels to analyze around the square

    Returns:
        dict: Average colors for each boundary (top, bottom, left, right)
    """
    x = missing_position['x']
    y = missing_position['y']
    w = missing_position['width']
    h = missing_position['height']

    boundaries = {}

    # Top boundary (above the black square)
    if y >= boundary_width:
        top_region = puzzle_image[y - boundary_width:y, x:x + w]
        boundaries['top'] = top_region.mean(axis=(0, 1))

    # Bottom boundary (below the black square)
    if y + h + boundary_width <= puzzle_image.shape[0]:
        bottom_region = puzzle_image[y + h:y + h + boundary_width, x:x + w]
        boundaries['bottom'] = bottom_region.mean(axis=(0, 1))

    # Left boundary (left of the black square)
    if x >= boundary_width:
        left_region = puzzle_image[y:y + h, x - boundary_width:x]
        boundaries['left'] = left_region.mean(axis=(0, 1))

    # Right boundary (right of the black square)
    if x + w + boundary_width <= puzzle_image.shape[1]:
        right_region = puzzle_image[y:y + h, x + w:x + w + boundary_width]
        boundaries['right'] = right_region.mean(axis=(0, 1))

    return boundaries


def get_dominant_color_name(bgr_color):
    """
    Convert BGR color values to a color name

    Args:
        bgr_color: [B, G, R] values

    Returns:
        str: Color name
    """
    b, g, r = bgr_color

    # Simple color classification
    if r > g and r > b:
        if r > 180:
            return "bright red"
        elif r > 120:
            return "red"
        else:
            return "dark red"
    elif g > r and g > b:
        if g > 180:
            return "bright green"
        elif g > 120:
            return "green"
        else:
            return "dark green"
    elif b > r and b > g:
        if b > 180:
            return "bright blue"
        elif b > 120:
            return "blue"
        else:
            return "dark blue"
    elif r > 150 and g > 150 and b < 100:
        return "yellow"
    elif r > 150 and g < 100 and b > 150:
        return "purple"
    elif r < 100 and g > 150 and b > 150:
        return "cyan"
    elif r > 180 and g > 180 and b > 180:
        return "white or light"
    elif r < 80 and g < 80 and b < 80:
        return "dark or black"
    else:
        return "mixed colors"


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'message': 'AI Puzzle Game API is running',
        'version': '2.0.0',  # Updated version
        'validator': 'boundary_matching',
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

        # Get number of missing regions
        num_regions = int(data.get('num_regions', 1))

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
        print(f"🎮 Creating puzzle with difficulty {difficulty}, {num_regions} region(s)...")
        puzzle_data = puzzle_generator.create_puzzle(
            image, difficulty_level=difficulty, num_regions=num_regions)

        # Generate unique game ID
        import uuid
        game_id = str(uuid.uuid4())

        # Store game data
        active_games[game_id] = {
            'puzzle_image': puzzle_data['puzzle_image'],
            'missing_positions': puzzle_data['missing_positions'],
            'num_regions': puzzle_data['num_regions'],
            'difficulty': difficulty,
            'attempts': 0
        }

        # Convert images to base64 for response
        puzzle_image_b64 = image_to_base64(puzzle_data['puzzle_image'])
        options_b64 = [image_to_base64(option)
                       for option in puzzle_data['options']]

        # Image dimensions (for frontend drop-zone overlay positioning)
        img_h, img_w = puzzle_data['puzzle_image'].shape[:2]

        # Prepare response
        response = {
            'game_id': game_id,
            'puzzle_image': puzzle_image_b64,
            'options': options_b64,
            'missing_positions': puzzle_data['missing_positions'],
            'image_dimensions': {'width': int(img_w), 'height': int(img_h)},
            'num_regions': puzzle_data['num_regions'],
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
    Validate user's answer using Boundary Matching + Computer Vision

    Request body (JSON):
    {
        "game_id": "unique_id",
        "placements": [
            {"zone_index": 0, "piece": "base64_encoded_image"},
            {"zone_index": 1, "piece": "base64_encoded_image"}
        ]
    }

    Returns:
    {
        "is_correct": true/false,
        "confidence": 0.0-1.0,
        "region_results": [...],
        "message": "Correct!" or "Try again!"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        game_id = data.get('game_id')
        placements = data.get('placements', [])

        if not game_id:
            return jsonify({'error': 'Missing game_id'}), 400
        if not placements:
            return jsonify({'error': 'Missing placements'}), 400

        if game_id not in active_games:
            return jsonify({'error': 'Invalid game_id or game expired'}), 404

        game_data = active_games[game_id]
        game_data['attempts'] += 1

        print(f"🔍 Validating {len(placements)} placement(s) for game {game_id}...")
        print(f"   Attempt: {game_data['attempts']}")

        puzzle_image = game_data['puzzle_image']
        missing_positions = game_data['missing_positions']

        region_results = []
        all_correct = True
        total_confidence = 0.0

        for placement in placements:
            zone_index = int(placement.get('zone_index', 0))
            placed_piece_b64 = placement.get('piece', '')

            if zone_index >= len(missing_positions):
                return jsonify({'error': f'Invalid zone_index: {zone_index}'}), 400

            placed_piece = base64_to_image(placed_piece_b64)
            missing_position = missing_positions[zone_index]

            print(f"   Zone {zone_index}: running CV + PyTorch validation...")

            is_match, confidence, details = validator.validate_comprehensive(
                puzzle_image,
                placed_piece,
                missing_position
            )

            print(f"   Zone {zone_index}: {'✅ CORRECT' if is_match else '❌ WRONG'} ({confidence:.3f})")

            region_results.append({
                'zone_index': zone_index,
                'is_correct': bool(is_match),
                'confidence': float(confidence),
                'validation_details': {
                    'boundary_score': float(details.get('boundary', {}).get('score', 0.0)),
                    'semantic_score': float(details.get('semantic', {}).get('score', 0.0)),
                    'color_score': float(details.get('color', {}).get('score', 0.0)),
                    'texture_score': float(details.get('texture', {}).get('score', 0.0)),
                    'edge_score': float(details.get('edges', {}).get('score', 0.0))
                }
            })

            if not is_match:
                all_correct = False
            total_confidence += confidence

        overall_confidence = total_confidence / len(placements)

        response = {
            'is_correct': all_correct,
            'confidence': float(overall_confidence),
            'region_results': region_results,
            'attempt_number': int(game_data['attempts'])
        }

        if all_correct:
            response['message'] = '🎉 Correct! Well done!'
        else:
            wrong = [r for r in region_results if not r['is_correct']]
            response['message'] = f'❌ {len(wrong)} piece(s) not quite right. Try again!'
            worst = min(wrong, key=lambda r: r['confidence'])
            response['hint'] = _generate_hint(worst['confidence'], {})

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
    # Check which aspect scored lowest
    boundary_score = details.get('boundary', {}).get('score', 0)
    color_score = details.get('color', {}).get('score', 0)

    if boundary_score < 0.5:
        return "The edges don't match well. Look at how the piece connects to the surrounding image."
    elif color_score < 0.5:
        return "The colors don't match. Look for a piece with similar colors to the surrounding area."
    elif confidence > 0.60:
        return "You're close! Look more carefully at the colors and patterns."
    elif confidence > 0.40:
        return "That piece is somewhat similar, but not quite right."
    else:
        return "That piece is very different. Try another one!"


@app.route('/api/puzzle/hint', methods=['POST'])
def get_hint():
    """
    Get a hint for the puzzle - UPDATED VERSION
    Analyzes the boundaries around the black square instead of the missing piece

    Request body (JSON):
    {
        "game_id": "unique_id"
    }

    Returns:
    {
        "hint": "Hint message",
        "hint_type": "boundary/color/position",
        "boundary_info": {...}
    }
    """
    try:
        data = request.get_json()
        game_id = data.get('game_id')

        if not game_id or game_id not in active_games:
            return jsonify({'error': 'Invalid game_id'}), 404

        game_data = active_games[game_id]

        # Get puzzle image and missing position
        puzzle_image = game_data['puzzle_image']
        missing_position = game_data['missing_position']
        attempts = game_data['attempts']

        # Extract boundary colors
        boundaries = extract_boundary_colors(
            puzzle_image, missing_position, boundary_width=10)

        if not boundaries:
            # Fallback to generic hints if no boundaries available
            hint = "Think about what would fit naturally in this spot."
            hint_type = "generic"
            boundary_info = {}
        else:
            # Calculate average color across all boundaries
            all_boundary_colors = np.array(list(boundaries.values()))
            avg_boundary_color = all_boundary_colors.mean(axis=0)

            # Get dominant color name
            dominant_color = get_dominant_color_name(avg_boundary_color)

            # Find which boundary has the most distinct color
            boundary_variances = {}
            for direction, color in boundaries.items():
                variance = np.std(color)
                boundary_variances[direction] = variance

            most_distinct_boundary = max(
                boundary_variances, key=boundary_variances.get)
            distinct_color = get_dominant_color_name(
                boundaries[most_distinct_boundary])

            # Generate hint based on attempts
            hints = [
                f"Look for a piece that matches the surrounding colors - especially {dominant_color} tones.",
                f"Pay attention to the {most_distinct_boundary} edge - it has {distinct_color} colors.",
                "Try to match the colors and patterns around the missing area.",
                f"The piece should blend with the {dominant_color} colors around the black square.",
                "Look at how the surrounding image connects - what would complete this naturally?"
            ]

            # Rotate through hints based on attempts
            hint = hints[attempts % len(hints)]
            hint_type = "boundary"

            # Prepare boundary info for response
            boundary_info = {
                'dominant_color': dominant_color,
                'most_distinct_boundary': most_distinct_boundary,
                'distinct_color': distinct_color
            }

        return jsonify({
            'hint': hint,
            'hint_type': hint_type,
            'boundary_info': boundary_info,
            'attempts': attempts
        }), 200

    except Exception as e:
        print(f"❌ Error generating hint: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """
    Get game statistics

    Returns:
    {
        "active_games": 10,
        "validator_type": "boundary_matching",
        "api_status": "healthy"
    }
    """
    return jsonify({
        'active_games': len(active_games),
        'unsplash_available': not unsplash_api.use_fallback,
        'validator_type': 'boundary_matching',
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
    print("🎮 AI Puzzle Game - Backend Server v2.0")
    print("=" * 60)
    print(f"Environment: {env}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print(
        f"Unsplash API: {'✅ Available' if not unsplash_api.use_fallback else '⚠️ Using Fallback'}")
    print(f"Validator: 🎯 Boundary Matching (PyTorch + CV)")
    print("=" * 60)
    print("\n🚀 Starting server...\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
