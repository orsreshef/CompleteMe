"""Flask application — API endpoints for the AI puzzle game."""

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
from extensions import db, jwt, bcrypt, limiter
from models.puzzle_generator import PuzzleGenerator
from models.image_processor import ImageProcessor
from models.cv_validator import CVValidator
from utils.unsplash_api import UnsplashAPI
from routes.auth import auth_bp


app = Flask(__name__)

env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(get_config(env))

db.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)
limiter.init_app(app)

# credentials=True is required for HTTP-only JWT cookies
CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

app.register_blueprint(auth_bp)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    from models.user import User  # noqa: F401
    from models.game_history import GameHistory  # noqa: F401
    db.create_all()
    print("✅ Database tables ready")

puzzle_generator = PuzzleGenerator()
image_processor = ImageProcessor()
unsplash_api = UnsplashAPI()

validator = CVValidator()
print("🎯 Using Boundary Matching Validator")

# In production, replace with Redis or a database
active_games = {}


def image_to_base64(image):
    """Convert a BGR numpy image to a base64-encoded PNG data URL."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"


def base64_to_image(base64_string):
    """Decode a base64 image string (with or without data URL prefix) to a BGR numpy array."""
    if 'base64,' in base64_string:
        base64_string = base64_string.split('base64,')[1]
    img_bytes = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


def extract_boundary_colors(puzzle_image, missing_position, boundary_width=10):
    """Extract average BGR colors from the four pixel strips surrounding the hole."""
    x = missing_position['x']
    y = missing_position['y']
    w = missing_position['width']
    h = missing_position['height']

    boundaries = {}

    if y >= boundary_width:
        boundaries['top'] = puzzle_image[y - boundary_width:y, x:x + w].mean(axis=(0, 1))

    if y + h + boundary_width <= puzzle_image.shape[0]:
        boundaries['bottom'] = puzzle_image[y + h:y + h + boundary_width, x:x + w].mean(axis=(0, 1))

    if x >= boundary_width:
        boundaries['left'] = puzzle_image[y:y + h, x - boundary_width:x].mean(axis=(0, 1))

    if x + w + boundary_width <= puzzle_image.shape[1]:
        boundaries['right'] = puzzle_image[y:y + h, x + w:x + w + boundary_width].mean(axis=(0, 1))

    return boundaries


def get_dominant_color_name(bgr_color):
    """Map a BGR color vector to a human-readable color name string."""
    b, g, r = bgr_color

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


def _get_piece_color_description(bgr_image):
    """Returns (color_name, saturation_desc, brightness_desc) for a BGR image."""
    hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
    avg_h = float(hsv[:, :, 0].mean())
    avg_s = float(hsv[:, :, 1].mean())
    avg_v = float(hsv[:, :, 2].mean())

    if avg_s < 40:
        color = "white" if avg_v > 180 else ("dark gray" if avg_v < 60 else "gray")
    elif avg_h < 10 or avg_h >= 160:
        color = "red"
    elif avg_h < 22:
        color = "brown" if avg_s < 160 and avg_v < 170 else "orange"
    elif avg_h < 33:
        color = "yellow"
    elif avg_h < 85:
        color = "green"
    elif avg_h < 130:
        color = "blue"
    elif avg_h < 160:
        color = "purple"
    else:
        color = "red"

    sat = "muted" if avg_s < 40 else ("soft" if avg_s < 120 else "vivid")
    brightness = "dark" if avg_v < 80 else ("bright" if avg_v > 180 else "")

    return color, sat, brightness


def _get_piece_texture_description(bgr_image):
    """Returns a texture description string based on pixel variance."""
    gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    std = float(np.std(gray))
    if std < 15:
        return "smooth and uniform"
    elif std < 40:
        return "lightly textured"
    else:
        return "rough and detailed"


def _build_visual_hint(piece_image):
    """Generates a natural-language hint describing a piece's visual appearance."""
    color, sat, brightness = _get_piece_color_description(piece_image)
    texture = _get_piece_texture_description(piece_image)
    color_phrase = f"{brightness}, {sat} {color}" if brightness else f"{sat} {color}"
    return f"Look for a piece with {color_phrase} tones and a {texture} appearance."


@app.route('/api/health', methods=['GET'])
def health_check():
    """Return API health status."""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Puzzle Game API is running',
        'version': '2.0.0',
        'validator': 'boundary_matching',
        'unsplash_available': not unsplash_api.use_fallback
    }), 200


@app.route('/api/config', methods=['GET'])
def get_client_config():
    """Return puzzle configuration constants for the frontend."""
    return jsonify({
        'difficulty_levels': Config.DIFFICULTY_LEVELS,
        'max_image_size': Config.MAX_IMAGE_DIMENSION,
        'decoy_count': Config.DECOY_COUNT,
        'validation_threshold': Config.VALIDATION_THRESHOLD
    }), 200


@app.route('/api/puzzle/create', methods=['POST'])
def create_puzzle():
    """Create a new puzzle game from an uploaded or random Unsplash image.
    Returns game_id, puzzle_image (base64), piece options, and layout metadata."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        difficulty = data.get('difficulty', 1)

        if difficulty not in Config.DIFFICULTY_LEVELS:
            return jsonify({'error': f'Invalid difficulty level: {difficulty}'}), 400

        num_regions = int(data.get('num_regions', 1))

        use_random = data.get('use_random_image', True)
        fetched_url = ''
        prefetched_decoys = None

        if use_random or 'image' not in data:
            print("Fetching main image and decoys in parallel from Unsplash...")
            image, fetched_url, prefetched_decoys = puzzle_generator.prefetch_all_images(
                query=data.get('query', None),
                difficulty_level=difficulty,
                num_regions=num_regions
            )

            if image is None:
                return jsonify({'error': 'Failed to fetch random image'}), 500

        else:
            print("Using uploaded image...")
            image_data = data['image']
            image = base64_to_image(image_data)

            if image is None:
                return jsonify({'error': 'Invalid image data'}), 400

        print(f"Creating puzzle with difficulty {difficulty}, {num_regions} region(s)...")
        puzzle_data = puzzle_generator.create_puzzle(
            image, difficulty_level=difficulty, num_regions=num_regions,
            prefetched_decoys=prefetched_decoys)

        import uuid
        game_id = str(uuid.uuid4())

        active_games[game_id] = {
            'puzzle_image': puzzle_data['puzzle_image'],
            'missing_positions': puzzle_data['missing_positions'],
            'num_regions': puzzle_data['num_regions'],
            'difficulty': difficulty,
            'attempts': 0,
            'options': puzzle_data['options'],
            'image_url': fetched_url or data.get('image_url', ''),
            'grid_size': puzzle_data.get('num_pieces', 0),
            'difficulty_name': puzzle_data.get('difficulty_name', '')
        }

        puzzle_image_b64 = image_to_base64(puzzle_data['puzzle_image'])
        options_b64 = [image_to_base64(option) for option in puzzle_data['options']]

        img_h, img_w = puzzle_data['puzzle_image'].shape[:2]

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

        print(f"Puzzle created with game_id: {game_id}")
        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Error creating puzzle: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/puzzle/validate', methods=['POST'])
def validate_answer():
    """Validate piece placements using relative boundary ranking across all 6 candidates.
    A placement is correct when the selected piece ranks #1; ties are broken by comprehensive CV scoring."""
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
        print(f"Validating {len(placements)} placement(s) for game {game_id}, attempt {game_data['attempts']}...")

        puzzle_image = game_data['puzzle_image']
        missing_positions = game_data['missing_positions']

        region_results = []
        all_correct = True
        total_confidence = 0.0

        all_options = game_data['options']

        for placement in placements:
            zone_index = int(placement.get('zone_index', 0))
            option_index = int(placement.get('option_index', 0))

            if zone_index >= len(missing_positions):
                return jsonify({'error': f'Invalid zone_index: {zone_index}'}), 400
            if option_index >= len(all_options):
                return jsonify({'error': f'Invalid option_index: {option_index}'}), 400

            placed_piece = all_options[option_index]
            missing_position = missing_positions[zone_index]

            # Score every candidate against this zone; the user wins if they rank #1.
            # TIE_MARGIN handles uniform-colour regions (white walls, clear sky) where
            # boundary scores cluster — comprehensive scoring then breaks the tie.
            TIE_MARGIN = 0.02

            option_boundary_scores = []
            for opt in all_options:
                _, opt_conf, _ = validator.boundary_matcher.validate_piece_placement(
                    puzzle_image, opt, missing_position
                )
                option_boundary_scores.append(opt_conf)

            user_boundary_score = option_boundary_scores[option_index]
            best_boundary_score = max(option_boundary_scores)
            rank = sum(1 for s in option_boundary_scores if s > user_boundary_score) + 1

            _, confidence, details = validator.validate_comprehensive(
                puzzle_image, placed_piece, missing_position
            )

            if rank == 1:
                is_match = True
            elif best_boundary_score - user_boundary_score <= TIE_MARGIN:
                competing_indices = [
                    i for i, s in enumerate(option_boundary_scores)
                    if s > user_boundary_score
                ]
                best_competing_conf = 0.0
                for comp_idx in competing_indices:
                    _, comp_conf, _ = validator.validate_comprehensive(
                        puzzle_image, all_options[comp_idx], missing_position
                    )
                    best_competing_conf = max(best_competing_conf, comp_conf)
                is_match = (confidence >= best_competing_conf)
                print(f"  Zone {zone_index}: TIE resolved - user {confidence:.3f} vs competitor {best_competing_conf:.3f} -> {'CORRECT' if is_match else 'WRONG'}")
            else:
                is_match = False

            print(f"  Zone {zone_index}: {'CORRECT' if is_match else 'WRONG'} (rank {rank}, conf {confidence:.3f})")
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

        if all_correct:
            try:
                from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                if user_id:
                    from models.user import User
                    from models.game_history import GameHistory
                    score_earned = max(10, 100 - (game_data['attempts'] - 1) * 10)
                    history_entry = GameHistory(
                        user_id=int(user_id),
                        image_url=game_data.get('image_url', ''),
                        difficulty_level=game_data.get('difficulty_name', str(game_data['difficulty'])),
                        grid_size=game_data.get('grid_size', 0),
                        num_missing_pieces=game_data['num_regions'],
                        success=True,
                        score_earned=score_earned
                    )
                    db.session.add(history_entry)
                    user = User.query.get(int(user_id))
                    if user:
                        user.total_score += score_earned
                    db.session.commit()
                    print(f"✅ Game saved to history for user {user_id} (+{score_earned} pts)")
            except Exception as hist_err:
                print(f"⚠️ Could not save game history: {hist_err}")

        score_earned = max(10, 100 - (game_data['attempts'] - 1) * 10) if all_correct else 0

        response = {
            'is_correct': all_correct,
            'confidence': float(overall_confidence),
            'region_results': region_results,
            'attempt_number': int(game_data['attempts']),
            'score_earned': score_earned,
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
    """Return a hint string based on boundary and color scores from the validation details."""
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
    """Return a visual hint for the missing zone using ResNet50 similarity, with a color-based fallback."""
    try:
        data = request.get_json()
        game_id = data.get('game_id')

        if not game_id or game_id not in active_games:
            return jsonify({'error': 'Invalid game_id'}), 404

        game_data = active_games[game_id]
        puzzle_image = game_data['puzzle_image']
        zone_index = int(data.get('zone_index', 0))
        missing_positions = game_data['missing_positions']
        if zone_index >= len(missing_positions):
            zone_index = 0
        missing_position = missing_positions[zone_index]
        options = game_data['options']

        if validator.has_deep_learning and validator.feature_extractor and options:
            try:
                margin = max(50, min(150, missing_position['height'], missing_position['width']))
                context_region = validator._extract_context_region(
                    puzzle_image, missing_position, margin=margin
                )
                ctx_features = validator.feature_extractor.extract_features(context_region)

                best_score = -1.0
                best_piece = None
                for option_img in options:
                    piece_features = validator.feature_extractor.extract_features(option_img)
                    score = validator.feature_extractor.compare_features(
                        ctx_features, piece_features, method='cosine'
                    )
                    if score > best_score:
                        best_score = score
                        best_piece = option_img

                if best_piece is not None:
                    hint = _build_visual_hint(best_piece)
                    return jsonify({'hint': hint, 'hint_type': 'dl_visual'}), 200

            except Exception as e:
                print(f"⚠️ DL hint failed, falling back to boundary analysis: {e}")

        boundaries = extract_boundary_colors(puzzle_image, missing_position, boundary_width=10)

        if not boundaries:
            hint = "Think about what would fit naturally in this spot."
        else:
            all_boundary_colors = np.array(list(boundaries.values()))
            avg_boundary_color = all_boundary_colors.mean(axis=0)
            dominant_color = get_dominant_color_name(avg_boundary_color)
            boundary_variances = {d: np.std(c) for d, c in boundaries.items()}
            most_distinct = max(boundary_variances, key=boundary_variances.get)
            distinct_color = get_dominant_color_name(boundaries[most_distinct])
            attempts = game_data['attempts']
            hints = [
                f"Look for a piece that matches the surrounding colors - especially {dominant_color} tones.",
                f"Pay attention to the {most_distinct} edge - it has {distinct_color} colors.",
                "Try to match the colors and patterns around the missing area.",
                f"The piece should blend with the {dominant_color} colors around the black square.",
                "Look at how the surrounding image connects - what would complete this naturally?"
            ]
            hint = hints[attempts % len(hints)]

        return jsonify({'hint': hint, 'hint_type': 'boundary'}), 200

    except Exception as e:
        print(f"❌ Error generating hint: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Return aggregate game statistics."""
    return jsonify({
        'active_games': len(active_games),
        'unsplash_available': not unsplash_api.use_fallback,
        'validator_type': 'boundary_matching',
        'api_status': 'healthy'
    }), 200


@app.route('/api/puzzle/cleanup', methods=['POST'])
def cleanup_game():
    """Remove a finished game from active_games to free memory."""
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
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🎮 AI Puzzle Game - Backend Server v2.0")
    print("=" * 60)
    print(f"Environment: {env}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print(f"Unsplash API: {'✅ Available' if not unsplash_api.use_fallback else '⚠️ Using Fallback'}")
    print(f"Validator: 🎯 Boundary Matching (PyTorch + CV)")
    print("=" * 60)
    print("\n🚀 Starting server...\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
