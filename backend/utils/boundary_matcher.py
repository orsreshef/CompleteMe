"""
Boundary Matching Validator
Checks whether a selected piece fits the puzzle image with a black square hole
"""

import numpy as np
import cv2
from scipy.spatial.distance import euclidean


class BoundaryMatcher:
    """
    Class for checking boundary compatibility between a selected piece and the original image
    """

    def __init__(self, boundary_width=5):
        """
        Initialize

        Args:
            boundary_width: width of the boundary strip to check (pixels)
        """
        self.boundary_width = boundary_width
        print(f"✅ Boundary Matcher initialized (width={boundary_width}px)")

    def extract_boundaries(self, puzzle_image, missing_position):
        """
        Extracts the boundary strips around the black square hole from the image

        Args:
            puzzle_image: the image with the black square
            missing_position: dict with x, y, width, height

        Returns:
            dict: {'top', 'bottom', 'left', 'right'} - image boundary strips
        """
        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        boundaries = {}

        # Top boundary (above the black square)
        if y >= self.boundary_width:
            boundaries['top'] = puzzle_image[
                y - self.boundary_width:y,
                x:x + w
            ]
        else:
            boundaries['top'] = None

        # Bottom boundary (below the black square)
        if y + h + self.boundary_width <= puzzle_image.shape[0]:
            boundaries['bottom'] = puzzle_image[
                y + h:y + h + self.boundary_width,
                x:x + w
            ]
        else:
            boundaries['bottom'] = None

        # Left boundary (left of the black square)
        if x >= self.boundary_width:
            boundaries['left'] = puzzle_image[
                y:y + h,
                x - self.boundary_width:x
            ]
        else:
            boundaries['left'] = None

        # Right boundary (right of the black square)
        if x + w + self.boundary_width <= puzzle_image.shape[1]:
            boundaries['right'] = puzzle_image[
                y:y + h,
                x + w:x + w + self.boundary_width
            ]
        else:
            boundaries['right'] = None

        return boundaries

    def extract_piece_boundaries(self, piece):
        """
        Extracts the edge strips from the selected piece

        Args:
            piece: the piece image

        Returns:
            dict: {'top', 'bottom', 'left', 'right'} - piece edge strips
        """
        h, w = piece.shape[:2]

        boundaries = {
            'top': piece[0:self.boundary_width, :],
            'bottom': piece[h - self.boundary_width:h, :],
            'left': piece[:, 0:self.boundary_width],
            'right': piece[:, w - self.boundary_width:w]
        }

        return boundaries

    def compare_boundary_colors(self, boundary1, boundary2):
        """
        Compares colors between two boundary strips

        Args:
            boundary1: first boundary strip (numpy array)
            boundary2: second boundary strip (numpy array)

        Returns:
            float: similarity score (0-1)
        """
        if boundary1 is None or boundary2 is None:
            return 0.0

        if boundary1.shape != boundary2.shape:
            # Resize if needed
            boundary2 = cv2.resize(
                boundary2, (boundary1.shape[1], boundary1.shape[0]))

        # Calculate average colors
        avg1 = boundary1.mean(axis=(0, 1))
        avg2 = boundary2.mean(axis=(0, 1))

        # Euclidean distance
        distance = euclidean(avg1, avg2)
        max_distance = np.sqrt(3 * 255**2)  # maximum possible distance

        # Convert to similarity score
        similarity = 1 - (distance / max_distance)

        return max(0, min(1, similarity))

    def compare_boundary_histograms(self, boundary1, boundary2):
        """
        Compares color histograms between two boundary strips

        Args:
            boundary1: first boundary strip
            boundary2: second boundary strip

        Returns:
            float: similarity score (0-1)
        """
        if boundary1 is None or boundary2 is None:
            return 0.0

        if boundary1.shape != boundary2.shape:
            boundary2 = cv2.resize(
                boundary2, (boundary1.shape[1], boundary1.shape[0]))

        # Convert to HSV
        hsv1 = cv2.cvtColor(boundary1, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(boundary2, cv2.COLOR_BGR2HSV)

        # Calculate histograms
        hist1 = cv2.calcHist([hsv1], [0, 1, 2], None, [
                             8, 8, 8], [0, 180, 0, 256, 0, 256])
        hist2 = cv2.calcHist([hsv2], [0, 1, 2], None, [
                             8, 8, 8], [0, 180, 0, 256, 0, 256])

        # Normalize
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()

        # Compare
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        return max(0, similarity)

    def validate_piece_placement(self, puzzle_image, selected_piece, missing_position):
        """
        Checks whether the selected piece fits the image

        Args:
            puzzle_image: the image with the black square
            selected_piece: the piece selected by the user
            missing_position: position of the black square

        Returns:
            tuple: (is_match, confidence, details)
        """
        try:
            # Resize piece if needed
            target_h = missing_position['height']
            target_w = missing_position['width']

            if selected_piece.shape[:2] != (target_h, target_w):
                selected_piece = cv2.resize(
                    selected_piece, (target_w, target_h))

            # Extract boundaries from the puzzle image
            puzzle_boundaries = self.extract_boundaries(
                puzzle_image, missing_position)

            # Extract boundaries from the piece
            piece_boundaries = self.extract_piece_boundaries(selected_piece)

            # Score each boundary direction
            scores = {}

            for direction in ['top', 'bottom', 'left', 'right']:
                puzzle_bound = puzzle_boundaries.get(direction)
                piece_bound = piece_boundaries.get(direction)

                if puzzle_bound is not None and piece_bound is not None:
                    # 70% weight to histograms, 30% to average color
                    hist_score = self.compare_boundary_histograms(
                        puzzle_bound, piece_bound)
                    color_score = self.compare_boundary_colors(
                        puzzle_bound, piece_bound)

                    scores[direction] = 0.7 * hist_score + 0.3 * color_score
                # else: zone is at the image edge — skip this direction
                # (don't penalize with 0.0; just average the sides that exist)

            # Overall score — average of available directions
            if scores:
                confidence = np.mean(list(scores.values()))
            else:
                confidence = 0.0

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

    def visualize_boundaries(self, puzzle_image, selected_piece, missing_position):
        """
        Creates a visualization of the boundaries for inspection

        Args:
            puzzle_image: the image with the black square
            selected_piece: the selected piece
            missing_position: the position

        Returns:
            numpy array: image with boundaries highlighted
        """
        vis = puzzle_image.copy()

        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        # Draw boundaries in different colors
        thickness = self.boundary_width

        # Top — red
        if y >= thickness:
            cv2.rectangle(vis, (x, y - thickness), (x + w, y), (0, 0, 255), -1)

        # Bottom — green
        if y + h + thickness <= vis.shape[0]:
            cv2.rectangle(vis, (x, y + h), (x + w, y +
                          h + thickness), (0, 255, 0), -1)

        # Left — blue
        if x >= thickness:
            cv2.rectangle(vis, (x - thickness, y), (x, y + h), (255, 0, 0), -1)

        # Right — yellow
        if x + w + thickness <= vis.shape[1]:
            cv2.rectangle(vis, (x + w, y),
                          (x + w + thickness, y + h), (0, 255, 255), -1)

        # The hole itself — white outline
        cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 255, 255), 2)

        return vis
