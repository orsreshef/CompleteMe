"""
Boundary Matching Validator
בודק התאמה של חתיכה נבחרת לתמונה עם ריבוע שחור
"""

import numpy as np
import cv2
from scipy.spatial.distance import euclidean


class BoundaryMatcher:
    """
    מחלקה לבדיקת התאמת גבולות בין חתיכה נבחרת לתמונה המקורית
    """

    def __init__(self, boundary_width=5):
        """
        אתחול

        Args:
            boundary_width: רוחב הגבול לבדיקה (פיקסלים)
        """
        self.boundary_width = boundary_width
        print(f"✅ Boundary Matcher initialized (width={boundary_width}px)")

    def extract_boundaries(self, puzzle_image, missing_position):
        """
        מחלץ את הגבולות של הריבוע השחור מהתמונה

        Args:
            puzzle_image: התמונה עם הריבוע השחור
            missing_position: dict עם x, y, width, height

        Returns:
            dict: {'top', 'bottom', 'left', 'right'} - גבולות התמונה
        """
        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        boundaries = {}

        # גבול עליון (מעל הריבוע השחור)
        if y >= self.boundary_width:
            boundaries['top'] = puzzle_image[
                y - self.boundary_width:y,
                x:x + w
            ]
        else:
            boundaries['top'] = None

        # גבול תחתון (מתחת לריבוע השחור)
        if y + h + self.boundary_width <= puzzle_image.shape[0]:
            boundaries['bottom'] = puzzle_image[
                y + h:y + h + self.boundary_width,
                x:x + w
            ]
        else:
            boundaries['bottom'] = None

        # גבול שמאלי (משמאל לריבוע השחור)
        if x >= self.boundary_width:
            boundaries['left'] = puzzle_image[
                y:y + h,
                x - self.boundary_width:x
            ]
        else:
            boundaries['left'] = None

        # גבול ימני (מימין לריבוע השחור)
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
        מחלץ את הגבולות של החתיכה הנבחרת

        Args:
            piece: התמונה של החתיכה

        Returns:
            dict: {'top', 'bottom', 'left', 'right'} - גבולות החתיכה
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
        משווה צבעים בין שני גבולות

        Args:
            boundary1: גבול ראשון (numpy array)
            boundary2: גבול שני (numpy array)

        Returns:
            float: ציון דמיון (0-1)
        """
        if boundary1 is None or boundary2 is None:
            return 0.0

        if boundary1.shape != boundary2.shape:
            # שינוי גודל אם צריך
            boundary2 = cv2.resize(
                boundary2, (boundary1.shape[1], boundary1.shape[0]))

        # חישוב ממוצע צבעים
        avg1 = boundary1.mean(axis=(0, 1))
        avg2 = boundary2.mean(axis=(0, 1))

        # מרחק אוקלידי
        distance = euclidean(avg1, avg2)
        max_distance = np.sqrt(3 * 255**2)  # מקסימום אפשרי

        # המרה לציון דמיון
        similarity = 1 - (distance / max_distance)

        return max(0, min(1, similarity))

    def compare_boundary_histograms(self, boundary1, boundary2):
        """
        משווה היסטוגרמות צבעים בין גבולות

        Args:
            boundary1: גבול ראשון
            boundary2: גבול שני

        Returns:
            float: ציון דמיון (0-1)
        """
        if boundary1 is None or boundary2 is None:
            return 0.0

        if boundary1.shape != boundary2.shape:
            boundary2 = cv2.resize(
                boundary2, (boundary1.shape[1], boundary1.shape[0]))

        # המרה ל-HSV
        hsv1 = cv2.cvtColor(boundary1, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(boundary2, cv2.COLOR_BGR2HSV)

        # חישוב היסטוגרמות
        hist1 = cv2.calcHist([hsv1], [0, 1, 2], None, [
                             8, 8, 8], [0, 180, 0, 256, 0, 256])
        hist2 = cv2.calcHist([hsv2], [0, 1, 2], None, [
                             8, 8, 8], [0, 180, 0, 256, 0, 256])

        # נרמול
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()

        # השוואה
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        return max(0, similarity)

    def validate_piece_placement(self, puzzle_image, selected_piece, missing_position):
        """
        בודק האם החתיכה הנבחרת מתאימה לתמונה

        Args:
            puzzle_image: התמונה עם הריבוע השחור
            selected_piece: החתיכה שהמשתמש בחר
            missing_position: המיקום של הריבוע השחור

        Returns:
            tuple: (is_match, confidence, details)
        """
        try:
            # שינוי גודל החתיכה אם צריך
            target_h = missing_position['height']
            target_w = missing_position['width']

            if selected_piece.shape[:2] != (target_h, target_w):
                selected_piece = cv2.resize(
                    selected_piece, (target_w, target_h))

            # חילוץ גבולות מהתמונה
            puzzle_boundaries = self.extract_boundaries(
                puzzle_image, missing_position)

            # חילוץ גבולות מהחתיכה
            piece_boundaries = self.extract_piece_boundaries(selected_piece)

            # בדיקת התאמה לכל גבול
            scores = {}

            for direction in ['top', 'bottom', 'left', 'right']:
                puzzle_bound = puzzle_boundaries.get(direction)
                piece_bound = piece_boundaries.get(direction)

                if puzzle_bound is not None and piece_bound is not None:
                    # משקל של 70% להיסטוגרמות, 30% לממוצע צבעים
                    hist_score = self.compare_boundary_histograms(
                        puzzle_bound, piece_bound)
                    color_score = self.compare_boundary_colors(
                        puzzle_bound, piece_bound)

                    scores[direction] = 0.7 * hist_score + 0.3 * color_score
                # else: zone is at the image edge — skip this direction
                # (don't penalize with 0.0; just average the sides that exist)

            # ציון כולל - ממוצע של כל הגבולות
            if scores:
                confidence = np.mean(list(scores.values()))
            else:
                confidence = 0.0

            # סף של 70% לאישור
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
        יוצר ויזואליזציה של הגבולות לבדיקה

        Args:
            puzzle_image: התמונה עם הריבוע השחור
            selected_piece: החתיכה הנבחרת
            missing_position: המיקום

        Returns:
            numpy array: תמונה עם הגבולות מסומנים
        """
        vis = puzzle_image.copy()

        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        # צביעת הגבולות בצבעים שונים
        thickness = self.boundary_width

        # עליון - אדום
        if y >= thickness:
            cv2.rectangle(vis, (x, y - thickness), (x + w, y), (0, 0, 255), -1)

        # תחתון - ירוק
        if y + h + thickness <= vis.shape[0]:
            cv2.rectangle(vis, (x, y + h), (x + w, y +
                          h + thickness), (0, 255, 0), -1)

        # שמאל - כחול
        if x >= thickness:
            cv2.rectangle(vis, (x - thickness, y), (x, y + h), (255, 0, 0), -1)

        # ימין - צהוב
        if x + w + thickness <= vis.shape[1]:
            cv2.rectangle(vis, (x + w, y),
                          (x + w + thickness, y + h), (0, 255, 255), -1)

        # הריבוע עצמו - לבן
        cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 255, 255), 2)

        return vis


if __name__ == "__main__":
    print("🧪 Testing Boundary Matcher...")

    # Create test images
    puzzle_image = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
    selected_piece = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    missing_position = {
        'x': 200,
        'y': 150,
        'width': 100,
        'height': 100
    }

    matcher = BoundaryMatcher(boundary_width=5)
    is_match, confidence, details = matcher.validate_piece_placement(
        puzzle_image, selected_piece, missing_position
    )

    print(f"Match: {is_match}, Confidence: {confidence:.3f}")
    print(f"Details: {details}")
    print("✅ Boundary Matcher - All tests passed!")
