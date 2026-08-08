"""Edge detection and analysis utilities for image comparison."""

import numpy as np
import cv2
from scipy.spatial.distance import directed_hausdorff


class EdgeAnalyzer:
    """Detects and compares edges using Canny, Sobel, Laplacian, and Hausdorff distance."""

    def __init__(self):
        """Initialize the edge analyzer."""
        print("✅ Edge Analyzer initialized")

    def detect_edges_canny(self, image, low_threshold=50, high_threshold=150):
        """Detect edges with Canny after Gaussian smoothing. Returns a binary edge image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
        return cv2.Canny(blurred, low_threshold, high_threshold)

    def detect_edges_sobel(self, image):
        """Compute Sobel gradient magnitude and return it as a uint8 image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        return (magnitude / magnitude.max() * 255).astype(np.uint8)

    def detect_edges_laplacian(self, image):
        """Detect edges with the Laplacian operator after Gaussian smoothing."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        laplacian = np.abs(cv2.Laplacian(blurred, cv2.CV_64F))
        return (laplacian / laplacian.max() * 255).astype(np.uint8)

    def calculate_edge_histogram(self, edges, bins=8):
        """Compute an orientation histogram over detected edge pixels using Sobel gradients."""
        sobelx = cv2.Sobel(edges, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(edges, cv2.CV_64F, 0, 1, ksize=3)
        angles = np.arctan2(sobely, sobelx)
        hist, _ = np.histogram(
            angles[edges > 0], bins=bins, range=(-np.pi, np.pi), density=True)
        return hist

    def analyze_edge_continuity(self, puzzle_image, selected_patch, position):
        """Check how well piece edges align with puzzle edges at each boundary side.
        Returns the mean IoU score over available boundary directions."""
        x, y, w, h = position

        edges_puzzle = self.detect_edges_canny(puzzle_image)
        edges_patch = self.detect_edges_canny(selected_patch)

        border_width = 5
        continuity_scores = []

        if y >= border_width:
            bp = edges_puzzle[y-border_width:y, x:x+w]
            bpa = edges_patch[0:border_width, :]
            if bp.shape == bpa.shape:
                continuity_scores.append(
                    np.sum(bp & bpa) / max(np.sum(bp | bpa), 1))

        if y + h + border_width < edges_puzzle.shape[0]:
            bp = edges_puzzle[y+h:y+h+border_width, x:x+w]
            bpa = edges_patch[-border_width:, :]
            if bp.shape == bpa.shape:
                continuity_scores.append(
                    np.sum(bp & bpa) / max(np.sum(bp | bpa), 1))

        if x >= border_width:
            bp = edges_puzzle[y:y+h, x-border_width:x]
            bpa = edges_patch[:, 0:border_width]
            if bp.shape == bpa.shape:
                continuity_scores.append(
                    np.sum(bp & bpa) / max(np.sum(bp | bpa), 1))

        if x + w + border_width < edges_puzzle.shape[1]:
            bp = edges_puzzle[y:y+h, x+w:x+w+border_width]
            bpa = edges_patch[:, -border_width:]
            if bp.shape == bpa.shape:
                continuity_scores.append(
                    np.sum(bp & bpa) / max(np.sum(bp | bpa), 1))

        return np.mean(continuity_scores) if continuity_scores else 0.0

    def compare_edge_histograms(self, hist1, hist2):
        """Compare two edge orientation histograms via chi-square distance. Returns a score in [0, 1]."""
        chi_square = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))
        return 1 / (1 + chi_square)

    def calculate_hausdorff_distance(self, edges1, edges2):
        """Compute the symmetric Hausdorff distance between two binary edge maps."""
        points1 = np.column_stack(np.where(edges1 > 0))
        points2 = np.column_stack(np.where(edges2 > 0))

        if len(points1) == 0 or len(points2) == 0:
            return float('inf')

        return max(
            directed_hausdorff(points1, points2)[0],
            directed_hausdorff(points2, points1)[0]
        )

    def analyze_edge_density(self, image):
        """Return Canny and Sobel edge density metrics for the image."""
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
        """Comprehensive edge comparison using density, orientation histogram, Hausdorff, and Sobel correlation.
        Returns (is_match: bool, score: float, details: dict)."""
        try:
            edges1_canny = self.detect_edges_canny(image1)
            edges2_canny = self.detect_edges_canny(image2)

            density1 = np.count_nonzero(edges1_canny) / edges1_canny.size
            density2 = np.count_nonzero(edges2_canny) / edges2_canny.size
            density_similarity = 1 - abs(density1 - density2)

            hist1 = self.calculate_edge_histogram(edges1_canny)
            hist2 = self.calculate_edge_histogram(edges2_canny)
            histogram_similarity = self.compare_edge_histograms(hist1, hist2)

            hausdorff_similarity = 0.5  # default when edges are too sparse
            if density1 > 0.01 and density2 > 0.01:
                edges1_small = cv2.resize(edges1_canny, (50, 50))
                edges2_small = cv2.resize(edges2_canny, (50, 50))
                hausdorff_dist = self.calculate_hausdorff_distance(edges1_small, edges2_small)
                max_dist = 50 * np.sqrt(2)
                hausdorff_similarity = 1 - min(hausdorff_dist / max_dist, 1)

            sobel1 = self.detect_edges_sobel(image1)
            sobel2 = self.detect_edges_sobel(image2)
            sobel_similarity = max(0, np.corrcoef(sobel1.ravel(), sobel2.ravel())[0, 1])

            final_score = (
                density_similarity * 0.20 +
                histogram_similarity * 0.30 +
                hausdorff_similarity * 0.25 +
                sobel_similarity * 0.25
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
        """Return the edge image computed by the specified detection method."""
        if method == 'canny':
            return self.detect_edges_canny(image)
        elif method == 'sobel':
            return self.detect_edges_sobel(image)
        elif method == 'laplacian':
            return self.detect_edges_laplacian(image)
        else:
            raise ValueError(f"Unknown method: {method}")
