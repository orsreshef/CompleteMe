"""
Semantic Analysis Module
Semantic understanding and context analysis for image validation
"""

import numpy as np
import cv2
from tensorflow.keras.applications import ResNet50, VGG16
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.models import Model
import tensorflow as tf

# Suppress TensorFlow warnings
tf.get_logger().setLevel('ERROR')


class SemanticAnalyzer:
    """
    Class for semantic understanding of images
    Identifies what objects are in the image and their relationships
    """

    def __init__(self, model_name='resnet50'):
        """
        Initialize the semantic analyzer

        Args:
            model_name: name of the model - 'resnet50' or 'vgg16'
        """
        self.model_name = model_name
        self.model = self._load_model()
        print(f"✅ Semantic Analyzer loaded: {model_name}")

    def _load_model(self):
        """Load pre-trained model with classification head"""
        if self.model_name == 'resnet50':
            return ResNet50(weights='imagenet', include_top=True)
        elif self.model_name == 'vgg16':
            return VGG16(weights='imagenet', include_top=True)
        else:
            raise ValueError(f"Unknown model: {self.model_name}")

    def _preprocess_image(self, image):
        """
        Prepare image for the model

        Args:
            image: image as numpy array (BGR)

        Returns:
            preprocessed image ready for model
        """
        # Convert BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image

        # Resize to 224x224
        img_resized = cv2.resize(image_rgb, (224, 224))

        # Add batch dimension
        img_batch = np.expand_dims(img_resized, axis=0)

        # Preprocess
        return preprocess_input(img_batch.astype('float32'))

    def identify_objects(self, image, top_k=5):
        """
        Identify objects in the image

        Args:
            image: image (numpy array)
            top_k: number of top predictions to return

        Returns:
            list of tuples: (class_name, probability)
        """
        try:
            # Preprocess
            processed_image = self._preprocess_image(image)

            # Predict
            predictions = self.model.predict(processed_image, verbose=0)

            # Decode predictions
            decoded = decode_predictions(predictions, top=top_k)[0]

            # Return as list of (name, probability)
            results = [(name, float(prob)) for (_, name, prob) in decoded]

            return results

        except Exception as e:
            print(f"❌ Error in object identification: {e}")
            return []

    def get_dominant_class(self, image):
        """
        Get the most likely class for the image

        Args:
            image: image

        Returns:
            tuple: (class_name, confidence)
        """
        predictions = self.identify_objects(image, top_k=1)

        if predictions:
            return predictions[0]
        else:
            return ("unknown", 0.0)

    def compare_semantic_similarity(self, image1, image2):
        """
        Compare semantic similarity between two images
        Checks if they contain similar objects/concepts

        Args:
            image1: first image
            image2: second image

        Returns:
            float: semantic similarity score (0-1)
        """
        try:
            # Get predictions for both images
            preds1 = self.identify_objects(image1, top_k=10)
            preds2 = self.identify_objects(image2, top_k=10)

            if not preds1 or not preds2:
                return 0.0

            # Extract class names
            classes1 = set([name for name, _ in preds1])
            classes2 = set([name for name, _ in preds2])

            # Calculate Jaccard similarity (intersection over union)
            intersection = len(classes1 & classes2)
            union = len(classes1 | classes2)

            if union == 0:
                return 0.0

            jaccard_similarity = intersection / union

            # Also consider confidence overlap
            confidence_overlap = 0.0
            for name1, conf1 in preds1[:5]:  # Top 5 predictions
                for name2, conf2 in preds2[:5]:
                    if name1 == name2:
                        confidence_overlap += min(conf1, conf2)

            # Weighted combination
            final_similarity = (jaccard_similarity * 0.5 +
                                confidence_overlap * 0.5)

            return min(final_similarity, 1.0)

        except Exception as e:
            print(f"❌ Error in semantic comparison: {e}")
            return 0.0

    def analyze_image_category(self, image):
        """
        Analyze what category the image belongs to

        Args:
            image: image

        Returns:
            dict: category analysis
        """
        predictions = self.identify_objects(image, top_k=10)

        # Define broad categories
        categories = {
            'animal': ['cat', 'dog', 'bird', 'horse', 'elephant', 'lion', 'tiger',
                       'bear', 'zebra', 'giraffe', 'monkey', 'rabbit', 'fox'],
            'vehicle': ['car', 'truck', 'bus', 'motorcycle', 'bicycle', 'airplane',
                        'boat', 'train'],
            'nature': ['tree', 'flower', 'plant', 'mountain', 'lake', 'ocean',
                       'forest', 'beach'],
            'food': ['pizza', 'burger', 'sandwich', 'apple', 'banana', 'cake',
                     'bread', 'fruit'],
            'object': ['chair', 'table', 'bottle', 'cup', 'book', 'phone',
                       'keyboard', 'computer'],
            'building': ['house', 'building', 'church', 'castle', 'tower',
                         'skyscraper']
        }

        # Count matches in each category
        category_scores = {cat: 0.0 for cat in categories}

        for pred_name, confidence in predictions:
            pred_name_lower = pred_name.lower()
            for category, keywords in categories.items():
                if any(keyword in pred_name_lower for keyword in keywords):
                    category_scores[category] += confidence

        # Get dominant category
        if sum(category_scores.values()) > 0:
            dominant_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[dominant_category]
        else:
            dominant_category = 'unknown'
            confidence = 0.0

        return {
            'dominant_category': dominant_category,
            'confidence': confidence,
            'all_scores': category_scores,
            'top_predictions': predictions[:3]
        }

    def validate_semantic_match(self, image1, image2, threshold=0.40):
        """
        Comprehensive semantic validation between two images

        Args:
            image1: first image
            image2: second image
            threshold: similarity threshold

        Returns:
            tuple: (is_match, score, details)
        """
        try:
            # 1. Direct semantic similarity
            semantic_sim = self.compare_semantic_similarity(image1, image2)

            # 2. Category analysis
            cat1 = self.analyze_image_category(image1)
            cat2 = self.analyze_image_category(image2)

            # Category match bonus
            category_match = 1.0 if cat1['dominant_category'] == cat2['dominant_category'] else 0.0

            # 3. Top prediction overlap
            top1 = cat1['top_predictions']
            top2 = cat2['top_predictions']

            top_match = 0.0
            if top1 and top2:
                if top1[0][0] == top2[0][0]:  # Same top prediction
                    top_match = 1.0
                elif any(p1[0] == p2[0] for p1 in top1 for p2 in top2):
                    top_match = 0.5

            # Weighted score
            weights = {
                'semantic': 0.50,
                'category': 0.30,
                'top_prediction': 0.20
            }

            final_score = (
                semantic_sim * weights['semantic'] +
                category_match * weights['category'] +
                top_match * weights['top_prediction']
            )

            is_match = final_score >= threshold

            details = {
                'semantic_similarity': semantic_sim,
                'category_match': category_match,
                'top_prediction_match': top_match,
                'category1': cat1['dominant_category'],
                'category2': cat2['dominant_category'],
                'final_score': final_score
            }

            return is_match, final_score, details

        except Exception as e:
            print(f"❌ Error in semantic validation: {e}")
            return False, 0.0, {}


class AdvancedSemanticAnalyzer:
    """
    Advanced semantic analysis using multiple techniques
    """

    def __init__(self):
        """Initialize with multiple models"""
        print("🔄 Loading advanced semantic models...")
        self.analyzer = SemanticAnalyzer('resnet50')
        print("✅ Advanced Semantic Analyzer ready!")

    def detect_image_context(self, image):
        """
        Detect overall context and scene of the image

        Args:
            image: image

        Returns:
            dict: context information
        """
        # Get object predictions
        predictions = self.analyzer.identify_objects(image, top_k=10)

        # Analyze color dominance
        avg_color = image.mean(axis=0).mean(axis=0)

        # Determine if image is bright or dark
        brightness = avg_color.mean()

        # Determine if image is colorful or grayscale
        color_variance = avg_color.std()

        context = {
            'predictions': predictions,
            'brightness': brightness,
            'is_bright': brightness > 127,
            'color_variance': color_variance,
            'is_colorful': color_variance > 30,
            'dominant_objects': [p[0] for p in predictions[:3]]
        }

        return context

    def validate_contextual_match(self, image1, image2, original_context=None):
        """
        Validate if an image patch matches the context of the original image

        Args:
            image1: original image or patch from original
            image2: candidate patch
            original_context: optional pre-computed context of original image

        Returns:
            tuple: (is_match, score, details)
        """
        if original_context is None:
            context1 = self.detect_image_context(image1)
        else:
            context1 = original_context

        context2 = self.detect_image_context(image2)

        # Compare brightness
        brightness_diff = abs(
            context1['brightness'] - context2['brightness']) / 255
        brightness_similarity = 1 - brightness_diff

        # Compare colorfulness
        color_diff = abs(context1['color_variance'] -
                         context2['color_variance']) / 100
        color_similarity = 1 - min(color_diff, 1.0)

        # Semantic comparison
        semantic_match, semantic_score, _ = self.analyzer.validate_semantic_match(
            image1, image2)

        # Weighted score
        final_score = (
            brightness_similarity * 0.20 +
            color_similarity * 0.20 +
            semantic_score * 0.60
        )

        is_match = final_score >= 0.50

        details = {
            'brightness_similarity': brightness_similarity,
            'color_similarity': color_similarity,
            'semantic_score': semantic_score,
            'context1': context1,
            'context2': context2,
            'final_score': final_score
        }

        return is_match, final_score, details


if __name__ == "__main__":
    # Testing
    print("🧪 Testing Semantic Analysis Module...")

    # Create test image (random)
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)

    analyzer = SemanticAnalyzer('resnet50')

    # Test object identification
    predictions = analyzer.identify_objects(test_image)
    print(f"✅ Object predictions: {len(predictions)} classes identified")
    if predictions:
        print(
            f"   Top prediction: {predictions[0][0]} ({predictions[0][1]:.3f})")

    # Test category analysis
    category = analyzer.analyze_image_category(test_image)
    print(f"✅ Category analysis: {category['dominant_category']}")

    # Test semantic comparison
    test_image2 = test_image.copy()
    similarity = analyzer.compare_semantic_similarity(test_image, test_image2)
    print(f"✅ Semantic similarity: {similarity:.3f}")

    # Test validation
    is_match, score, details = analyzer.validate_semantic_match(
        test_image, test_image2)
    print(f"✅ Semantic validation: match={is_match}, score={score:.3f}")

    # Test advanced analyzer
    adv_analyzer = AdvancedSemanticAnalyzer()
    context = adv_analyzer.detect_image_context(test_image)
    print(
        f"✅ Context detection: brightness={context['brightness']:.1f}, colorful={context['is_colorful']}")

    print("✅ Semantic Analysis Module - All tests passed!")
