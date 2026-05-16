"""
Edge Detection and Analysis Module
Advanced edge detection and analysis for image comparison
"""

import numpy as np
import cv2
from scipy.spatial.distance import directed_hausdorff


class EdgeAnalyzer:
    """
    Class for detecting and analyzing edges in images
    """

    def __init__(self):
        """Initialize the edge analyzer"""
        print("✅ Edge Analyzer initialized")

    def detect_edges_canny(self, image, low_threshold=50, high_threshold=150):
        """
        Detect edges using Canny Edge Detection

        Args:
            image: image
            low_threshold: lower threshold
            high_threshold: upper threshold

        Returns:
            Edge image (binary)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Smooth before edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)

        # Canny edge detection
        edges = cv2.Canny(blurred, low_threshold, high_threshold)

        return edges

    def detect_edges_sobel(self, image):
        """
        Detect edges using Sobel operator

        Args:
            image: image

        Returns:
            Gradient magnitude
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Sobel in X direction
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)

        # Sobel in Y direction
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        # Calculate magnitude
        magnitude = np.sqrt(sobelx**2 + sobely**2)

        # Normalize to 0-255
        magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)

        return magnitude

    def detect_edges_laplacian(self, image):
        """
        Detect edges using Laplacian

        Args:
            image: image

        Returns:
            Edge image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Smooth
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # Laplacian
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)

        # Convert to absolute values and normalize
        laplacian = np.abs(laplacian)
        laplacian = (laplacian / laplacian.max() * 255).astype(np.uint8)

        return laplacian

    def calculate_edge_histogram(self, edges, bins=8):
        """
        Calculate edge orientation histogram

        Args:
            edges: edge image
            bins: number of histogram bins

        Returns:
            Histogram of edge orientations
        """
        # Calculate gradient
        sobelx = cv2.Sobel(edges, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(edges, cv2.CV_64F, 0, 1, ksize=3)

        # Calculate orientations
        angles = np.arctan2(sobely, sobelx)

        # Histogram
        hist, _ = np.histogram(
            angles[edges > 0], bins=bins, range=(-np.pi, np.pi), density=True)

        return hist

    def analyze_edge_continuity(self, puzzle_image, selected_patch, position):
        """
        Checks if the edges of the piece connect to the edges of the image

        Args:
            puzzle_image: puzzle image (with the black hole)
            selected_patch: the selected piece
            position: (x, y, w, h) piece position

        Returns:
            Similarity score (0-1)
        """
        x, y, w, h = position

        # Detect edges in the main image
        edges_puzzle = self.detect_edges_canny(puzzle_image)

        # Detect edges in the piece
        edges_patch = self.detect_edges_canny(selected_patch)

        # Check boundary continuity
        border_width = 5

        continuity_scores = []

        # Check top boundary
        if y >= border_width:
            border_puzzle_top = edges_puzzle[y-border_width:y, x:x+w]
            border_patch_top = edges_patch[0:border_width, :]
            if border_puzzle_top.shape == border_patch_top.shape:
                score = np.sum(border_puzzle_top & border_patch_top) / \
                    max(np.sum(border_puzzle_top | border_patch_top), 1)
                continuity_scores.append(score)

        # Check bottom boundary
        if y + h + border_width < edges_puzzle.shape[0]:
            border_puzzle_bottom = edges_puzzle[y+h:y+h+border_width, x:x+w]
            border_patch_bottom = edges_patch[-border_width:, :]
            if border_puzzle_bottom.shape == border_patch_bottom.shape:
                score = np.sum(border_puzzle_bottom & border_patch_bottom) / \
                    max(np.sum(border_puzzle_bottom | border_patch_bottom), 1)
                continuity_scores.append(score)

        # Check left boundary
        if x >= border_width:
            border_puzzle_left = edges_puzzle[y:y+h, x-border_width:x]
            border_patch_left = edges_patch[:, 0:border_width]
            if border_puzzle_left.shape == border_patch_left.shape:
                score = np.sum(border_puzzle_left & border_patch_left) / \
                    max(np.sum(border_puzzle_left | border_patch_left), 1)
                continuity_scores.append(score)

        # Check right boundary
        if x + w + border_width < edges_puzzle.shape[1]:
            border_puzzle_right = edges_puzzle[y:y+h, x+w:x+w+border_width]
            border_patch_right = edges_patch[:, -border_width:]
            if border_puzzle_right.shape == border_patch_right.shape:
                score = np.sum(border_puzzle_right & border_patch_right) / \
                    max(np.sum(border_puzzle_right | border_patch_right), 1)
                continuity_scores.append(score)

        # Average of scores
        if continuity_scores:
            return np.mean(continuity_scores)
        else:
            return 0.0

    def compare_edge_histograms(self, hist1, hist2):
        """
        Compare edge orientation histograms

        Args:
            hist1: first histogram
            hist2: second histogram

        Returns:
            Similarity score (0-1)
        """
        # Chi-square distance
        chi_square = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))

        # Convert to similarity score
        similarity = 1 / (1 + chi_square)

        return similarity

    def calculate_hausdorff_distance(self, edges1, edges2):
        """
        Calculate Hausdorff distance between two edge sets
        This metric measures the maximum minimum distance between points

        Args:
            edges1: first edge set
            edges2: second edge set

        Returns:
            Hausdorff distance (lower = more similar)
        """
        # Find coordinates of edge pixels
        points1 = np.column_stack(np.where(edges1 > 0))
        points2 = np.column_stack(np.where(edges2 > 0))

        if len(points1) == 0 or len(points2) == 0:
            return float('inf')

        # Calculate Hausdorff distance
        hausdorff_dist = max(
            directed_hausdorff(points1, points2)[0],
            directed_hausdorff(points2, points1)[0]
        )

        return hausdorff_dist

    def analyze_edge_density(self, image):
        """
        Analyzes edge density in an image

        Args:
            image: image

        Returns:
            dict: edge density metrics
        """
        edges_canny = self.detect_edges_canny(image)
        edges_sobel = self.detect_edges_sobel(image)

        canny_density = np.count_nonzero(edges_canny) / edges_canny.size
        sobel_density = np.count_nonzero(edges_sobel > 50) / edges_sobel.size

        return {
            'canny_density': canny_density,
            'sobel_density': sobel_density,
            'average_density': (canny_density + sobel_density) / 2
        }

    def validate_edge_match(self, image1, image2, threshold=0.65):
        """
        Comprehensive check of edge match between two images

        Args:
            image1: first image
            image2: second image
            threshold: similarity threshold

        Returns:
            tuple: (is_match, score, details)
        """
        try:
            # 1. Edge detection
            edges1_canny = self.detect_edges_canny(image1)
            edges2_canny = self.detect_edges_canny(image2)

            # 2. Edge density comparison
            density1 = np.count_nonzero(edges1_canny) / edges1_canny.size
            density2 = np.count_nonzero(edges2_canny) / edges2_canny.size
            density_similarity = 1 - abs(density1 - density2)

            # 3. Orientation histogram comparison
            hist1 = self.calculate_edge_histogram(edges1_canny)
            hist2 = self.calculate_edge_histogram(edges2_canny)
            histogram_similarity = self.compare_edge_histograms(hist1, hist2)

            # 4. Hausdorff distance (if enough edges exist)
            hausdorff_similarity = 0.5  # default
            if density1 > 0.01 and density2 > 0.01:
                # Resize for faster calculation
                edges1_small = cv2.resize(edges1_canny, (50, 50))
                edges2_small = cv2.resize(edges2_canny, (50, 50))

                hausdorff_dist = self.calculate_hausdorff_distance(
                    edges1_small, edges2_small)
                max_dist = 50 * np.sqrt(2)  # maximum distance in a 50x50 image
                hausdorff_similarity = 1 - min(hausdorff_dist / max_dist, 1)

            # 5. Sobel magnitude comparison
            sobel1 = self.detect_edges_sobel(image1)
            sobel2 = self.detect_edges_sobel(image2)
            sobel_correlation = np.corrcoef(
                sobel1.ravel(), sobel2.ravel())[0, 1]
            sobel_similarity = max(0, sobel_correlation)  # Normalize to 0-1

            # Weighted score
            weights = {
                'density': 0.20,
                'histogram': 0.30,
                'hausdorff': 0.25,
                'sobel': 0.25
            }

            final_score = (
                density_similarity * weights['density'] +
                histogram_similarity * weights['histogram'] +
                hausdorff_similarity * weights['hausdorff'] +
                sobel_similarity * weights['sobel']
            )

            is_match = final_score >= threshold

            details = {
                'density_similarity': density_similarity,
                'histogram_similarity': histogram_similarity,
                'hausdorff_similarity': hausdorff_similarity,
                'sobel_similarity': sobel_similarity,
                'final_score': final_score
            }

            return is_match, final_score, details

        except Exception as e:
            print(f"❌ Error in edge validation: {e}")
            return False, 0.0, {}

    def visualize_edges(self, image, method='canny'):
        """
        Returns the detected edges as an image

        Args:
            image: image
            method: detection method - 'canny', 'sobel', 'laplacian'

        Returns:
            Edge image
        """
        if method == 'canny':
            return self.detect_edges_canny(image)
        elif method == 'sobel':
            return self.detect_edges_sobel(image)
        elif method == 'laplacian':
            return self.detect_edges_laplacian(image)
        else:
            raise ValueError(f"Unknown method: {method}")


