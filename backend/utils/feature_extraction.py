"""
Feature Extraction Module - PyTorch Version
חילוץ מאפיינים עמוקים מתמונות באמצעות PyTorch
"""

import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2
from scipy.spatial.distance import cosine, euclidean


class FeatureExtractor:
    """
    מחלקה לחילוץ מאפיינים מתמונות באמצעות PyTorch
    """

    def __init__(self, model_name='resnet50'):
        """
        אתחול המודל

        Args:
            model_name: 'resnet50', 'vgg16', 'resnet18', 'efficientnet_b0'
        """
        self.model_name = model_name
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model()
        self.model.eval()  # מצב הערכה (לא אימון)

        # הגדרת transformations
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        print(
            f"✅ PyTorch Feature Extractor loaded: {model_name} on {self.device}")

    def _load_model(self):
        """טוען את המודל המאומן מראש"""
        if self.model_name == 'resnet50':
            model = models.resnet50(
                weights=models.ResNet50_Weights.IMAGENET1K_V1)
            # מסיר את השכבה האחרונה (FC layer)
            model = torch.nn.Sequential(*list(model.children())[:-1])

        elif self.model_name == 'resnet18':
            model = models.resnet18(
                weights=models.ResNet18_Weights.IMAGENET1K_V1)
            model = torch.nn.Sequential(*list(model.children())[:-1])

        elif self.model_name == 'vgg16':
            model = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1)
            # רק את ה-features, בלי classifier
            model = model.features

        elif self.model_name == 'efficientnet_b0':
            model = models.efficientnet_b0(
                weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            # מסיר את ה-classifier
            model.classifier = torch.nn.Identity()

        else:
            raise ValueError(f"Unknown model: {self.model_name}")

        return model.to(self.device)

    def extract_features(self, image):
        """
        מחלץ מאפיינים מתמונה

        Args:
            image: תמונה (numpy array BGR או PIL Image)

        Returns:
            numpy array: וקטור מאפיינים
        """
        # המרה ל-PIL אם צריך
        if isinstance(image, np.ndarray):
            # OpenCV משתמש ב-BGR, צריך להמיר ל-RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image.astype('uint8'))

        # הכנת התמונה
        img_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # חילוץ features
        with torch.no_grad():
            features = self.model(img_tensor)

        # המרה ל-numpy
        features = features.squeeze().cpu().numpy()

        # נרמול
        if features.ndim > 1:
            features = features.flatten()

        return features

    def compare_features(self, features1, features2, method='cosine'):
        """
        משווה שני וקטורי מאפיינים

        Args:
            features1: וקטור ראשון
            features2: וקטור שני
            method: 'cosine' או 'euclidean'

        Returns:
            float: ציון דמיון (0-1)
        """
        if method == 'cosine':
            # Cosine similarity: 1 = זהה, 0 = שונה לגמרי
            similarity = 1 - cosine(features1.flatten(), features2.flatten())
        elif method == 'euclidean':
            # Euclidean distance: קטן יותר = דומה יותר
            distance = euclidean(features1.flatten(), features2.flatten())
            # נרמול לטווח 0-1
            similarity = 1 / (1 + distance / 100)  # חלוקה ב-100 לנרמול
        else:
            raise ValueError(f"Unknown method: {method}")

        return max(0, min(1, similarity))

    def validate(self, image1, image2, threshold=0.75):
        """
        בדיקה מהירה של התאמה בין שתי תמונות

        Args:
            image1: תמונה ראשונה
            image2: תמונה שנייה
            threshold: סף דמיון

        Returns:
            tuple: (is_match, confidence)
        """
        try:
            features1 = self.extract_features(image1)
            features2 = self.extract_features(image2)

            confidence = self.compare_features(features1, features2)
            is_match = confidence >= threshold

            return is_match, confidence

        except Exception as e:
            print(f"❌ Error in feature validation: {e}")
            return False, 0.0


class MultiModelFeatureExtractor:
    """
    מחלקה שמשתמשת במספר מודלים ומשלבת את התוצאות
    """

    def __init__(self, models=['resnet50', 'vgg16']):
        """
        אתחול מספר מודלים

        Args:
            models: רשימת שמות מודלים
        """
        self.extractors = {}
        for model_name in models:
            try:
                self.extractors[model_name] = FeatureExtractor(model_name)
            except Exception as e:
                print(f"⚠️ Failed to load {model_name}: {e}")

        if not self.extractors:
            raise ValueError("No models loaded successfully")

        print(
            f"✅ Multi-Model Extractor initialized with {len(self.extractors)} models")

    def validate(self, image1, image2, threshold=0.75):
        """
        בדיקה משולבת עם מספר מודלים

        Args:
            image1: תמונה ראשונה
            image2: תמונה שנייה
            threshold: סף דמיון

        Returns:
            tuple: (is_match, confidence)
        """
        confidences = []

        for model_name, extractor in self.extractors.items():
            try:
                _, conf = extractor.validate(image1, image2, threshold)
                confidences.append(conf)
            except Exception as e:
                print(f"⚠️ Error in {model_name}: {e}")

        if not confidences:
            return False, 0.0

        # ממוצע של כל המודלים
        avg_confidence = np.mean(confidences)
        is_match = avg_confidence >= threshold

        return is_match, avg_confidence


if __name__ == "__main__":
    print("🧪 Testing PyTorch Feature Extractor...")

    # Create test images
    test_image1 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    test_image2 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    # Test single model
    extractor = FeatureExtractor('resnet50')
    is_match, confidence = extractor.validate(test_image1, test_image2)
    print(f"Single Model - Match: {is_match}, Confidence: {confidence:.3f}")

    # Test multi-model
    multi_extractor = MultiModelFeatureExtractor(['resnet50', 'vgg16'])
    is_match, confidence = multi_extractor.validate(test_image1, test_image2)
    print(f"Multi Model - Match: {is_match}, Confidence: {confidence:.3f}")

    print("✅ PyTorch Feature Extractor - All tests passed!")
