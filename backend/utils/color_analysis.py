"""Color analysis utilities for comparing images by histogram, moments, and average color."""

import numpy as np
import cv2
from scipy.spatial.distance import euclidean
import colorsys


class ColorAnalyzer:
    """Analyzes and compares colors in images using histograms, statistical moments, and K-Means."""

    def __init__(self):
        """Initialize the color analyzer."""
        print("✅ Color Analyzer initialized")

    def extract_dominant_colors(self, image, k=5):
        """Extract the k dominant colors using K-Means clustering. Returns an array of BGR colors."""
        pixels = image.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
        return centers.astype(np.uint8)

    def calculate_color_histogram(self, image, color_space='HSV'):
        """Compute and return a normalized 3D histogram in HSV, RGB, or LAB color space."""
        if color_space == 'HSV':
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([converted], [0, 1, 2], None, [18, 32, 32],
                                [0, 180, 0, 256, 0, 256])
        elif color_space == 'RGB':
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            hist = cv2.calcHist([converted], [0, 1, 2], None, [32, 32, 32],
                                [0, 256, 0, 256, 0, 256])
        elif color_space == 'LAB':
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            hist = cv2.calcHist([converted], [0, 1, 2], None, [32, 32, 32],
                                [0, 256, 0, 256, 0, 256])
        else:
            raise ValueError(f"Unknown color space: {color_space}")

        return cv2.normalize(hist, hist).flatten()

    def compare_color_histograms(self, hist1, hist2, method='correlation'):
        """Compare two histograms and return a similarity score in [0, 1]."""
        if method == 'correlation':
            return max(0, cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))
        elif method == 'chi_square':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
            return 1 / (1 + score)
        elif method == 'intersection':
            return cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)
        elif method == 'bhattacharyya':
            return 1 - cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
        else:
            raise ValueError(f"Unknown method: {method}")

    def analyze_average_color(self, image):
        """Return the average (B, G, R) color of the image as a tuple of ints."""
        return tuple(image.mean(axis=0).mean(axis=0).astype(int))

    def calculate_color_moments(self, image):
        """Compute mean, std, and skewness for each BGR channel. Returns a nested dict."""
        moments = {}
        for i, channel_name in enumerate(['B', 'G', 'R']):
            channel = image[:, :, i]
            moments[channel_name] = {
                'mean': np.mean(channel),
                'std': np.std(channel),
                'skewness': self._calculate_skewness(channel)
            }
        return moments

    def _calculate_skewness(self, data):
        """Calculate the skewness of a data distribution."""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 3)

    def compare_color_moments(self, moments1, moments2):
        """Compare two color moment dicts and return a normalized similarity score in [0, 1]."""
        total_distance = 0

        for channel in ['B', 'G', 'R']:
            for moment_type in ['mean', 'std', 'skewness']:
                val1 = moments1[channel][moment_type]
                val2 = moments2[channel][moment_type]

                max_val = 255 if moment_type in ('mean', 'std') else 3
                total_distance += abs(val1 - val2) / max_val

        avg_distance = total_distance / 9  # 3 channels × 3 moments
        return max(0, min(1, 1 - avg_distance))

    def validate_color_match(self, image1, image2, threshold=0.75):
        """Comprehensive color comparison using histogram, moments, and average color.
        Returns (is_match: bool, score: float, details: dict)."""
        try:
            hist1_hsv = self.calculate_color_histogram(image1, 'HSV')
            hist2_hsv = self.calculate_color_histogram(image2, 'HSV')
            hist_similarity = self.compare_color_histograms(hist1_hsv, hist2_hsv, 'correlation')

            moments1 = self.calculate_color_moments(image1)
            moments2 = self.calculate_color_moments(image2)
            moments_similarity = self.compare_color_moments(moments1, moments2)

            avg1 = self.analyze_average_color(image1)
            avg2 = self.analyze_average_color(image2)
            avg_similarity = 1 - euclidean(avg1, avg2) / (255 * np.sqrt(3))

            final_score = (
                hist_similarity * 0.5 +
                moments_similarity * 0.3 +
                avg_similarity * 0.2
            )

            is_match = final_score >= threshold

            details = {
                'histogram_similarity': hist_similarity,
                'moments_similarity': moments_similarity,
                'average_similarity': avg_similarity,
                'final_score': final_score
            }

            return is_match, final_score, details

        except Exception as e:
            print(f"❌ Error in color validation: {e}")
            return False, 0.0, {}

    def get_color_palette(self, image, n_colors=5):
        """Return the n dominant colors of the image as a list of RGB tuples."""
        dominant_colors = self.extract_dominant_colors(image, k=n_colors)
        return [tuple(color[::-1]) for color in dominant_colors]

    def visualize_color_comparison(self, image1, image2):
        """Return a side-by-side comparison image with dominant color palettes drawn below each."""
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]

        max_h = max(h1, h2)
        comparison = np.full((max_h, w1 + w2 + 20, 3), 255, dtype=np.uint8)

        comparison[0:h1, 0:w1] = image1
        comparison[0:h2, w1+20:w1+20+w2] = image2

        palette1 = self.get_color_palette(image1)
        palette2 = self.get_color_palette(image2)

        palette_height = 50
        color_width = w1 // len(palette1)

        for i, color in enumerate(palette1):
            cv2.rectangle(comparison,
                          (i * color_width, max_h - palette_height),
                          ((i + 1) * color_width, max_h),
                          color[::-1], -1)

        for i, color in enumerate(palette2):
            cv2.rectangle(comparison,
                          (w1 + 20 + i * color_width, max_h - palette_height),
                          (w1 + 20 + (i + 1) * color_width, max_h),
                          color[::-1], -1)

        return comparison
