"""Puzzle generation — splits images into grids, selects missing regions, and assembles decoys."""

import numpy as np
import cv2
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.unsplash_api import UnsplashAPI
from models.image_processor import ImageProcessor
from config import Config


class PuzzleGenerator:
    """Generates complete puzzle games: splits the image, hides pieces, and builds the option pool."""

    def __init__(self):
        """Initialize puzzle generator."""
        self.image_processor = ImageProcessor()
        self.unsplash_api = UnsplashAPI()
        print("✅ Puzzle Generator initialized")

    def _get_difficulty_queries(self, difficulty_level):
        """Return the Unsplash query pool for a given difficulty level."""
        if difficulty_level <= 2:
            return ['flowers', 'balloons', 'candy', 'fruits', 'birds']
        elif difficulty_level == 3:
            return ['butterflies', 'parrots', 'coral reef', 'sunflowers', 'koi fish']
        else:
            return ['autumn leaves', 'tropical flowers', 'feathers', 'peacock', 'mosaic']

    def prefetch_all_images(self, query, difficulty_level, num_regions):
        """Fetch the main puzzle image and all decoy images in parallel to avoid sequential waits.
        Returns (main_image, fetched_url, decoy_images); main_image is None if fetch failed."""
        num_pieces = Config.DIFFICULTY_LEVELS[difficulty_level]['pieces']
        actual_regions = max(1, min(int(num_regions), 4, num_pieces - 1))
        decoy_count = max(6 - actual_regions, 2)
        queries = self._get_difficulty_queries(difficulty_level)

        def fetch_main():
            img, url = self.unsplash_api.get_random_image(
                query=query, orientation='landscape')
            return img, url

        def fetch_decoy(i):
            q = random.choice(queries)
            img, _ = self.unsplash_api.get_random_image(query=q)
            return img

        with ThreadPoolExecutor(max_workers=1 + decoy_count) as executor:
            main_future = executor.submit(fetch_main)
            decoy_futures = [executor.submit(
                fetch_decoy, i) for i in range(decoy_count)]
            # executor.__exit__ waits for all futures before continuing, also result() do the same
            main_image, fetched_url = main_future.result()
            decoy_images = [f.result() for f in decoy_futures]
        return main_image, fetched_url, decoy_images

    def create_puzzle(self, image, difficulty_level=1, num_regions=1, prefetched_decoys=None):
        """Build a complete puzzle from an image: split into grid, hide num_regions pieces, add decoys.
        Returns a dict with puzzle_image, options, missing_positions, grid metadata, and more."""
        if isinstance(image, str):
            image = self.image_processor.load_image(image)

        if difficulty_level not in Config.DIFFICULTY_LEVELS:
            raise ValueError(f"Invalid difficulty level: {difficulty_level}")

        difficulty_info = Config.DIFFICULTY_LEVELS[difficulty_level]
        num_pieces = difficulty_info['pieces']

        # Clamp num_regions: at least 1, at most 4, never >= total pieces
        num_regions = max(1, min(int(num_regions), 4, num_pieces - 1))

        print(
            f"Creating puzzle: {difficulty_info['name']} ({num_pieces} pieces, {num_regions} missing)")

        image = self.image_processor.resize_image(
            image, max_size=Config.MAX_IMAGE_DIMENSION, maintain_aspect=True)

        grid_rows, grid_cols = self._calculate_grid_dimensions(num_pieces)
        pieces = self._split_image_into_pieces(image, grid_rows, grid_cols)

        piece_height = image.shape[0] // grid_rows
        piece_width = image.shape[1] // grid_cols

        # pieces is row-major flat list: pieces[i] is grid cell (row=i//cols, col=i%cols)
        missing_indices = random.sample(range(len(pieces)), num_regions)

        missing_pieces = []
        missing_positions = []
        puzzle_image = image.copy()

        for missing_index in missing_indices:
            # reverse the flat index back into (row, col) on the grid
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

            # save the hole's position and size, so we know where to draw it later
            missing_positions.append(pos)
            # save the real piece image, so it can be added to the 6 answer choices
            missing_pieces.append(pieces[missing_index])

            puzzle_image = self.image_processor.create_black_square(
                puzzle_image, pos['x'], pos['y'], pos['width'], pos['height'])

        # Pool of answers - always has 6 pieces: num_regions correct + (6 - num_regions) decoys
        decoy_count = max(6 - num_regions, 2)
        decoy_pieces = self._generate_decoy_pieces(
            piece_width, piece_height,
            count=decoy_count,
            difficulty_level=difficulty_level,
            prefetched_images=prefetched_decoys
        )

        all_options = missing_pieces + decoy_pieces
        random.shuffle(all_options)

        # correct_indices IS computed in puzzle_data, but app.py's
        # active_games never stores it — validate_answer never reads this value, it decides correctness purely via CV scores
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
            'missing_pieces': missing_pieces,
            'missing_positions': missing_positions,
            'correct_indices': correct_indices,
            'num_regions': num_regions,
            'missing_piece': missing_pieces[0],
            'missing_position': missing_positions[0],
            'correct_index': correct_indices[0] if correct_indices else None,
            'options': all_options,
            'difficulty_level': difficulty_level,
            'difficulty_name': difficulty_info['name'],
            'num_pieces': num_pieces,
            'grid_rows': grid_rows,
            'grid_cols': grid_cols
        }

        print(
            f"Puzzle created: {num_regions} region(s), {len(all_options)} options")
        return puzzle_data

    def _calculate_grid_dimensions(self, num_pieces):
        """Return (rows, cols) for the most square grid that fits num_pieces."""
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
            sqrt_pieces = int(np.sqrt(num_pieces))
            for i in range(sqrt_pieces, 0, -1):
                if num_pieces % i == 0:
                    return (i, num_pieces // i)
            return (1, num_pieces)

    def _split_image_into_pieces(self, image, rows, cols):
        """Split image into a rows×cols grid and return the list of piece arrays."""
        h, w = image.shape[:2]
        piece_height = h // rows
        piece_width = w // cols

        pieces = []

        for row in range(rows):
            for col in range(cols):
                y = row * piece_height
                x = col * piece_width

                # Last row/col may be slightly larger due to integer division
                piece_h = h - y if row == rows - 1 else piece_height
                piece_w = w - x if col == cols - 1 else piece_width

                piece = self.image_processor.crop_image(
                    image, x, y, piece_w, piece_h)
                pieces.append(piece)

        return pieces

    def _generate_decoy_pieces(self, width, height, count=4, difficulty_level=1,
                               prefetched_images=None):
        """Generate decoy pieces by cropping Unsplash images; skips download if prefetched_images provided."""
        queries = self._get_difficulty_queries(difficulty_level)

        def process_one(i):
            try:
                raw_image = prefetched_images[i] if prefetched_images else None
                if raw_image is None:
                    query = random.choice(queries)
                    raw_image, _ = self.unsplash_api.get_random_image(
                        query=query)
                if raw_image is None:
                    print(
                        f"⚠️ Failed to get decoy image {i+1}, using fallback")
                    return self._create_fallback_decoy(width, height)
                return self._extract_random_crop(raw_image, width, height)
            except Exception as e:
                print(f"⚠️ Error generating decoy {i+1}: {e}")
                return self._create_fallback_decoy(width, height)

        if prefetched_images:
            # Images already downloaded — just crop, no threads needed
            decoys = [process_one(i) for i in range(count)]
        else:
            with ThreadPoolExecutor(max_workers=count) as executor:
                futures = {executor.submit(
                    process_one, i): i for i in range(count)}
                decoys = [None] * count
                for future in as_completed(futures):
                    decoys[futures[future]] = future.result()

        return decoys

    def _extract_random_crop(self, image, target_width, target_height):
        """Extract a random crop of target_width × target_height from image, upscaling if needed."""
        h, w = image.shape[:2]

        # if we got from unsplash smaller image than the target size, upscale it first to ensure we can crop the desired size
        if h < target_height or w < target_width:
            scale = max(target_height / h, target_width / w) * 1.2
            image = cv2.resize(image, (int(w * scale), int(h * scale)))
            h, w = image.shape[:2]

        max_x = w - target_width
        max_y = h - target_height

        x = random.randint(0, max_x) if max_x > 0 else 0
        y = random.randint(0, max_y) if max_y > 0 else 0

        return self.image_processor.crop_image(image, x, y, target_width, target_height)

    def _create_fallback_decoy(self, width, height):
        """Generate a random-coloured noise patch as a fallback decoy piece."""
        base_color = np.random.randint(0, 255, 3)
        piece = np.zeros((height, width, 3), dtype=np.uint8)

        for i in range(3):
            piece[:, :, i] = np.random.randint(
                max(0, base_color[i] - 40),
                min(255, base_color[i] + 40),
                (height, width)
            )

        # Gaussian noise
        noise = np.random.normal(0, 20, (height, width, 3)).astype(np.int16)
        piece = np.clip(piece.astype(np.int16) +
                        noise, 0, 255).astype(np.uint8)
        piece = cv2.GaussianBlur(piece, (5, 5), 0)

        return piece
