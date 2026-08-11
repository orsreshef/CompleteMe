"""Texture analysis utilities using Local Binary Patterns (LBP)."""

import numpy as np
import cv2
from skimage.feature import local_binary_pattern


class TextureAnalyzer:
    """Analyzes and compares image textures using LBP histograms."""

    def __init__(self):
        """Initialize the texture analyzer."""
        print("✅ Texture Analyzer initialized")

    def calculate_lbp(self, image, radius=1, n_points=8):
        """Compute a normalized LBP histogram for the image. Returns a 1-D float array."""
        if len(image.shape) == 3:
            # LBP works on intensity only, so convert color images to grayscale first
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # For every pixel, encode how its neighbors (within radius) compare to it
        lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
        n_bins = n_points + 2  # uniform patterns + 2 non-uniform bins
        # Turn per-pixel pattern codes into one global histogram
        hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)
        return hist

    def compare_lbp(self, hist1, hist2):
        """Compare two LBP histograms via chi-square distance. Returns a score in [0, 1]."""
        # Chi-square distance between histograms; 1e-10 avoids division by zero
        chi_square = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))
        # Convert distance to similarity: [1,0]
        return 1 / (1 + chi_square)
