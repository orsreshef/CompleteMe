"""
Texture Analysis Module
Advanced texture analysis for image comparison
"""

import numpy as np
import cv2
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops
from scipy.stats import entropy
from scipy.spatial.distance import euclidean


class TextureAnalyzer:
    """
    Class for analyzing and comparing textures in images
    """

    def __init__(self):
        """Initialize the texture analyzer"""
        print("✅ Texture Analyzer initialized")

    def calculate_lbp(self, image, radius=1, n_points=8):
        """
        Calculate Local Binary Pattern (LBP)
        LBP is a local descriptor of image texture

        Args:
            image: image (numpy array)
            radius: neighbour radius
            n_points: number of points around the pixel

        Returns:
            LBP histogram (normalized)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Calculate LBP
        lbp = local_binary_pattern(gray, n_points, radius, method='uniform')

        # Calculate histogram
        n_bins = n_points + 2  # uniform patterns + 2
        hist, _ = np.histogram(lbp.ravel(), bins=n_bins,
                               range=(0, n_bins), density=True)

        return hist

    def calculate_glcm(self, image, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4]):
        """
        Calculate Gray-Level Co-occurrence Matrix (GLCM)
        GLCM describes the spatial relationship between pixels

        Args:
            image: image
            distances: list of distances to check
            angles: list of angles to check

        Returns:
            dict: GLCM properties (contrast, dissimilarity, homogeneity, energy, correlation)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Quantize to 256 levels if needed
        if gray.max() > 255:
            gray = (gray / gray.max() * 255).astype(np.uint8)

        # Calculate GLCM
        glcm = graycomatrix(gray, distances=distances, angles=angles,
                            levels=256, symmetric=True, normed=True)

        # Extract properties
        properties = {
            'contrast': graycoprops(glcm, 'contrast').mean(),
            'dissimilarity': graycoprops(glcm, 'dissimilarity').mean(),
            'homogeneity': graycoprops(glcm, 'homogeneity').mean(),
            'energy': graycoprops(glcm, 'energy').mean(),
            'correlation': graycoprops(glcm, 'correlation').mean(),
            'ASM': graycoprops(glcm, 'ASM').mean()  # Angular Second Moment
        }

        return properties

    def calculate_gabor_features(self, image, num_filters=8):
        """
        Calculate Gabor Features
        Gabor filters detect patterns at different frequencies and orientations

        Args:
            image: image
            num_filters: number of filters (orientations)

        Returns:
            Gabor feature vector
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        features = []

        # Gabor parameters
        ksize = 31  # kernel size
        sigma = 4.0
        lambd = 10.0
        gamma = 0.5
        psi = 0

        # Create filters at different orientations
        for theta in np.arange(0, np.pi, np.pi / num_filters):
            # Create Gabor kernel
            kernel = cv2.getGaborKernel(
                (ksize, ksize), sigma, theta, lambd, gamma, psi)

            # Apply filter
            filtered = cv2.filter2D(gray, cv2.CV_64F, kernel)

            # Calculate mean and standard deviation
            features.append(filtered.mean())
            features.append(filtered.std())

        return np.array(features)

    def calculate_entropy(self, image):
        """
        Calculate image entropy
        Entropy measures the amount of information/randomness in the image

        Args:
            image: image

        Returns:
            entropy value
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Calculate histogram
        hist, _ = np.histogram(gray.ravel(), bins=256,
                               range=(0, 256), density=True)

        # Remove zero values (prevent log(0))
        hist = hist[hist > 0]

        # Calculate entropy
        ent = entropy(hist, base=2)

        return ent

    def calculate_edge_density(self, image):
        """
        Calculate edge density in the image
        More edges = more complex texture

        Args:
            image: image

        Returns:
            edge density (0-1)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Detect edges with Canny
        edges = cv2.Canny(gray, 50, 150)

        # Calculate density (percentage of edge pixels)
        edge_density = np.count_nonzero(edges) / edges.size

        return edge_density

    def calculate_fourier_features(self, image):
        """
        Calculate features in the frequency domain (Fourier)

        Args:
            image: image

        Returns:
            dict: features in the frequency domain
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # FFT
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)

        # Calculate features
        features = {
            'mean_magnitude': magnitude.mean(),
            'std_magnitude': magnitude.std(),
            'energy': (magnitude ** 2).sum(),
            'entropy': self.calculate_entropy((magnitude / magnitude.max() * 255).astype(np.uint8))
        }

        return features

    def compare_lbp(self, hist1, hist2):
        """
        Compare two LBP histograms

        Args:
            hist1: first LBP histogram
            hist2: second LBP histogram

        Returns:
            Similarity score (0-1)
        """
        # Chi-square distance
        chi_square = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))

        # Convert to similarity score
        similarity = 1 / (1 + chi_square)

        return similarity

    def compare_glcm(self, props1, props2):
        """
        Compare GLCM properties

        Args:
            props1: first GLCM properties
            props2: second GLCM properties

        Returns:
            Similarity score (0-1)
        """
        total_distance = 0

        for key in props1.keys():
            val1 = props1[key]
            val2 = props2[key]

            # Normalize
            if key == 'contrast':
                max_val = 100  # typical maximum value
            elif key in ['correlation', 'homogeneity', 'energy', 'ASM']:
                max_val = 1
            else:
                max_val = 10

            distance = abs(val1 - val2) / max_val
            total_distance += distance

        # Average of distances
        avg_distance = total_distance / len(props1)

        # Convert to similarity score
        similarity = 1 - min(avg_distance, 1)

        return similarity

    def compare_gabor(self, features1, features2):
        """
        Compare Gabor features

        Args:
            features1: first Gabor features
            features2: second Gabor features

        Returns:
            Similarity score (0-1)
        """
        # Euclidean distance
        distance = euclidean(features1, features2)

        # Normalize (the maximum possible value is quite large)
        max_distance = np.sqrt(len(features1)) * 100  # estimate

        # Convert to similarity score
        similarity = 1 - min(distance / max_distance, 1)

        return similarity

    def validate_texture_match(self, image1, image2, threshold=0.70):
        """
        Comprehensive check of texture match between two images

        Args:
            image1: first image
            image2: second image
            threshold: similarity threshold

        Returns:
            tuple: (is_match, score, details)
        """
        try:
            # 1. LBP comparison
            lbp1 = self.calculate_lbp(image1)
            lbp2 = self.calculate_lbp(image2)
            lbp_similarity = self.compare_lbp(lbp1, lbp2)

            # 2. GLCM comparison
            glcm1 = self.calculate_glcm(image1)
            glcm2 = self.calculate_glcm(image2)
            glcm_similarity = self.compare_glcm(glcm1, glcm2)

            # 3. Gabor features comparison
            gabor1 = self.calculate_gabor_features(image1)
            gabor2 = self.calculate_gabor_features(image2)
            gabor_similarity = self.compare_gabor(gabor1, gabor2)

            # 4. Edge density comparison
            edge1 = self.calculate_edge_density(image1)
            edge2 = self.calculate_edge_density(image2)
            edge_similarity = 1 - abs(edge1 - edge2)

            # 5. Entropy comparison
            entropy1 = self.calculate_entropy(image1)
            entropy2 = self.calculate_entropy(image2)
            entropy_similarity = 1 - \
                abs(entropy1 - entropy2) / max(entropy1, entropy2, 1)

            # Weighted score
            weights = {
                'lbp': 0.30,
                'glcm': 0.25,
                'gabor': 0.25,
                'edge': 0.10,
                'entropy': 0.10
            }

            final_score = (
                lbp_similarity * weights['lbp'] +
                glcm_similarity * weights['glcm'] +
                gabor_similarity * weights['gabor'] +
                edge_similarity * weights['edge'] +
                entropy_similarity * weights['entropy']
            )

            is_match = final_score >= threshold

            details = {
                'lbp_similarity': lbp_similarity,
                'glcm_similarity': glcm_similarity,
                'gabor_similarity': gabor_similarity,
                'edge_similarity': edge_similarity,
                'entropy_similarity': entropy_similarity,
                'final_score': final_score
            }

            return is_match, final_score, details

        except Exception as e:
            print(f"❌ Error in texture validation: {e}")
            return False, 0.0, {}

    def analyze_texture_complexity(self, image):
        """
        Analyzes the texture complexity of an image

        Args:
            image: image

        Returns:
            dict: complexity metrics
        """
        entropy_val = self.calculate_entropy(image)
        edge_density = self.calculate_edge_density(image)
        glcm_props = self.calculate_glcm(image)

        # Calculate overall complexity
        complexity = {
            'entropy': entropy_val,
            'edge_density': edge_density,
            'contrast': glcm_props['contrast'],
            'overall_complexity': (entropy_val / 8 + edge_density + glcm_props['contrast'] / 100) / 3
        }

        return complexity


class AdvancedTextureAnalyzer(TextureAnalyzer):
    """
    Extended analyzer with additional techniques
    """

    def __init__(self):
        super().__init__()
        print("✅ Advanced Texture Analyzer initialized")

    def calculate_wavelet_features(self, image):
        """
        Calculate Wavelet Transform features
        Wavelets are effective for analyzing textures at different scales

        Args:
            image: image

        Returns:
            feature vector
        """
        try:
            import pywt

            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Wavelet decomposition
            coeffs = pywt.dwt2(gray, 'haar')
            cA, (cH, cV, cD) = coeffs

            # Calculate features from each component
            features = []
            for coeff in [cA, cH, cV, cD]:
                features.append(coeff.mean())
                features.append(coeff.std())
                features.append(np.median(coeff))

            return np.array(features)

        except ImportError:
            print("⚠️ PyWavelets not installed, skipping wavelet features")
            return np.zeros(12)

    def calculate_haralick_features(self, image):
        """
        Calculate Haralick texture features
        A comprehensive set of 13 texture descriptors

        Args:
            image: image

        Returns:
            array: Haralick features
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # GLCM at multiple distances and angles
        distances = [1, 2, 3]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]

        glcm = graycomatrix(gray, distances=distances, angles=angles,
                            levels=256, symmetric=True, normed=True)

        # Extract all properties
        features = []
        properties = ['contrast', 'dissimilarity', 'homogeneity',
                      'energy', 'correlation', 'ASM']

        for prop in properties:
            values = graycoprops(glcm, prop)
            features.append(values.mean())
            features.append(values.std())

        return np.array(features)


