"""Deep feature extraction from images using pretrained PyTorch models."""

import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2
from scipy.spatial.distance import cosine, euclidean


class FeatureExtractor:
    """Extracts deep feature vectors from images using a pretrained torchvision backbone."""

    def __init__(self, model_name='resnet50'):
        """Load the specified pretrained model and set up the ImageNet normalization transform."""
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model()
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        print(f"✅ PyTorch Feature Extractor loaded: {model_name} on {self.device}")

    def _load_model(self):
        """Load the pretrained backbone and strip the classification head."""
        if self.model_name == 'resnet50':
            model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
            model = torch.nn.Sequential(*list(model.children())[:-1])

        elif self.model_name == 'resnet18':
            model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            model = torch.nn.Sequential(*list(model.children())[:-1])

        elif self.model_name == 'vgg16':
            model = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1)
            model = model.features  # keep convolutional layers only

        elif self.model_name == 'efficientnet_b0':
            model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
            model.classifier = torch.nn.Identity()

        else:
            raise ValueError(f"Unknown model: {self.model_name}")

        return model.to(self.device)

    def extract_features(self, image):
        """Run the image through the backbone and return a flattened 1-D feature vector."""
        if isinstance(image, np.ndarray):
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image.astype('uint8'))

        img_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            features = self.model(img_tensor)

        features = features.squeeze().cpu().numpy()

        if features.ndim > 1:
            features = features.flatten()

        return features

    def compare_features(self, features1, features2, method='cosine'):
        """Compare two feature vectors and return a similarity score in [0, 1]."""
        if method == 'cosine':
            # cosine distance: 0 = identical, 1 = orthogonal; invert to get similarity
            similarity = 1 - cosine(features1.flatten(), features2.flatten())
        elif method == 'euclidean':
            distance = euclidean(features1.flatten(), features2.flatten())
            similarity = 1 / (1 + distance / 100)
        else:
            raise ValueError(f"Unknown method: {method}")

        return max(0, min(1, similarity))
