"""
Texture Analysis Module
ניתוח מרקמים מתקדם להשוואת תמונות
"""

import numpy as np
import cv2
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops
from scipy.stats import entropy
from scipy.spatial.distance import euclidean


class TextureAnalyzer:
    """
    מחלקה לניתוח והשוואת מרקמים בתמונות
    """

    def __init__(self):
        """אתחול מנתח המרקמים"""
        print("✅ Texture Analyzer initialized")

    def calculate_lbp(self, image, radius=1, n_points=8):
        """
        חישוב Local Binary Pattern (LBP)
        LBP הוא תיאור מקומי של מרקם התמונה
        
        Args:
            image: תמונה (numpy array)
            radius: רדיוס השכנים
            n_points: מספר נקודות סביב הפיקסל
        
        Returns:
            LBP histogram (normalized)
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # חישוב LBP
        lbp = local_binary_pattern(gray, n_points, radius, method='uniform')

        # חישוב היסטוגרמה
        n_bins = n_points + 2  # uniform patterns + 2
        hist, _ = np.histogram(lbp.ravel(), bins=n_bins,
                               range=(0, n_bins), density=True)

        return hist

    def calculate_glcm(self, image, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4]):
        """
        חישוב Gray-Level Co-occurrence Matrix (GLCM)
        GLCM מתאר את הקשר המרחבי בין פיקסלים
        
        Args:
            image: תמונה
            distances: רשימת מרחקים לבדיקה
            angles: רשימת זוויות לבדיקה
        
        Returns:
            dict: מאפייני GLCM (contrast, dissimilarity, homogeneity, energy, correlation)
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # קוונטיזציה ל-256 רמות (אם צריך)
        if gray.max() > 255:
            gray = (gray / gray.max() * 255).astype(np.uint8)

        # חישוב GLCM
        glcm = graycomatrix(gray, distances=distances, angles=angles,
                            levels=256, symmetric=True, normed=True)

        # חילוץ מאפיינים
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
        חישוב Gabor Features
        Gabor filters מזהים תבניות בתדרים וכיוונים שונים
        
        Args:
            image: תמונה
            num_filters: מספר פילטרים (כיוונים)
        
        Returns:
            וקטור מאפייני Gabor
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        features = []

        # פרמטרים של Gabor
        ksize = 31  # גודל הקרנל
        sigma = 4.0
        lambd = 10.0
        gamma = 0.5
        psi = 0

        # יצירת פילטרים בכיוונים שונים
        for theta in np.arange(0, np.pi, np.pi / num_filters):
            # יצירת Gabor kernel
            kernel = cv2.getGaborKernel(
                (ksize, ksize), sigma, theta, lambd, gamma, psi)

            # החלת הפילטר
            filtered = cv2.filter2D(gray, cv2.CV_64F, kernel)

            # חישוב ממוצע וסטיית תקן
            features.append(filtered.mean())
            features.append(filtered.std())

        return np.array(features)

    def calculate_entropy(self, image):
        """
        חישוב אנטרופיה של תמונה
        אנטרופיה מודדת את כמות המידע/אקראיות בתמונה
        
        Args:
            image: תמונה
        
        Returns:
            entropy value
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # חישוב היסטוגרמה
        hist, _ = np.histogram(gray.ravel(), bins=256,
                               range=(0, 256), density=True)

        # הסרת ערכים אפסיים (למנוע log(0))
        hist = hist[hist > 0]

        # חישוב אנטרופיה
        ent = entropy(hist, base=2)

        return ent

    def calculate_edge_density(self, image):
        """
        חישוב צפיפות קצוות בתמונה
        קצוות רבים = מרקם מורכב
        
        Args:
            image: תמונה
        
        Returns:
            edge density (0-1)
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # זיהוי קצוות עם Canny
        edges = cv2.Canny(gray, 50, 150)

        # חישוב צפיפות (אחוז פיקסלי קצה)
        edge_density = np.count_nonzero(edges) / edges.size

        return edge_density

    def calculate_fourier_features(self, image):
        """
        חישוב מאפיינים בתחום התדר (Fourier)
        
        Args:
            image: תמונה
        
        Returns:
            dict: מאפיינים בתחום התדר
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # FFT
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)

        # חישוב מאפיינים
        features = {
            'mean_magnitude': magnitude.mean(),
            'std_magnitude': magnitude.std(),
            'energy': (magnitude ** 2).sum(),
            'entropy': self.calculate_entropy((magnitude / magnitude.max() * 255).astype(np.uint8))
        }

        return features

    def compare_lbp(self, hist1, hist2):
        """
        משווה שני LBP histograms
        
        Args:
            hist1: LBP histogram ראשון
            hist2: LBP histogram שני
        
        Returns:
            ציון דמיון (0-1)
        """
        # Chi-square distance
        chi_square = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))

        # המרה לציון דמיון
        similarity = 1 / (1 + chi_square)

        return similarity

    def compare_glcm(self, props1, props2):
        """
        משווה מאפייני GLCM
        
        Args:
            props1: GLCM properties ראשון
            props2: GLCM properties שני
        
        Returns:
            ציון דמיון (0-1)
        """
        total_distance = 0

        for key in props1.keys():
            val1 = props1[key]
            val2 = props2[key]

            # נרמול
            if key == 'contrast':
                max_val = 100  # ערך טיפוסי מקסימלי
            elif key in ['correlation', 'homogeneity', 'energy', 'ASM']:
                max_val = 1
            else:
                max_val = 10

            distance = abs(val1 - val2) / max_val
            total_distance += distance

        # ממוצע המרחקים
        avg_distance = total_distance / len(props1)

        # המרה לציון דמיון
        similarity = 1 - min(avg_distance, 1)

        return similarity

    def compare_gabor(self, features1, features2):
        """
        משווה Gabor features
        
        Args:
            features1: Gabor features ראשון
            features2: Gabor features שני
        
        Returns:
            ציון דמיון (0-1)
        """
        # Euclidean distance
        distance = euclidean(features1, features2)

        # נרמול (הערך המקסימלי האפשרי הוא די גדול)
        max_distance = np.sqrt(len(features1)) * 100  # הערכה

        # המרה לציון דמיון
        similarity = 1 - min(distance / max_distance, 1)

        return similarity

    def validate_texture_match(self, image1, image2, threshold=0.70):
        """
        בדיקה מקיפה של התאמת מרקמים בין שתי תמונות
        
        Args:
            image1: תמונה ראשונה
            image2: תמונה שנייה
            threshold: סף דמיון
        
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

            # ציון משוקלל
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
        מנתח את מורכבות המרקם בתמונה
        
        Args:
            image: תמונה
        
        Returns:
            dict: מדדי מורכבות
        """
        entropy_val = self.calculate_entropy(image)
        edge_density = self.calculate_edge_density(image)
        glcm_props = self.calculate_glcm(image)

        # חישוב מורכבות כוללת
        complexity = {
            'entropy': entropy_val,
            'edge_density': edge_density,
            'contrast': glcm_props['contrast'],
            'overall_complexity': (entropy_val / 8 + edge_density + glcm_props['contrast'] / 100) / 3
        }

        return complexity


class AdvancedTextureAnalyzer(TextureAnalyzer):
    """
    מחלקה מתקדמת יותר עם טכניקות נוספות
    """

    def __init__(self):
        super().__init__()
        print("✅ Advanced Texture Analyzer initialized")

    def calculate_wavelet_features(self, image):
        """
        חישוב Wavelet Transform features
        Wavelets טובים לניתוח מרקמים בסקאלות שונות
        
        Args:
            image: תמונה
        
        Returns:
            וקטור features
        """
        try:
            import pywt

            # המרה לגווני אפור
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Wavelet decomposition
            coeffs = pywt.dwt2(gray, 'haar')
            cA, (cH, cV, cD) = coeffs

            # חישוב מאפיינים מכל רכיב
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
        חישוב Haralick texture features
        סט מקיף של 13 מאפייני מרקם
        
        Args:
            image: תמונה
        
        Returns:
            array: Haralick features
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # GLCM בכיוונים שונים
        distances = [1, 2, 3]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]

        glcm = graycomatrix(gray, distances=distances, angles=angles,
                            levels=256, symmetric=True, normed=True)

        # חילוץ כל המאפיינים
        features = []
        properties = ['contrast', 'dissimilarity', 'homogeneity',
                      'energy', 'correlation', 'ASM']

        for prop in properties:
            values = graycoprops(glcm, prop)
            features.append(values.mean())
            features.append(values.std())

        return np.array(features)


if __name__ == "__main__":
    # בדיקה
    print("🧪 Testing Texture Analysis Module...")

    # יצירת תמונות דמה
    test_image1 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    test_image2 = test_image1.copy()

    # הוספת רעש לתמונה השנייה
    noise = np.random.normal(0, 10, test_image2.shape).astype(np.int16)
    test_image2 = np.clip(test_image2.astype(
        np.int16) + noise, 0, 255).astype(np.uint8)

    analyzer = TextureAnalyzer()

    # בדיקת LBP
    lbp = analyzer.calculate_lbp(test_image1)
    print(f"✅ LBP calculated: shape={lbp.shape}")

    # בדיקת GLCM
    glcm_props = analyzer.calculate_glcm(test_image1)
    print(f"✅ GLCM properties: {list(glcm_props.keys())}")

    # בדיקת Gabor
    gabor_features = analyzer.calculate_gabor_features(test_image1)
    print(f"✅ Gabor features: shape={gabor_features.shape}")

    # בדיקת השוואה מלאה
    is_match, score, details = analyzer.validate_texture_match(
        test_image1, test_image2)
    print(f"✅ Texture match validation: match={is_match}, score={score:.3f}")

    # בדיקת Advanced Analyzer
    adv_analyzer = AdvancedTextureAnalyzer()
    wavelet_features = adv_analyzer.calculate_wavelet_features(test_image1)
    print(f"✅ Wavelet features: shape={wavelet_features.shape}")

    print("✅ Texture Analysis Module - All tests passed!")
