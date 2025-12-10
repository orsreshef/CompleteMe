"""
Computer Vision Validator Module
Integrated validation system combining all CV techniques
"""

import numpy as np
import cv2
from utils.feature_extraction import FeatureExtractor, MultiModelFeatureExtractor
from utils.color_analysis import ColorAnalyzer
from utils.texture_analysis import TextureAnalyzer
from utils.edge_detection import EdgeAnalyzer
from utils.semantic_analysis import SemanticAnalyzer, AdvancedSemanticAnalyzer
from .image_processor import ImageProcessor


class CVValidator:
    """
    Comprehensive Computer Vision Validator
    Combines multiple CV techniques for robust image matching
    """

    def __init__(self, use_ensemble=True, verbose=True):
        """
        Initialize the CV Validator with all analysis modules

        Args:
            use_ensemble: whether to use ensemble feature extraction
            verbose: whether to print detailed information
        """
        self.verbose = verbose

        if self.verbose:
            print("🔄 Initializing Computer Vision Validator...")

        # Initialize all analyzers
        if use_ensemble:
            self.feature_extractor = MultiModelFeatureExtractor()
        else:
            self.feature_extractor = FeatureExtractor('resnet50')

        self.color_analyzer = ColorAnalyzer()
        self.texture_analyzer = TextureAnalyzer()
        self.edge_analyzer = EdgeAnalyzer()
        self.semantic_analyzer = AdvancedSemanticAnalyzer()
        self.image_processor = ImageProcessor()

        self.use_ensemble = use_ensemble

        if self.verbose:
            print("✅ Computer Vision Validator ready!")

    def preprocess_images(self, image1, image2):
        """
        Preprocess both images for consistent analysis

        Args:
            image1: first image
            image2: second image

        Returns:
            tuple: (processed_image1, processed_image2)
        """
        # Normalize both images
        img1 = self.image_processor.normalize_image(image1)
        img2 = self.image_processor.normalize_image(image2)

        # Resize to same dimensions if needed
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]

        if (h1, w1) != (h2, w2):
            # Resize second image to match first
            img2 = cv2.resize(img2, (w1, h1), interpolation=cv2.INTER_AREA)

        return img1, img2

    def validate_comprehensive(self, original_patch, selected_patch, weights=None):
        """
        Comprehensive validation using all CV techniques

        Args:
            original_patch: the correct piece from original image
            selected_patch: the piece selected by user
            weights: dict of weights for each validation method

        Returns:
            tuple: (is_match, final_score, detailed_results)
        """
        if weights is None:
            # Default weights (can be tuned)
            weights = {
                'features': 0.30,      # Deep features - most important
                'color': 0.25,         # Color analysis
                'texture': 0.20,       # Texture analysis
                'edges': 0.15,         # Edge analysis
                'semantic': 0.10       # Semantic understanding
            }

        # Preprocess images
        img1, img2 = self.preprocess_images(original_patch, selected_patch)

        if self.verbose:
            print("\n🔍 Starting comprehensive validation...")

        results = {}

        # 1. Feature-based validation (Deep Learning)
        try:
            if self.use_ensemble:
                is_feat_match, feat_score, feat_details = \
                    self.feature_extractor.validate_match_ensemble(img1, img2)
            else:
                is_feat_match, feat_score = \
                    self.feature_extractor.validate_match(img1, img2)
                feat_details = {}

            results['features'] = {
                'score': feat_score,
                'is_match': is_feat_match,
                'details': feat_details
            }
            if self.verbose:
                print(f"   ✓ Features: {feat_score:.3f}")
        except Exception as e:
            print(f"   ✗ Features failed: {e}")
            results['features'] = {'score': 0.0, 'is_match': False}

        # 2. Color analysis
        try:
            is_color_match, color_score, color_details = \
                self.color_analyzer.validate_color_match(img1, img2)

            results['color'] = {
                'score': color_score,
                'is_match': is_color_match,
                'details': color_details
            }
            if self.verbose:
                print(f"   ✓ Color: {color_score:.3f}")
        except Exception as e:
            print(f"   ✗ Color failed: {e}")
            results['color'] = {'score': 0.0, 'is_match': False}

        # 3. Texture analysis
        try:
            is_texture_match, texture_score, texture_details = \
                self.texture_analyzer.validate_texture_match(img1, img2)

            results['texture'] = {
                'score': texture_score,
                'is_match': is_texture_match,
                'details': texture_details
            }
            if self.verbose:
                print(f"   ✓ Texture: {texture_score:.3f}")
        except Exception as e:
            print(f"   ✗ Texture failed: {e}")
            results['texture'] = {'score': 0.0, 'is_match': False}

        # 4. Edge analysis
        try:
            is_edge_match, edge_score, edge_details = \
                self.edge_analyzer.validate_edge_match(img1, img2)

            results['edges'] = {
                'score': edge_score,
                'is_match': is_edge_match,
                'details': edge_details
            }
            if self.verbose:
                print(f"   ✓ Edges: {edge_score:.3f}")
        except Exception as e:
            print(f"   ✗ Edges failed: {e}")
            results['edges'] = {'score': 0.0, 'is_match': False}

        # 5. Semantic analysis
        try:
            is_semantic_match, semantic_score, semantic_details = \
                self.semantic_analyzer.validate_contextual_match(img1, img2)

            results['semantic'] = {
                'score': semantic_score,
                'is_match': is_semantic_match,
                'details': semantic_details
            }
            if self.verbose:
                print(f"   ✓ Semantic: {semantic_score:.3f}")
        except Exception as e:
            print(f"   ✗ Semantic failed: {e}")
            results['semantic'] = {'score': 0.0, 'is_match': False}

        # Calculate weighted final score
        final_score = sum(
            results[method]['score'] * weights[method]
            for method in weights.keys()
        )

        # Normalize to 0-1
        final_score = max(0.0, min(1.0, final_score))

        # Determine if it's a match (threshold: 0.75)
        is_match = final_score >= 0.75

        if self.verbose:
            print(
                f"\n⭐ Final Score: {final_score:.3f} - {'✅ MATCH' if is_match else '❌ NO MATCH'}")

        return is_match, final_score, results

    def validate_quick(self, original_patch, selected_patch):
        """
        Quick validation using only essential methods
        Faster but slightly less accurate

        Args:
            original_patch: correct piece
            selected_patch: selected piece

        Returns:
            tuple: (is_match, score)
        """
        # Preprocess
        img1, img2 = self.preprocess_images(original_patch, selected_patch)

        # Only use features and color (fastest methods)
        feat_match, feat_score = self.feature_extractor.validate_match(
            img1, img2)
        color_match, color_score, _ = self.color_analyzer.validate_color_match(
            img1, img2)

        # Weighted average
        final_score = feat_score * 0.6 + color_score * 0.4
        is_match = final_score >= 0.75

        return is_match, final_score

    def validate_with_context(self, original_image, missing_position, selected_patch):
        """
        Advanced validation that considers the full image context

        Args:
            original_image: full original image
            missing_position: (x, y, width, height) of missing piece
            selected_patch: the piece selected by user

        Returns:
            tuple: (is_match, score, details)
        """
        x, y, w, h = missing_position

        # Extract the correct patch from original
        original_patch = self.image_processor.crop_image(
            original_image, x, y, w, h)

        # Standard comprehensive validation
        is_match, score, results = self.validate_comprehensive(
            original_patch, selected_patch)

        # Additional context-based checks
        try:
            # Analyze if the patch fits semantically with surrounding area
            context_region = self._extract_context_region(
                original_image, x, y, w, h)

            context_match, context_score, context_details = \
                self.semantic_analyzer.validate_contextual_match(
                    context_region, selected_patch
                )

            # Adjust final score with context
            adjusted_score = score * 0.85 + context_score * 0.15

            results['context'] = {
                'score': context_score,
                'is_match': context_match,
                'details': context_details
            }

            return adjusted_score >= 0.75, adjusted_score, results

        except Exception as e:
            if self.verbose:
                print(f"⚠️ Context analysis failed: {e}")
            return is_match, score, results

    def _extract_context_region(self, image, x, y, w, h, margin=20):
        """
        Extract region around the missing piece for context analysis

        Args:
            image: full image
            x, y, w, h: position and size of missing piece
            margin: pixels to include around the piece

        Returns:
            context region image
        """
        img_h, img_w = image.shape[:2]

        # Calculate context bounds
        ctx_x = max(0, x - margin)
        ctx_y = max(0, y - margin)
        ctx_w = min(img_w - ctx_x, w + 2 * margin)
        ctx_h = min(img_h - ctx_y, h + 2 * margin)

        context = self.image_processor.crop_image(
            image, ctx_x, ctx_y, ctx_w, ctx_h)

        return context

    def batch_validate(self, original_patch, candidate_patches):
        """
        Validate multiple candidate patches at once
        Returns them ranked by match score

        Args:
            original_patch: correct piece
            candidate_patches: list of candidate pieces

        Returns:
            list of tuples: [(patch_index, is_match, score), ...]
            sorted by score (highest first)
        """
        results = []

        for idx, candidate in enumerate(candidate_patches):
            is_match, score, _ = self.validate_comprehensive(
                original_patch, candidate)
            results.append((idx, is_match, score))

        # Sort by score (descending)
        results.sort(key=lambda x: x[2], reverse=True)

        return results

    def get_confidence_explanation(self, validation_results):
        """
        Generate human-readable explanation of validation results

        Args:
            validation_results: results dict from validate_comprehensive

        Returns:
            str: explanation text
        """
        explanations = []

        for method, result in validation_results.items():
            score = result['score']

            if score >= 0.85:
                level = "Excellent"
            elif score >= 0.70:
                level = "Good"
            elif score >= 0.50:
                level = "Moderate"
            else:
                level = "Poor"

            explanations.append(
                f"{method.capitalize()}: {level} match ({score:.2%})")

        return "\n".join(explanations)

    def visualize_validation(self, original_patch, selected_patch, results):
        """
        Create visualization showing the comparison

        Args:
            original_patch: correct piece
            selected_patch: selected piece
            results: validation results

        Returns:
            visualization image
        """
        # Resize images to same size for display
        display_size = (200, 200)
        img1_display = cv2.resize(original_patch, display_size)
        img2_display = cv2.resize(selected_patch, display_size)

        # Create canvas
        canvas_height = display_size[1]
        canvas_width = display_size[0] * 2 + 100  # space for text
        canvas = np.ones((canvas_height + 150, canvas_width, 3),
                         dtype=np.uint8) * 255

        # Place images
        canvas[0:display_size[1], 0:display_size[0]] = img1_display
        canvas[0:display_size[1], display_size[0] +
               100:display_size[0]*2+100] = img2_display

        # Add labels
        cv2.putText(canvas, "Original", (50, display_size[1] + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(canvas, "Selected", (display_size[0] + 130, display_size[1] + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Add scores
        y_offset = display_size[1] + 70
        for method, result in results.items():
            score = result['score']
            text = f"{method}: {score:.2%}"
            color = (0, 200, 0) if score >= 0.75 else (0, 0, 200)
            cv2.putText(canvas, text, (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_offset += 25

        return canvas


class FastCVValidator:
    """
    Lightweight validator for real-time performance
    Uses only the fastest CV techniques
    """

    def __init__(self):
        """Initialize fast validator"""
        print("⚡ Initializing Fast CV Validator...")
        self.feature_extractor = FeatureExtractor('resnet50')
        self.color_analyzer = ColorAnalyzer()
        self.image_processor = ImageProcessor()
        print("✅ Fast CV Validator ready!")

    def validate(self, original_patch, selected_patch, threshold=0.75):
        """
        Fast validation using only features and color

        Args:
            original_patch: correct piece
            selected_patch: selected piece
            threshold: match threshold

        Returns:
            tuple: (is_match, score)
        """
        # Preprocess
        img1 = self.image_processor.normalize_image(original_patch)
        img2 = self.image_processor.normalize_image(selected_patch)

        # Resize to same size
        h, w = img1.shape[:2]
        img2 = cv2.resize(img2, (w, h))

        # Feature validation (60% weight)
        _, feat_score = self.feature_extractor.validate_match(img1, img2)

        # Color validation (40% weight)
        _, color_score, _ = self.color_analyzer.validate_color_match(
            img1, img2)

        # Combined score
        final_score = feat_score * 0.60 + color_score * 0.40
        is_match = final_score >= threshold

        return is_match, final_score


if __name__ == "__main__":
    # Testing
    print("🧪 Testing CV Validator Module...")

    # Create test images
    test_original = np.random.randint(100, 200, (150, 150, 3), dtype=np.uint8)
    test_correct = test_original.copy()
    test_wrong = np.random.randint(0, 100, (150, 150, 3), dtype=np.uint8)

    print("\n--- Testing Comprehensive Validator ---")
    validator = CVValidator(use_ensemble=False, verbose=True)

    # Test with correct piece
    print("\n🎯 Testing with CORRECT piece:")
    is_match, score, results = validator.validate_comprehensive(
        test_original, test_correct)
    print(
        f"Result: {'✅ MATCH' if is_match else '❌ NO MATCH'} (score: {score:.3f})")

    # Test with wrong piece
    print("\n🎯 Testing with WRONG piece:")
    is_match, score, results = validator.validate_comprehensive(
        test_original, test_wrong)
    print(
        f"Result: {'✅ MATCH' if is_match else '❌ NO MATCH'} (score: {score:.3f})")

    # Test quick validation
    print("\n--- Testing Quick Validator ---")
    is_match_quick, score_quick = validator.validate_quick(
        test_original, test_correct)
    print(f"Quick validation: {is_match_quick} (score: {score_quick:.3f})")

    # Test fast validator
    print("\n--- Testing Fast Validator ---")
    fast_validator = FastCVValidator()
    is_match_fast, score_fast = fast_validator.validate(
        test_original, test_correct)
    print(f"Fast validation: {is_match_fast} (score: {score_fast:.3f})")

    # Test batch validation
    print("\n--- Testing Batch Validation ---")
    candidates = [test_correct, test_wrong, test_original.copy()]
    batch_results = validator.batch_validate(test_original, candidates)
    print("Batch results (ranked):")
    for idx, is_match, score in batch_results:
        print(f"  Candidate {idx}: {score:.3f} - {'✅' if is_match else '❌'}")

    print("\n✅ CV Validator Module - All tests passed!")
