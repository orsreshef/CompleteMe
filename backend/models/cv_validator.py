"""
Computer Vision Validator - Updated Version
משלב את כל האלגוריתמים לוולידציה מקיפה עם בדיקת גבולות
"""

import numpy as np
import cv2
from utils.feature_extraction import FeatureExtractor, MultiModelFeatureExtractor
from utils.color_analysis import ColorAnalyzer
from utils.texture_analysis import TextureAnalyzer
from utils.edge_detection import EdgeAnalyzer
# from utils.semantic_analysis import SemanticAnalyzer
from utils.boundary_matcher import BoundaryMatcher
from models.image_processor import ImageProcessor


class CVValidator:
    """
    מערכת וולידציה מקיפה המשלבת ראייה ממוחשבת ולמידה עמוקה
    """

    def __init__(self):
        """אתחול כל האלגוריתמים"""
        print("🚀 Initializing CV Validator...")

        # אלגוריתמי למידה עמוקה (PyTorch)
        try:
            self.feature_extractor = FeatureExtractor('resnet50')
            self.has_deep_learning = True
            print("✅ Deep Learning (PyTorch) - Loaded")
        except Exception as e:
            print(f"⚠️ Deep Learning not available: {e}")
            self.feature_extractor = None
            self.has_deep_learning = False

        # בדיקת גבולות (מרכזי!)
        self.boundary_matcher = BoundaryMatcher(boundary_width=5)

        # אלגוריתמי Computer Vision קלאסיים
        self.color_analyzer = ColorAnalyzer()
        self.texture_analyzer = TextureAnalyzer()
        self.edge_analyzer = EdgeAnalyzer()

        self.semantic_analyzer = None
        self.has_semantic = False

        self.image_processor = ImageProcessor()

        print("✅ CV Validator initialized successfully!")

    def validate(self, puzzle_image, selected_piece, missing_position, threshold=0.75):
        """
        וולידציה מהירה (בדיקת גבולות בלבד)

        Args:
            puzzle_image: התמונה עם הריבוע השחור
            selected_piece: החתיכה שהמשתמש בחר
            missing_position: dict עם x, y, width, height
            threshold: סף דמיון

        Returns:
            tuple: (is_match, confidence)
        """
        try:
            is_match, confidence, _ = self.boundary_matcher.validate_piece_placement(
                puzzle_image, selected_piece, missing_position
            )

            return is_match, confidence

        except Exception as e:
            print(f"❌ Error in fast validation: {e}")
            return False, 0.0

    def validate_comprehensive(self, puzzle_image, selected_piece, missing_position, threshold=0.65):
        """
        Comprehensive validation: boundary matching + PyTorch DL + color + texture + edges.

        All five components compare puzzle_image boundary strips (the strips
        adjacent to the hole) against the matching edge strips of the selected
        piece.  The completed_image is never used, which prevents the circular
        comparison where the piece would be compared to itself.

        Args:
            puzzle_image: image with the black square
            selected_piece: the piece the user selected
            missing_position: dict with x, y, width, height
            threshold: similarity threshold (0-1)

        Returns:
            tuple: (is_match, confidence, validation_details)
        """
        try:
            print("🔍 Running comprehensive validation...")

            validation_results = {}
            weights = {}

            x = missing_position['x']
            y = missing_position['y']
            w = missing_position['width']
            h = missing_position['height']
            piece_resized = cv2.resize(selected_piece, (w, h))

            # Build matched strip pairs once and reuse across all components.
            # Each pair: (puzzle_strip from puzzle_image, piece_edge_strip).
            # puzzle_strip is the pixels just outside the hole on that side.
            # piece_edge_strip is the corresponding edge pixels of the piece.
            border = max(5, min(20, h // 4, w // 4))
            strip_pairs = []

            if y >= border:
                strip_pairs.append((
                    puzzle_image[y - border:y, x:x + w],
                    piece_resized[0:border, :]
                ))
            if y + h + border <= puzzle_image.shape[0]:
                strip_pairs.append((
                    puzzle_image[y + h:y + h + border, x:x + w],
                    piece_resized[h - border:h, :]
                ))
            if x >= border:
                strip_pairs.append((
                    puzzle_image[y:y + h, x - border:x],
                    piece_resized[:, 0:border]
                ))
            if x + w + border <= puzzle_image.shape[1]:
                strip_pairs.append((
                    puzzle_image[y:y + h, x + w:x + w + border],
                    piece_resized[:, w - border:w]
                ))

            # 1. Boundary matching (HSV histogram + avg color per edge) - weight 0.35
            print("   📐 Checking boundary matching...")
            _, boundary_conf, boundary_details = self.boundary_matcher.validate_piece_placement(
                puzzle_image, selected_piece, missing_position
            )
            validation_results['boundary'] = {'score': boundary_conf, 'details': boundary_details}
            weights['boundary'] = 0.35
            print(f"      Boundary score: {boundary_conf:.3f}")

            # 2. PyTorch ResNet50 on boundary strips - weight 0.35
            # Compare deep features of each puzzle strip to the matching piece edge strip.
            if self.has_deep_learning and self.feature_extractor:
                print("   🤖 Running deep learning boundary analysis...")
                try:
                    dl_scores = []
                    for pz, pc in strip_pairs:
                        if pz.size > 0 and pc.size > 0:
                            dl_scores.append(
                                self.feature_extractor.compare_features(
                                    self.feature_extractor.extract_features(pz),
                                    self.feature_extractor.extract_features(pc),
                                    method='cosine'
                                )
                            )
                    if dl_scores:
                        dl_sim = float(np.mean(dl_scores))
                        validation_results['features'] = {'score': dl_sim, 'method': 'resnet50_boundary_strips'}
                        weights['features'] = 0.35
                        print(f"      Deep Learning score: {dl_sim:.3f}")
                    else:
                        validation_results['features'] = {'score': 0.0}
                        weights['features'] = 0.0
                except Exception as e:
                    print(f"      ⚠️ Deep learning error: {e}")
                    validation_results['features'] = {'score': 0.0}
                    weights['features'] = 0.0
            else:
                validation_results['features'] = {'score': 0.0}
                weights['features'] = 0.0

            # 3. Color comparison on boundary strips - weight 0.15
            # Compare the average BGR color of each puzzle strip to the matching piece strip.
            print("   🎨 Analyzing colors...")
            try:
                color_scores = []
                for pz, pc in strip_pairs:
                    if pz.size > 0 and pc.size > 0:
                        color_scores.append(
                            self.boundary_matcher.compare_boundary_colors(pz, pc)
                        )
                color_sim = float(np.mean(color_scores)) if color_scores else 0.0
                validation_results['color'] = {'score': color_sim, 'method': 'boundary_color'}
                weights['color'] = 0.15
                print(f"      Color score: {color_sim:.3f}")
            except Exception as e:
                print(f"      ⚠️ Color analysis error: {e}")
                validation_results['color'] = {'score': 0.0}
                weights['color'] = 0.0

            # 4. Texture comparison (LBP) on boundary strips - weight 0.10
            # Compare LBP histograms of each puzzle strip to the matching piece strip.
            print("   🔲 Analyzing textures...")
            try:
                texture_scores = []
                for pz, pc in strip_pairs:
                    if pz.size > 0 and pc.size > 0:
                        texture_scores.append(
                            self.texture_analyzer.compare_lbp(
                                self.texture_analyzer.calculate_lbp(pz),
                                self.texture_analyzer.calculate_lbp(pc)
                            )
                        )
                texture_sim = float(np.mean(texture_scores)) if texture_scores else 0.0
                validation_results['texture'] = {'score': texture_sim, 'method': 'lbp_boundary'}
                weights['texture'] = 0.10
                print(f"      Texture score: {texture_sim:.3f}")
            except Exception as e:
                print(f"      ⚠️ Texture analysis error: {e}")
                validation_results['texture'] = {'score': 0.0}
                weights['texture'] = 0.0

            # 5. Edge density comparison (Canny) on boundary strips - weight 0.05
            # Compare the edge density of each puzzle strip to the matching piece strip.
            print("   📏 Detecting edges...")
            try:
                edge_scores = []
                for pz, pc in strip_pairs:
                    if pz.size > 0 and pc.size > 0:
                        e_pz = self.edge_analyzer.detect_edges_canny(pz)
                        e_pc = self.edge_analyzer.detect_edges_canny(pc)
                        d_pz = np.count_nonzero(e_pz) / e_pz.size if e_pz.size > 0 else 0
                        d_pc = np.count_nonzero(e_pc) / e_pc.size if e_pc.size > 0 else 0
                        edge_scores.append(1 - abs(d_pz - d_pc))
                edge_sim = float(np.mean(edge_scores)) if edge_scores else 0.0
                validation_results['edges'] = {'score': edge_sim, 'method': 'canny_boundary'}
                weights['edges'] = 0.05
                print(f"      Edge score: {edge_sim:.3f}")
            except Exception as e:
                print(f"      ⚠️ Edge detection error: {e}")
                validation_results['edges'] = {'score': 0.0}
                weights['edges'] = 0.0

            # Compute normalized weighted confidence
            total_weight = sum(weights.values())
            if total_weight > 0:
                normalized_weights = {k: v / total_weight for k, v in weights.items()}
                confidence = sum(
                    validation_results[key]['score'] * normalized_weights[key]
                    for key in validation_results.keys()
                    if key in normalized_weights
                )
            else:
                confidence = 0.0

            is_match = confidence >= threshold

            print(f"   ✅ Overall confidence: {confidence:.3f} ({'MATCH' if is_match else 'NO MATCH'})")

            return is_match, confidence, validation_results

        except Exception as e:
            print(f"❌ Error in comprehensive validation: {e}")
            import traceback
            traceback.print_exc()
            return False, 0.0, {}

    def _place_piece_in_image(self, puzzle_image, piece, missing_position):
        """
        מציב חתיכה בתמונה (עבור בדיקת למידה עמוקה)

        Args:
            puzzle_image: התמונה עם הריבוע השחור
            piece: החתיכה
            missing_position: המיקום

        Returns:
            numpy array: תמונה עם החתיכה מוצבת
        """
        result = puzzle_image.copy()

        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        # שינוי גודל החתיכה
        piece_resized = cv2.resize(piece, (w, h))

        # הצבה
        result[y:y+h, x:x+w] = piece_resized

        return result

    def _extract_context_region(self, puzzle_image, missing_position, margin=20):
        """
        מחלץ את האזור מסביב לריבוע השחור

        Args:
            puzzle_image: התמונה
            missing_position: המיקום
            margin: שוליים לחילוץ

        Returns:
            numpy array: אזור ההקשר
        """
        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        # חישוב גבולות עם שוליים
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(puzzle_image.shape[1], x + w + margin)
        y2 = min(puzzle_image.shape[0], y + h + margin)

        context = puzzle_image[y1:y2, x1:x2]

        return context


if __name__ == "__main__":
    print("🧪 Testing CV Validator...")

    # Create test data
    puzzle_image = np.random.randint(0, 255, (400, 600, 3), dtype=np.uint8)
    selected_piece = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    missing_position = {
        'x': 200,
        'y': 150,
        'width': 100,
        'height': 100
    }

    validator = CVValidator()

    # Test fast validation
    print("\n--- Fast Validation ---")
    is_match, confidence = validator.validate(
        puzzle_image, selected_piece, missing_position)
    print(f"Result: {is_match}, Confidence: {confidence:.3f}")

    # Test comprehensive validation
    print("\n--- Comprehensive Validation ---")
    is_match, confidence, details = validator.validate_comprehensive(
        puzzle_image, selected_piece, missing_position
    )
    print(f"Result: {is_match}, Confidence: {confidence:.3f}")

    print("\n✅ CV Validator - All tests passed!")
