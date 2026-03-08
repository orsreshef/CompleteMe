"""
Puzzle Generator Module
Handles creation of puzzle pieces and game setup
"""

import numpy as np
import cv2
import random
from utils.unsplash_api import UnsplashAPI
from models.image_processor import ImageProcessor
from config import Config


class PuzzleGenerator:
    """
    Class for generating puzzle games
    """

    def __init__(self):
        """Initialize puzzle generator"""
        self.image_processor = ImageProcessor()
        self.unsplash_api = UnsplashAPI()
        print("✅ Puzzle Generator initialized")

    def create_puzzle(self, image, difficulty_level=1, num_regions=1):
        """
        Create a complete puzzle game from an image.

        Args:
            image: input image (numpy array or file path)
            difficulty_level: 1-5 (1=easiest, 5=hardest)
            num_regions: how many pieces to hide (black squares), 1-4

        Returns:
            dict: complete puzzle data
        """
        # Load image if path provided
        if isinstance(image, str):
            image = self.image_processor.load_image(image)

        # Validate difficulty level
        if difficulty_level not in Config.DIFFICULTY_LEVELS:
            raise ValueError(f"Invalid difficulty level: {difficulty_level}")

        difficulty_info = Config.DIFFICULTY_LEVELS[difficulty_level]
        num_pieces = difficulty_info['pieces']

        # Clamp num_regions: at least 1, at most 4, never >= total pieces
        num_regions = max(1, min(int(num_regions), 4, num_pieces - 1))

        print(f"🎮 Creating puzzle: {difficulty_info['name']} ({num_pieces} pieces, {num_regions} missing)")

        # Resize image to standard size
        image = self.image_processor.resize_image(
            image,
            max_size=Config.MAX_IMAGE_DIMENSION,
            maintain_aspect=True
        )

        # Calculate grid dimensions
        grid_rows, grid_cols = self._calculate_grid_dimensions(num_pieces)

        # Split image into pieces
        pieces = self._split_image_into_pieces(image, grid_rows, grid_cols)

        piece_height = image.shape[0] // grid_rows
        piece_width = image.shape[1] // grid_cols

        # Select num_regions unique random piece indices to hide
        missing_indices = random.sample(range(len(pieces)), num_regions)

        missing_pieces = []
        missing_positions = []
        puzzle_image = image.copy()

        for missing_index in missing_indices:
            missing_row = missing_index // grid_cols
            missing_col = missing_index % grid_cols

            pos = {
                'x': missing_col * piece_width,
                'y': missing_row * piece_height,
                'width': piece_width,
                'height': piece_height,
                'row': missing_row,
                'col': missing_col,
                'index': missing_index
            }
            missing_positions.append(pos)
            missing_pieces.append(pieces[missing_index])

            # Paint that region black
            puzzle_image = self.image_processor.create_black_square(
                puzzle_image,
                pos['x'], pos['y'],
                pos['width'], pos['height']
            )

        # Pool always has 6 pieces: num_regions correct + (6 - num_regions) decoys
        decoy_count = max(6 - num_regions, 2)
        decoy_pieces = self._generate_decoy_pieces(
            piece_width, piece_height,
            count=decoy_count,
            difficulty_level=difficulty_level
        )

        # Combine and shuffle
        all_options = missing_pieces + decoy_pieces
        random.shuffle(all_options)

        # Map each correct piece to its index in the shuffled pool
        correct_indices = []
        used = set()
        for correct_piece in missing_pieces:
            for idx, option in enumerate(all_options):
                if idx not in used and np.array_equal(option, correct_piece):
                    correct_indices.append(idx)
                    used.add(idx)
                    break

        puzzle_data = {
            'original_image': image,
            'puzzle_image': puzzle_image,
            # Multi-region fields
            'missing_pieces': missing_pieces,
            'missing_positions': missing_positions,
            'correct_indices': correct_indices,
            'num_regions': num_regions,
            # Single-region backward-compat aliases
            'missing_piece': missing_pieces[0],
            'missing_position': missing_positions[0],
            'correct_index': correct_indices[0] if correct_indices else None,
            # Meta
            'options': all_options,
            'difficulty_level': difficulty_level,
            'difficulty_name': difficulty_info['name'],
            'num_pieces': num_pieces,
            'grid_rows': grid_rows,
            'grid_cols': grid_cols
        }

        print(f"✅ Puzzle created: {num_regions} region(s), {len(all_options)} options")
        return puzzle_data

    def _calculate_grid_dimensions(self, num_pieces):
        """
        Calculate optimal grid dimensions for given number of pieces

        Args:
            num_pieces: total number of pieces

        Returns:
            tuple: (rows, cols)
        """
        # Try to create a grid as square as possible
        if num_pieces == 2:
            return (1, 2)
        elif num_pieces == 4:
            return (2, 2)
        elif num_pieces == 8:
            return (2, 4)
        elif num_pieces == 16:
            return (4, 4)
        elif num_pieces == 32:
            return (4, 8)
        else:
            # Fallback: find closest factors
            sqrt_pieces = int(np.sqrt(num_pieces))
            for i in range(sqrt_pieces, 0, -1):
                if num_pieces % i == 0:
                    return (i, num_pieces // i)
            return (1, num_pieces)

    def _split_image_into_pieces(self, image, rows, cols):
        """
        Split image into grid of pieces

        Args:
            image: input image
            rows: number of rows
            cols: number of columns

        Returns:
            list: list of image pieces
        """
        h, w = image.shape[:2]
        piece_height = h // rows
        piece_width = w // cols

        pieces = []

        for row in range(rows):
            for col in range(cols):
                y = row * piece_height
                x = col * piece_width

                # Handle last row/col (might be slightly larger)
                if row == rows - 1:
                    piece_h = h - y
                else:
                    piece_h = piece_height

                if col == cols - 1:
                    piece_w = w - x
                else:
                    piece_w = piece_width

                piece = self.image_processor.crop_image(
                    image, x, y, piece_w, piece_h)
                pieces.append(piece)

        return pieces

    def _generate_decoy_pieces(self, width, height, count=4, difficulty_level=1):
        """
        Generate decoy pieces from random images

        Args:
            width: width of pieces
            height: height of pieces
            count: number of decoys to generate
            difficulty_level: affects how similar decoys are

        Returns:
            list: list of decoy pieces
        """
        decoys = []

        # Determine query based on difficulty
        if difficulty_level <= 2:
            # Easy: completely random images
            queries = [None]  # Random
        elif difficulty_level == 3:
            # Medium: somewhat related categories
            queries = ['nature', 'animals', 'objects', 'textures', 'patterns']
        else:
            # Hard: similar textures and patterns
            queries = ['textures', 'patterns', 'abstract', 'closeup', 'detail']

        for i in range(count):
            try:
                # Get random image from Unsplash
                query = random.choice(queries)
                random_image, _ = self.unsplash_api.get_random_image(query=query)

                if random_image is None:
                    print(f"⚠️ Failed to get image {i+1}, using fallback")
                    random_image = self._create_fallback_decoy(width, height)

                # Extract random crop from the image
                decoy_piece = self._extract_random_crop(
                    random_image, width, height)

                decoys.append(decoy_piece)

            except Exception as e:
                print(f"⚠️ Error generating decoy {i+1}: {e}")
                decoys.append(self._create_fallback_decoy(width, height))

        return decoys

    def _extract_random_crop(self, image, target_width, target_height):
        """
        Extract a random crop from image

        Args:
            image: source image
            target_width: desired width
            target_height: desired height

        Returns:
            cropped piece
        """
        h, w = image.shape[:2]

        # If image is smaller than target, resize it first
        if h < target_height or w < target_width:
            scale = max(target_height / h, target_width / w) * 1.2
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(image, (new_w, new_h))
            h, w = image.shape[:2]

        # Random crop position
        max_x = w - target_width
        max_y = h - target_height

        x = random.randint(0, max_x) if max_x > 0 else 0
        y = random.randint(0, max_y) if max_y > 0 else 0

        crop = self.image_processor.crop_image(
            image, x, y, target_width, target_height)

        return crop

    def _create_fallback_decoy(self, width, height):
        """
        Create a fallback decoy piece with random pattern

        Args:
            width: piece width
            height: piece height

        Returns:
            numpy array
        """
        # Create random colored pattern
        base_color = np.random.randint(0, 255, 3)
        piece = np.zeros((height, width, 3), dtype=np.uint8)

        for i in range(3):
            piece[:, :, i] = np.random.randint(
                max(0, base_color[i] - 40),
                min(255, base_color[i] + 40),
                (height, width)
            )

        # Add texture
        noise = np.random.normal(0, 20, (height, width, 3)).astype(np.int16)
        piece = np.clip(piece.astype(np.int16) +
                        noise, 0, 255).astype(np.uint8)

        piece = cv2.GaussianBlur(piece, (5, 5), 0)

        return piece


if __name__ == "__main__":
    # Testing
    print("🧪 Testing Puzzle Generator Module...")

    generator = PuzzleGenerator()

    # Create test image
    test_image = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)

    # Draw some shapes for visual testing
    cv2.rectangle(test_image, (100, 100), (300, 300), (255, 0, 0), -1)
    cv2.circle(test_image, (500, 200), 80, (0, 255, 0), -1)
    cv2.rectangle(test_image, (400, 400), (700, 550), (0, 0, 255), -1)

    # Test puzzle generation at different levels
    for level in [1, 2, 3]:
        print(f"\n--- Testing difficulty level {level} ---")
        puzzle_data = generator.create_puzzle(
            test_image, difficulty_level=level)

        print(f"✅ Puzzle created:")
        print(
            f"   Grid: {puzzle_data['grid_rows']}x{puzzle_data['grid_cols']}")
        print(f"   Options: {len(puzzle_data['options'])} pieces")
        print(f"   Correct index: {puzzle_data['correct_index']}")
        print(
            f"   Missing position: ({puzzle_data['missing_position']['x']}, {puzzle_data['missing_position']['y']})")

    print("\n✅ Puzzle Generator Module - All tests passed!")
