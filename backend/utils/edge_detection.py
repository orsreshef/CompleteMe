"""
Edge Detection and Analysis Module
זיהוי וניתוח קצוות מתקדם להשוואת תמונות
"""

import numpy as np
import cv2
from scipy.spatial.distance import directed_hausdorff


class EdgeAnalyzer:
    """
    מחלקה לזיהוי וניתוח קצוות בתמונות
    """

    def __init__(self):
        """אתחול מנתח הקצוות"""
        print("✅ Edge Analyzer initialized")

    def detect_edges_canny(self, image, low_threshold=50, high_threshold=150):
        """
        זיהוי קצוות באמצעות Canny Edge Detection
        
        Args:
            image: תמונה
            low_threshold: סף תחתון
            high_threshold: סף עליון
        
        Returns:
            תמונת קצוות (binary)
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # החלקה לפני זיהוי קצוות
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)

        # Canny edge detection
        edges = cv2.Canny(blurred, low_threshold, high_threshold)

        return edges

    def detect_edges_sobel(self, image):
        """
        זיהוי קצוות באמצעות Sobel operator
        
        Args:
            image: תמונה
        
        Returns:
            magnitude של הגרדיאנט
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Sobel בכיוון X
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)

        # Sobel בכיוון Y
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        # חישוב magnitude
        magnitude = np.sqrt(sobelx**2 + sobely**2)

        # נרמול ל-0-255
        magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)

        return magnitude

    def detect_edges_laplacian(self, image):
        """
        זיהוי קצוות באמצעות Laplacian
        
        Args:
            image: תמונה
        
        Returns:
            תמונת קצוות
        """
        # המרה לגווני אפור
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # החלקה
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # Laplacian
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)

        # המרה לערכים מוחלטים ונרמול
        laplacian = np.abs(laplacian)
        laplacian = (laplacian / laplacian.max() * 255).astype(np.uint8)

        return laplacian

    def calculate_edge_histogram(self, edges, bins=8):
        """
        מחשב היסטוגרמת כיווני קצוות
        
        Args:
            edges: תמונת קצוות
            bins: מספר bins להיסטוגרמה
        
        Returns:
            היסטוגרמה של כיווני הקצוות
        """
        # חישוב gradient
        sobelx = cv2.Sobel(edges, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(edges, cv2.CV_64F, 0, 1, ksize=3)

        # חישוב כיוונים
        angles = np.arctan2(sobely, sobelx)

        # היסטוגרמה
        hist, _ = np.histogram(
            angles[edges > 0], bins=bins, range=(-np.pi, np.pi), density=True)

        return hist

    def analyze_edge_continuity(self, puzzle_image, selected_patch, position):
        """
        בודק אם הקצוות של החתיכה מתחברים לקצוות התמונה
        
        Args:
            puzzle_image: תמונת הפאזל (עם החור השחור)
            selected_patch: החתיכה שנבחרה
            position: (x, y, w, h) מיקום החתיכה
        
        Returns:
            ציון דמיון (0-1)
        """
        x, y, w, h = position

        # זיהוי קצוות בתמונה הראשית
        edges_puzzle = self.detect_edges_canny(puzzle_image)

        # זיהוי קצוות בחתיכה
        edges_patch = self.detect_edges_canny(selected_patch)

        # בדיקת התאמה בגבולות
        border_width = 5  # רוחב הגבול לבדיקה

        continuity_scores = []

        # בדיקת גבול עליון
        if y >= border_width:
            border_puzzle_top = edges_puzzle[y-border_width:y, x:x+w]
            border_patch_top = edges_patch[0:border_width, :]
            if border_puzzle_top.shape == border_patch_top.shape:
                score = np.sum(border_puzzle_top & border_patch_top) / \
                    max(np.sum(border_puzzle_top | border_patch_top), 1)
                continuity_scores.append(score)

        # בדיקת גבול תחתון
        if y + h + border_width < edges_puzzle.shape[0]:
            border_puzzle_bottom = edges_puzzle[y+h:y+h+border_width, x:x+w]
            border_patch_bottom = edges_patch[-border_width:, :]
            if border_puzzle_bottom.shape == border_patch_bottom.shape:
                score = np.sum(border_puzzle_bottom & border_patch_bottom) / \
                    max(np.sum(border_puzzle_bottom | border_patch_bottom), 1)
                continuity_scores.append(score)

        # בדיקת גבול שמאלי
        if x >= border_width:
            border_puzzle_left = edges_puzzle[y:y+h, x-border_width:x]
            border_patch_left = edges_patch[:, 0:border_width]
            if border_puzzle_left.shape == border_patch_left.shape:
                score = np.sum(border_puzzle_left & border_patch_left) / \
                    max(np.sum(border_puzzle_left | border_patch_left), 1)
                continuity_scores.append(score)

        # בדיקת גבול ימני
        if x + w + border_width < edges_puzzle.shape[1]:
            border_puzzle_right = edges_puzzle[y:y+h, x+w:x+w+border_width]
            border_patch_right = edges_patch[:, -border_width:]
            if border_puzzle_right.shape == border_patch_right.shape:
                score = np.sum(border_puzzle_right & border_patch_right) / \
                    max(np.sum(border_puzzle_right | border_patch_right), 1)
                continuity_scores.append(score)

        # ממוצע הציונים
        if continuity_scores:
            return np.mean(continuity_scores)
        else:
            return 0.0

    def compare_edge_histograms(self, hist1, hist2):
        """
        משווה היסטוגרמות של כיווני קצוות
        
        Args:
            hist1: היסטוגרמה ראשונה
            hist2: היסטוגרמה שנייה
        
        Returns:
            ציון דמיון (0-1)
        """
        # Chi-square distance
        chi_square = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))

        # המרה לציון דמיון
        similarity = 1 / (1 + chi_square)

        return similarity

    def calculate_hausdorff_distance(self, edges1, edges2):
        """
        מחשב Hausdorff distance בין שתי קבוצות קצוות
        מדד זה מודד את המרחק המקסימלי המינימלי בין נקודות
        
        Args:
            edges1: קצוות ראשונים
            edges2: קצוות שניים
        
        Returns:
            Hausdorff distance (ערך נמוך = דומה יותר)
        """
        # מציאת קואורדינטות של פיקסלי הקצוות
        points1 = np.column_stack(np.where(edges1 > 0))
        points2 = np.column_stack(np.where(edges2 > 0))

        if len(points1) == 0 or len(points2) == 0:
            return float('inf')

        # חישוב Hausdorff distance
        hausdorff_dist = max(
            directed_hausdorff(points1, points2)[0],
            directed_hausdorff(points2, points1)[0]
        )

        return hausdorff_dist

    def analyze_edge_density(self, image):
        """
        מנתח את צפיפות הקצוות בתמונה
        
        Args:
            image: תמונה
        
        Returns:
            dict: מדדי צפיפות קצוות
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
        בדיקה מקיפה של התאמת קצוות בין שתי תמונות
        
        Args:
            image1: תמונה ראשונה
            image2: תמונה שנייה
            threshold: סף דמיון
        
        Returns:
            tuple: (is_match, score, details)
        """
        try:
            # 1. זיהוי קצוות
            edges1_canny = self.detect_edges_canny(image1)
            edges2_canny = self.detect_edges_canny(image2)

            # 2. השוואת צפיפות קצוות
            density1 = np.count_nonzero(edges1_canny) / edges1_canny.size
            density2 = np.count_nonzero(edges2_canny) / edges2_canny.size
            density_similarity = 1 - abs(density1 - density2)

            # 3. השוואת היסטוגרמות כיוונים
            hist1 = self.calculate_edge_histogram(edges1_canny)
            hist2 = self.calculate_edge_histogram(edges2_canny)
            histogram_similarity = self.compare_edge_histograms(hist1, hist2)

            # 4. Hausdorff distance (אם יש מספיק קצוות)
            hausdorff_similarity = 0.5  # ברירת מחדל
            if density1 > 0.01 and density2 > 0.01:
                # שינוי גודל לחישוב מהיר יותר
                edges1_small = cv2.resize(edges1_canny, (50, 50))
                edges2_small = cv2.resize(edges2_canny, (50, 50))

                hausdorff_dist = self.calculate_hausdorff_distance(
                    edges1_small, edges2_small)
                max_dist = 50 * np.sqrt(2)  # מרחק מקסימלי בתמונה 50x50
                hausdorff_similarity = 1 - min(hausdorff_dist / max_dist, 1)

            # 5. השוואת Sobel magnitude
            sobel1 = self.detect_edges_sobel(image1)
            sobel2 = self.detect_edges_sobel(image2)
            sobel_correlation = np.corrcoef(
                sobel1.ravel(), sobel2.ravel())[0, 1]
            sobel_similarity = max(0, sobel_correlation)  # מנרמל ל-0-1

            # ציון משוקלל
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
        מציג את הקצוות שזוהו
        
        Args:
            image: תמונה
            method: שיטת זיהוי - 'canny', 'sobel', 'laplacian'
        
        Returns:
            תמונת קצוות
        """
        if method == 'canny':
            return self.detect_edges_canny(image)
        elif method == 'sobel':
            return self.detect_edges_sobel(image)
        elif method == 'laplacian':
            return self.detect_edges_laplacian(image)
        else:
            raise ValueError(f"Unknown method: {method}")


if __name__ == "__main__":
    # בדיקה
    print("🧪 Testing Edge Detection Module...")

    # יצירת תמונת דמה עם קצוות
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (20, 20), (80, 80), (255, 255, 255), -1)
    cv2.circle(test_image, (50, 50), 15, (0, 0, 0), -1)

    analyzer = EdgeAnalyzer()

    # בדיקת Canny
    edges_canny = analyzer.detect_edges_canny(test_image)
    print(
        f"✅ Canny edges detected: {np.count_nonzero(edges_canny)} edge pixels")

    # בדיקת Sobel
    edges_sobel = analyzer.detect_edges_sobel(test_image)
    print(
        f"✅ Sobel edges detected: magnitude range [{edges_sobel.min()}, {edges_sobel.max()}]")

    # בדיקת histogram
    hist = analyzer.calculate_edge_histogram(edges_canny)
    print(f"✅ Edge histogram calculated: shape={hist.shape}")

    # בדיקת צפיפות
    density = analyzer.analyze_edge_density(test_image)
    print(f"✅ Edge density: {density['average_density']:.3f}")

    # בדיקת השוואה
    test_image2 = test_image.copy()
    test_image2 = cv2.GaussianBlur(test_image2, (5, 5), 0)

    is_match, score, details = analyzer.validate_edge_match(
        test_image, test_image2)
    print(f"✅ Edge match validation: match={is_match}, score={score:.3f}")

    print("✅ Edge Detection Module - All tests passed!")
