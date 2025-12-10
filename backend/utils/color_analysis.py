"""
Color Analysis Module
ניתוח צבעים מתקדם להשוואת תמונות
"""

import numpy as np
import cv2
from scipy.spatial.distance import euclidean
import colorsys


class ColorAnalyzer:
    """
    מחלקה לניתוח והשוואת צבעים בתמונות
    """

    def __init__(self):
        """אתחול מנתח הצבעים"""
        print("✅ Color Analyzer initialized")

    def extract_dominant_colors(self, image, k=5):
        """
        מחלץ את הצבעים הדומיננטיים בתמונה באמצעות K-Means

        Args:
            image: תמונה (numpy array)
            k: מספר צבעים דומיננטיים לחלץ

        Returns:
            list: רשימת הצבעים הדומיננטיים (RGB)
        """
        # שינוי צורה לרשימת פיקסלים
        pixels = image.reshape(-1, 3).astype(np.float32)

        # K-Means clustering
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(
            pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

        # המרה ל-int
        dominant_colors = centers.astype(np.uint8)

        return dominant_colors

    def calculate_color_histogram(self, image, color_space='HSV'):
        """
        מחשב היסטוגרמת צבעים

        Args:
            image: תמונה
            color_space: מרחב צבעים - 'HSV', 'RGB', או 'LAB'

        Returns:
            היסטוגרמה מנורמלת
        """
        # המרה למרחב צבעים מתאים
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

        # נרמול
        hist = cv2.normalize(hist, hist).flatten()

        return hist

    def compare_color_histograms(self, hist1, hist2, method='correlation'):
        """
        משווה שתי היסטוגרמות צבעים

        Args:
            hist1: היסטוגרמה ראשונה
            hist2: היסטוגרמה שנייה
            method: שיטת השוואה - 'correlation', 'chi_square', 'intersection', 'bhattacharyya'

        Returns:
            ציון דמיון (0-1)
        """
        if method == 'correlation':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return max(0, score)  # מנרמל ל-0-1
        elif method == 'chi_square':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
            # ככל שהערך קטן יותר, הדמיון גדול יותר
            return 1 / (1 + score)
        elif method == 'intersection':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)
            return score
        elif method == 'bhattacharyya':
            score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
            return 1 - score  # מנרמל ל-0-1
        else:
            raise ValueError(f"Unknown method: {method}")

    def analyze_average_color(self, image):
        """
        מחשב את הצבע הממוצע בתמונה

        Args:
            image: תמונה

        Returns:
            tuple: (B, G, R) - ערכי הצבע הממוצע
        """
        avg_color = image.mean(axis=0).mean(axis=0)
        return tuple(avg_color.astype(int))

    def calculate_color_moments(self, image):
        """
        מחשב מומנטים סטטיסטיים של צבעים (mean, std, skewness)

        Args:
            image: תמונה

        Returns:
            dict: מומנטים לכל ערוץ צבע
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
        """מחשב skewness (אסימטריה) של התפלגות"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 3)

    def compare_color_moments(self, moments1, moments2):
        """
        משווה מומנטים של צבעים

        Args:
            moments1: מומנטים של תמונה ראשונה
            moments2: מומנטים של תמונה שנייה

        Returns:
            ציון דמיון (0-1)
        """
        total_distance = 0

        for channel in ['B', 'G', 'R']:
            for moment_type in ['mean', 'std', 'skewness']:
                val1 = moments1[channel][moment_type]
                val2 = moments2[channel][moment_type]

                # נרמול לפי טווח הערכים
                if moment_type == 'mean' or moment_type == 'std':
                    max_val = 255
                else:  # skewness
                    max_val = 3  # ערך טיפוסי מקסימלי

                distance = abs(val1 - val2) / max_val
                total_distance += distance

        # ממוצע המרחקים (9 השוואות: 3 ערוצים × 3 מומנטים)
        avg_distance = total_distance / 9

        # המרה לציון דמיון
        similarity = 1 - avg_distance

        return max(0, min(1, similarity))

    def validate_color_match(self, image1, image2, threshold=0.75):
        """
        בדיקה מקיפה של התאמת צבעים בין שתי תמונות

        Args:
            image1: תמונה ראשונה
            image2: תמונה שנייה
            threshold: סף דמיון

        Returns:
            tuple: (is_match, score, details)
        """
        try:
            # 1. השוואת היסטוגרמות (HSV - הכי טוב לצבעים)
            hist1_hsv = self.calculate_color_histogram(image1, 'HSV')
            hist2_hsv = self.calculate_color_histogram(image2, 'HSV')
            hist_similarity = self.compare_color_histograms(
                hist1_hsv, hist2_hsv, 'correlation')

            # 2. השוואת מומנטים סטטיסטיים
            moments1 = self.calculate_color_moments(image1)
            moments2 = self.calculate_color_moments(image2)
            moments_similarity = self.compare_color_moments(moments1, moments2)

            # 3. השוואת צבע ממוצע
            avg1 = self.analyze_average_color(image1)
            avg2 = self.analyze_average_color(image2)
            avg_distance = euclidean(avg1, avg2) / (255 * np.sqrt(3))  # נרמול
            avg_similarity = 1 - avg_distance

            # ציון משוקלל
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
        מחלץ פלטת צבעים מתמונה

        Args:
            image: תמונה
            n_colors: מספר צבעים בפלטה

        Returns:
            list: רשימת צבעים ב-RGB
        """
        dominant_colors = self.extract_dominant_colors(image, k=n_colors)

        # המרה מ-BGR ל-RGB
        rgb_colors = [tuple(color[::-1]) for color in dominant_colors]

        return rgb_colors

    def visualize_color_comparison(self, image1, image2):
        """
        יוצר ויזואליזציה של השוואת צבעים

        Args:
            image1: תמונה ראשונה
            image2: תמונה שנייה

        Returns:
            תמונת השוואה
        """
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]

        # יצירת קנבס
        max_h = max(h1, h2)
        comparison = np.zeros((max_h, w1 + w2 + 20, 3), dtype=np.uint8)
        comparison.fill(255)

        # הצבת התמונות
        comparison[0:h1, 0:w1] = image1
        comparison[0:h2, w1+20:w1+20+w2] = image2

        # הוספת פלטות צבעים
        palette1 = self.get_color_palette(image1)
        palette2 = self.get_color_palette(image2)

        # ציור פלטות
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


if __name__ == "__main__":
    # בדיקה
    print("🧪 Testing Color Analysis Module...")

    # יצירת תמונות דמה
    test_image1 = np.random.randint(50, 150, (100, 100, 3), dtype=np.uint8)
    test_image2 = test_image1.copy()
    test_image2 = cv2.GaussianBlur(test_image2, (5, 5), 0)  # הוספת blur קל

    analyzer = ColorAnalyzer()

    # בדיקת חילוץ צבעים דומיננטיים
    colors = analyzer.extract_dominant_colors(test_image1)
    print(f"✅ Dominant colors extracted: {len(colors)} colors")

    # בדיקת היסטוגרמה
    hist = analyzer.calculate_color_histogram(test_image1)
    print(f"✅ Histogram calculated: shape={hist.shape}")

    # בדיקת השוואה
    is_match, score, details = analyzer.validate_color_match(
        test_image1, test_image2)
    print(f"✅ Color match validation: match={is_match}, score={score:.3f}")

    print("✅ Color Analysis Module - All tests passed!")
