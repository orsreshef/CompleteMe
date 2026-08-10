"""Boundary matching — validates piece placement by comparing HSV histograms along the hole edges."""

import numpy as np
import cv2
from scipy.spatial.distance import euclidean


class BoundaryMatcher:
    """Checks whether a candidate piece fits the puzzle hole by comparing boundary strip similarity."""

    def __init__(self, boundary_width=5):
        """Initialize with the pixel width of strips to sample around the hole."""
        self.boundary_width = boundary_width
        print(f"✅ Boundary Matcher initialized (width={boundary_width}px)")

    def extract_boundaries(self, puzzle_image, missing_position):
        """Extract the four boundary strips around the hole from puzzle_image.
        Returns a dict with keys 'top', 'bottom', 'left', 'right' (None if at image edge)."""
        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        boundaries = {}

        if y >= self.boundary_width:
            boundaries['top'] = puzzle_image[y - self.boundary_width:y, x:x + w]
        else:
            boundaries['top'] = None

        if y + h + self.boundary_width <= puzzle_image.shape[0]:
            boundaries['bottom'] = puzzle_image[y + h:y + h + self.boundary_width, x:x + w]
        else:
            boundaries['bottom'] = None

        if x >= self.boundary_width:
            boundaries['left'] = puzzle_image[y:y + h, x - self.boundary_width:x]
        else:
            boundaries['left'] = None

        if x + w + self.boundary_width <= puzzle_image.shape[1]:
            boundaries['right'] = puzzle_image[y:y + h, x + w:x + w + self.boundary_width]
        else:
            boundaries['right'] = None

        return boundaries

    def extract_piece_boundaries(self, piece):
        """Extract the four edge strips from a piece image.
        Returns a dict with keys 'top', 'bottom', 'left', 'right'."""
        h, w = piece.shape[:2]

        return {
            'top': piece[0:self.boundary_width, :],
            'bottom': piece[h - self.boundary_width:h, :],
            'left': piece[:, 0:self.boundary_width],
            'right': piece[:, w - self.boundary_width:w]
        }

    def compare_boundary_colors(self, boundary1, boundary2):
        """Compare the average BGR color of two strips. Returns a similarity score in [0, 1]."""
        if boundary1 is None or boundary2 is None:
            return 0.0

        if boundary1.shape != boundary2.shape:
            boundary2 = cv2.resize(boundary2, (boundary1.shape[1], boundary1.shape[0]))

        avg1 = boundary1.mean(axis=(0, 1))
        avg2 = boundary2.mean(axis=(0, 1))

        distance = euclidean(avg1, avg2)
        max_distance = np.sqrt(3 * 255**2)

        return max(0, min(1, 1 - (distance / max_distance)))

    def compare_boundary_histograms(self, boundary1, boundary2):
        """Compare HSV histograms of two boundary strips. Returns a correlation score in [0, 1]."""
        if boundary1 is None or boundary2 is None:
            return 0.0

        if boundary1.shape != boundary2.shape:
            boundary2 = cv2.resize(boundary2, (boundary1.shape[1], boundary1.shape[0]))

        hsv1 = cv2.cvtColor(boundary1, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(boundary2, cv2.COLOR_BGR2HSV)

        hist1 = cv2.calcHist([hsv1], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
        hist2 = cv2.calcHist([hsv2], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])

        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()

        return max(0, cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))

    def validate_piece_placement(self, puzzle_image, selected_piece, missing_position):
        """Score a candidate piece against the hole using boundary histograms and average colors.
        Returns (is_match: bool, confidence: float, details: dict)."""
        try:
            target_h = missing_position['height']
            target_w = missing_position['width']

            if selected_piece.shape[:2] != (target_h, target_w):
                selected_piece = cv2.resize(selected_piece, (target_w, target_h))

            puzzle_boundaries = self.extract_boundaries(puzzle_image, missing_position)
            piece_boundaries = self.extract_piece_boundaries(selected_piece)

            scores = {}

            for direction in ['top', 'bottom', 'left', 'right']:
                puzzle_bound = puzzle_boundaries.get(direction)
                piece_bound = piece_boundaries.get(direction)

                if puzzle_bound is not None and piece_bound is not None:
                    # 70% weight to histograms, 30% to average color
                    hist_score = self.compare_boundary_histograms(puzzle_bound, piece_bound)
                    color_score = self.compare_boundary_colors(puzzle_bound, piece_bound)
                    scores[direction] = 0.7 * hist_score + 0.3 * color_score
                # Zone is at the image edge — skip this direction rather than penalise with 0.0

            confidence = np.mean(list(scores.values())) if scores else 0.0
            is_match = confidence >= 0.70

            details = {
                'boundary_scores': scores,
                'overall_confidence': confidence
            }

            return is_match, confidence, details

        except Exception as e:
            print(f"❌ Error in boundary validation: {e}")
            import traceback
            traceback.print_exc()
            return False, 0.0, {}
