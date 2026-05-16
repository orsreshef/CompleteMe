"""
Color Analysis Module
Advanced color analysis for image comparison
"""

import numpy as np
import cv2
from scipy.spatial.distance import euclidean
import colorsys


class ColorAnalyzer:
    """
    Class for analyzing and comparing colors in images
    """

    def __init__(self):
        """Initialize the color analyzer"""
        print("✅ Color Analyzer initialized")

    def extract_dominant_colors(self, image, k=5):
        """
        Extracts the dominant colors in the image using K-Means

        Args:
            image: image (numpy array)
            k: number of dominant colors to extract

        Returns:
            list: list of dominant colors (RGB)
        """
        # Reshape to pixel list
        pixels = image.reshape(-1, 3).astype(np.float32)

        # K-Means clustering
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(
            pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

        # Convert to int
        dominant_colors = centers.astype(np.uint8)

        return dominant_colors

    def calculate_color_histogram(self, image, color_space='HSV'):
        """
        Calculates a color histogram

        Args:
            image: image
            color_space: color space - 'HSV', 'RGB', or 'LAB'

        Returns:
            Normalized histogram
        """
        # Convert to appropriate color space
        if color_space == 'HSV':
            converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            # HSV: Hue (0-180), Saturation (0-255), Value (0-255)
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

        # Normalize
        hist = cv2.normalize(hist, hist).flatten()

        return hist

    def compare_color_histograms(self, hist1, hist2, method='correlation'):
        """
        Compares two color histograms

        Args:
            hist1: first histogram
            hist2: second histogram
            method: comparison method - 'correlation', 'chi_square', 'intersection', 'bhattacharyya'

        Returns:
            Similarity score (0-1)
        """
        if method == 'correlation':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return max(0, score)  # Normalize to 0-1
        elif method == 'chi_square':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
            # Lower value means higher similarity
            return 1 / (1 + score)
        elif method == 'intersection':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)
            return score
        elif method == 'bhattacharyya':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
            return 1 - score  # Normalize to 0-1
        else:
            raise ValueError(f"Unknown method: {method}")

    def analyze_average_color(self, image):
        """
        Calculates the average color in the image

        Args:
            image: image

        Returns:
            tuple: (B, G, R) - average color values
        """
        avg_color = image.mean(axis=0).mean(axis=0)
        return tuple(avg_color.astype(int))

    def calculate_color_moments(self, image):
        """
        Calculates statistical color moments (mean, std, skewness)

        Args:
            image: image

        Returns:
            dict: moments for each color channel
        """
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
        """Calculates the skewness of a distribution"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 3)

    def compare_color_moments(self, moments1, moments2):
        """
        Compares color moments

        Args:
            moments1: moments of the first image
            moments2: moments of the second image

        Returns:
            Similarity score (0-1)
        """
        total_distance = 0

        for channel in ['B', 'G', 'R']:
            for moment_type in ['mean', 'std', 'skewness']:
                val1 = moments1[channel][moment_type]
                val2 = moments2[channel][moment_type]

                # Normalize by value range
                if moment_type == 'mean' or moment_type == 'std':
                    max_val = 255
                else:  # skewness
                    max_val = 3  # typical maximum value

                distance = abs(val1 - val2) / max_val
                total_distance += distance

        # Average of distances (9 comparisons: 3 channels × 3 moments)
        avg_distance = total_distance / 9

        # Convert to similarity score
        similarity = 1 - avg_distance

        return max(0, min(1, similarity))

    def validate_color_match(self, image1, image2, threshold=0.75):
        """
        Comprehensive check of color match between two images

        Args:
            image1: first image
            image2: second image
            threshold: similarity threshold

        Returns:
            tuple: (is_match, score, details)
        """
        try:
            # 1. Histogram comparison (HSV - best for colors)
            hist1_hsv = self.calculate_color_histogram(image1, 'HSV')
            hist2_hsv = self.calculate_color_histogram(image2, 'HSV')
            hist_similarity = self.compare_color_histograms(
                hist1_hsv, hist2_hsv, 'correlation')

            # 2. Statistical moments comparison
            moments1 = self.calculate_color_moments(image1)
            moments2 = self.calculate_color_moments(image2)
            moments_similarity = self.compare_color_moments(moments1, moments2)

            # 3. Average color comparison
            avg1 = self.analyze_average_color(image1)
            avg2 = self.analyze_average_color(image2)
            avg_distance = euclidean(avg1, avg2) / (255 * np.sqrt(3))  # Normalize
            avg_similarity = 1 - avg_distance

            # Weighted score
            weights = {
                'histogram': 0.5,
                'moments': 0.3,
                'average': 0.2
            }

            final_score = (
                hist_similarity * weights['histogram'] +
                moments_similarity * weights['moments'] +
                avg_similarity * weights['average']
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
        """
        Extracts a color palette from an image

        Args:
            image: image
            n_colors: number of colors in the palette

        Returns:
            list: list of colors in RGB
        """
        dominant_colors = self.extract_dominant_colors(image, k=n_colors)

        # Convert from BGR to RGB
        rgb_colors = [tuple(color[::-1]) for color in dominant_colors]

        return rgb_colors

    def visualize_color_comparison(self, image1, image2):
        """
        Creates a visualization of color comparison

        Args:
            image1: first image
            image2: second image

        Returns:
            Comparison image
        """
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]

        # Create canvas
        max_h = max(h1, h2)
        comparison = np.zeros((max_h, w1 + w2 + 20, 3), dtype=np.uint8)
        comparison.fill(255)

        # Place images
        comparison[0:h1, 0:w1] = image1
        comparison[0:h2, w1+20:w1+20+w2] = image2

        # Add color palettes
        palette1 = self.get_color_palette(image1)
        palette2 = self.get_color_palette(image2)

        # Draw palettes
        palette_height = 50
        color_width = w1 // len(palette1)

        for i, color in enumerate(palette1):
            cv2.rectangle(comparison,
                          (i * color_width, max_h - palette_height),
                          ((i + 1) * color_width, max_h),
                          color[::-1], -1)  # BGR

        for i, color in enumerate(palette2):
            cv2.rectangle(comparison,
                          (w1 + 20 + i * color_width, max_h - palette_height),
                          (w1 + 20 + (i + 1) * color_width, max_h),
                          color[::-1], -1)  # BGR

        return comparison


