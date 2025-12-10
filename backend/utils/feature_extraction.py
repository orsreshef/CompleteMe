"""
Feature Extraction Module
חילוץ מאפיינים עמוקים מתמונות באמצעות רשתות נוירונים מאומנות מראש
"""

import numpy as np
import cv2
from tensorflow.keras.applications import ResNet50, VGG16, EfficientNetB0
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.vgg16 import preprocess_input as vgg_preprocess
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from scipy.spatial.distance import cosine, euclidean
import tensorflow as tf

# השתקת אזהרות TensorFlow
tf.get_logger().setLevel('ERROR')


class FeatureExtractor:
    """
    מחלקה לחילוץ מאפיינים מתמונות באמצעות מודלים שונים
    """

    def __init__(self, model_name='resnet50'):
        """
        אתחול המודל

        Args:
            model_name: שם המודל - 'resnet50', 'vgg16', או 'efficientnet'
        """
        self.model_name = model_name
        self.model = self._load_model()
        print(f"✅ Feature Extractor loaded: {model_name}")

    def _load_model(self):
        """טוען את המודל המאומן מראש"""
        if self.model_name == 'resnet50':
            return ResNet50(weights='imagenet', include_top=False, pooling='avg')
        elif self.model_name == 'vgg16':
            return VGG16(weights='imagenet', include_top=False, pooling='avg')
        elif self.model_name == 'efficientnet':
            return EfficientNetB0(weights='imagenet', include_top=False, pooling='avg')
        else:
            raise ValueError(f"Unknown model: {self.model_name}")

    def _preprocess_image(self, image):
        """
        מכין תמונה לעיבוד במודל

        Args:
            image: תמונה במבנה numpy array (BGR)

        Returns:
            תמונה מעובדת מוכנה למודל
        """
        # המרה מ-BGR ל-RGB (OpenCV vs Keras)
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image

        # שינוי גודל ל-224x224 (גודל סטנדרטי למודלים)
        img_resized = cv2.resize(image_rgb, (224, 224))

        # הוספת ממד batch
        img_batch = np.expand_dims(img_resized, axis=0)

        # Preprocessing לפי המודל
        if self.model_name == 'resnet50':
            return resnet_preprocess(img_batch.astype('float32'))
        elif self.model_name == 'vgg16':
            return vgg_preprocess(img_batch.astype('float32'))
        elif self.model_name == 'efficientnet':
            return efficientnet_preprocess(img_batch.astype('float32'))

    def extract_features(self, image):
        """
        חולץ וקטור מאפיינים מתמונה

        Args:
            image: תמונה (numpy array)

        Returns:
            וקטור מאפיינים (1D numpy array)
        """
        # טיפול בתמונות ריקות או קטנות מדי
        if image is None or image.size == 0:
            raise ValueError("Invalid image: empty or None")

        if image.shape[0] < 10 or image.shape[1] < 10:
            raise ValueError(f"Image too small: {image.shape}")

        # עיבוד מקדים
        processed_image = self._preprocess_image(image)

        # חילוץ features
        features = self.model.predict(processed_image, verbose=0)

        # המרה לוקטור 1D
        return features.flatten()

    def compare_features(self, features1, features2, metric='cosine'):
        """
        משווה בין שני וקטורי מאפיינים

        Args:
            features1: וקטור מאפיינים ראשון
            features2: וקטור מאפיינים שני
            metric: מדד השוואה - 'cosine' או 'euclidean'

        Returns:
            ציון דמיון (0-1, כאשר 1 = זהה לחלוטין)
        """
        if metric == 'cosine':
            # Cosine similarity (1 - cosine distance)
            similarity = 1 - cosine(features1, features2)
        elif metric == 'euclidean':
            # Euclidean distance (מנורמל)
            distance = euclidean(features1, features2)
            # המרה לציון דמיון (ככל שהמרחק קטן יותר, הדמיון גדול יותר)
            max_distance = np.sqrt(len(features1))  # מרחק מקסימלי אפשרי
            similarity = 1 - (distance / max_distance)
        else:
            raise ValueError(f"Unknown metric: {metric}")

        return max(0, min(1, similarity))  # מוודא שהערך בין 0 ל-1

    def validate_match(self, image1, image2, threshold=0.85):
        """
        בודק אם שתי תמונות דומות מספיק

        Args:
            image1: תמונה ראשונה
            image2: תמונה שנייה
            threshold: סף דמיון (0.85 = 85%)

        Returns:
            tuple: (is_match: bool, similarity_score: float)
        """
        try:
            features1 = self.extract_features(image1)
            features2 = self.extract_features(image2)

            similarity = self.compare_features(features1, features2)

            is_match = similarity >= threshold

            return is_match, similarity

        except Exception as e:
            print(f"❌ Error in feature validation: {e}")
            return False, 0.0


class MultiModelFeatureExtractor:
    """
    מחלקה שמשתמשת במספר מודלים במקביל לדיוק מקסימלי
    """

    def __init__(self):
        """אתחול מספר מודלים"""
        print("🔄 Loading multiple models for ensemble feature extraction...")
        self.extractors = {
            'resnet50': FeatureExtractor('resnet50'),
            'vgg16': FeatureExtractor('vgg16'),
        }
        print("✅ All models loaded successfully!")

    def extract_ensemble_features(self, image):
        """
        חולץ features ממספר מודלים ומשלב אותם

        Args:
            image: תמונה

        Returns:
            dict: מילון עם features מכל מודל
        """
        features_dict = {}

        for name, extractor in self.extractors.items():
            try:
                features = extractor.extract_features(image)
                features_dict[name] = features
            except Exception as e:
                print(f"⚠️ Failed to extract features with {name}: {e}")

        return features_dict

    def validate_match_ensemble(self, image1, image2, threshold=0.85):
        """
        משווה תמונות באמצעות מספר מודלים ומחזיר ממוצע

        Args:
            image1: תמונה ראשונה
            image2: תמונה שנייה
            threshold: סף דמיון

        Returns:
            tuple: (is_match, average_similarity, detailed_scores)
        """
        scores = {}

        for name, extractor in self.extractors.items():
            try:
                is_match, similarity = extractor.validate_match(
                    image1, image2, threshold)
                scores[name] = similarity
            except Exception as e:
                print(f"⚠️ Failed validation with {name}: {e}")
                scores[name] = 0.0

        # חישוב ממוצע משוקלל
        weights = {
            'resnet50': 0.6,  # משקל גבוה יותר ל-ResNet
            'vgg16': 0.4,
        }

        weighted_similarity = sum(
            scores[name] * weights[name] for name in scores)

        is_match = weighted_similarity >= threshold

        return is_match, weighted_similarity, scores


# פונקציות עזר
def extract_features_from_path(image_path, model_name='resnet50'):
    """
    חולץ features מתמונה לפי נתיב

    Args:
        image_path: נתיב לתמונה
        model_name: שם המודל

    Returns:
        וקטור features
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    extractor = FeatureExtractor(model_name)
    return extractor.extract_features(image)


def compare_images(image1, image2, model_name='resnet50'):
    """
    משווה שתי תמונות

    Args:
        image1: תמונה ראשונה או נתיב
        image2: תמונה שנייה או נתיב
        model_name: שם המודל

    Returns:
        ציון דמיון
    """
    extractor = FeatureExtractor(model_name)

    # טעינת תמונות אם הן נתיבים
    if isinstance(image1, str):
        image1 = cv2.imread(image1)
    if isinstance(image2, str):
        image2 = cv2.imread(image2)

    is_match, similarity = extractor.validate_match(image1, image2)

    return similarity


if __name__ == "__main__":
    # בדיקה
    print("🧪 Testing Feature Extraction Module...")

    # יצירת תמונת דמה
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    # בדיקת extractor יחיד
    extractor = FeatureExtractor('resnet50')
    features = extractor.extract_features(test_image)
    print(f"✅ Features extracted: shape={features.shape}")

    # בדיקת ensemble
    ensemble = MultiModelFeatureExtractor()
    features_dict = ensemble.extract_ensemble_features(test_image)
    print(f"✅ Ensemble features: {list(features_dict.keys())}")

    print("✅ Feature Extraction Module - All tests passed!")
