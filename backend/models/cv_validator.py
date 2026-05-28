"""
Computer Vision Validator - Updated Version
Combines all algorithms for comprehensive validation with boundary checking
"""

import numpy as np
import cv2
from utils.feature_extraction import FeatureExtractor, MultiModelFeatureExtractor
from utils.color_analysis import ColorAnalyzer
from utils.texture_analysis import TextureAnalyzer
from utils.edge_detection import EdgeAnalyzer
from utils.boundary_matcher import BoundaryMatcher
from models.image_processor import ImageProcessor


class CVValidator:
    """
    Comprehensive validation system combining computer vision and deep learning
    """

    def __init__(self):
        """Initialize all algorithms"""
        print("🚀 Initializing CV Validator...")

        # Deep learning algorithms (PyTorch)
        try:
            self.feature_extractor = FeatureExtractor('resnet50')
            self.has_deep_learning = True
            print("✅ Deep Learning (PyTorch) - Loaded")
        except Exception as e:
            print(f"⚠️ Deep Learning not available: {e}")
            self.feature_extractor = None
            self.has_deep_learning = False

        # Boundary matching (core component)
        self.boundary_matcher = BoundaryMatcher(boundary_width=10)

        # Classical Computer Vision algorithms
        self.color_analyzer = ColorAnalyzer()
        self.texture_analyzer = TextureAnalyzer()
        self.edge_analyzer = EdgeAnalyzer()

        self.semantic_analyzer = None
        self.has_semantic = False

        self.image_processor = ImageProcessor()

        print("✅ CV Validator initialized successfully!")

    def validate(self, puzzle_image, selected_piece, missing_position, threshold=0.75):
        """
        Fast validation (boundary check only)

        Args:
            puzzle_image: the image with the black square
            selected_piece: the piece selected by the user
            missing_position: dict with x, y, width, height
            threshold: similarity threshold

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

    def validate_comprehensive(self, puzzle_image, selected_piece, missing_position, threshold=0.58):
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
            print("Running comprehensive validation...")
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
            print("  Checking boundary matching...")
            _, boundary_conf, boundary_details = self.boundary_matcher.validate_piece_placement(
                puzzle_image, selected_piece, missing_position
            )
            validation_results['boundary'] = {'score': boundary_conf, 'details': boundary_details}
            weights['boundary'] = 0.35
            print(f"    Boundary score: {boundary_conf:.3f}")

            # 2. Semantic deep learning: context region vs full piece - weight 0.35
            # Extract ResNet50 features from the surrounding puzzle context (the region
            # around the hole) and compare them to the full candidate piece.
            # This detects whether the piece semantically belongs here:
            # e.g. an eye matches a face context, but a flower does not.
            if self.has_deep_learning and self.feature_extractor:
                print("  Running semantic deep learning analysis...")
                try:
                    # Use a large margin so the black hole is a small fraction
                    # of the context region and doesn't dominate ResNet50 features.
                    margin = max(50, min(150, h, w))
                    context_region = self._extract_context_region(
                        puzzle_image, missing_position, margin=margin
                    )
                    if context_region.size > 0 and piece_resized.size > 0:
                        ctx_features = self.feature_extractor.extract_features(context_region)
                        piece_features = self.feature_extractor.extract_features(piece_resized)
                        semantic_sim = self.feature_extractor.compare_features(
                            ctx_features, piece_features, method='cosine'
                        )
                        validation_results['semantic'] = {
                            'score': float(semantic_sim),
                            'method': 'resnet50_semantic_context'
                        }
                        weights['semantic'] = 0.35
                        print(f"    Semantic score: {semantic_sim:.3f}")
                    else:
                        validation_results['semantic'] = {'score': 0.0}
                        weights['semantic'] = 0.0
                except Exception as e:
                    print(f"      ⚠️ Semantic deep learning error: {e}")
                    validation_results['semantic'] = {'score': 0.0}
                    weights['semantic'] = 0.0
            else:
                validation_results['semantic'] = {'score': 0.0}
                weights['semantic'] = 0.0

            # 3. Color comparison on boundary strips - weight 0.15
            # Compare the average BGR color of each puzzle strip to the matching piece strip.
            print("  Analyzing colors...")
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
                print(f"    Color score: {color_sim:.3f}")
            except Exception as e:
                validation_results['color'] = {'score': 0.0}
                weights['color'] = 0.0

            # 4. Texture comparison (LBP) on boundary strips - weight 0.10
            # Compare LBP histograms of each puzzle strip to the matching piece strip.
            print("  Analyzing textures...")
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
                print(f"    Texture score: {texture_sim:.3f}")
            except Exception as e:
                validation_results['texture'] = {'score': 0.0}
                weights['texture'] = 0.0

            # 5. Edge density comparison (Canny) on boundary strips - weight 0.05
            # Compare the edge density of each puzzle strip to the matching piece strip.
            print("  Detecting edges...")
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
                print(f"    Edge score: {edge_sim:.3f}")
            except Exception as e:
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

            print(f"  Overall confidence: {confidence:.3f} ({'MATCH' if is_match else 'NO MATCH'})")
            return is_match, confidence, validation_results

        except Exception as e:
            print(f"❌ Error in comprehensive validation: {e}")
            import traceback
            traceback.print_exc()
            return False, 0.0, {}

    def _place_piece_in_image(self, puzzle_image, piece, missing_position):
        """
        Places a piece into the image (for deep learning validation)

        Args:
            puzzle_image: the image with the black square
            piece: the piece
            missing_position: the position

        Returns:
            numpy array: image with the piece placed
        """
        result = puzzle_image.copy()

        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        # Resize the piece
        piece_resized = cv2.resize(piece, (w, h))

        # Place it
        result[y:y+h, x:x+w] = piece_resized

        return result

    def _extract_context_region(self, puzzle_image, missing_position, margin=20):
        """
        Extracts the region surrounding the black square hole

        Args:
            puzzle_image: the image
            missing_position: the position
            margin: margin to extract around the hole

        Returns:
            numpy array: context region
        """
        x = missing_position['x']
        y = missing_position['y']
        w = missing_position['width']
        h = missing_position['height']

        # Compute bounds with margin, clamped to image edges
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(puzzle_image.shape[1], x + w + margin)
        y2 = min(puzzle_image.shape[0], y + h + margin)

        context = puzzle_image[y1:y2, x1:x2]

        return context

