"""Image processing utilities used during puzzle creation."""

import numpy as np
import cv2
from PIL import Image
import io


class ImageProcessor:
    """General-purpose image processing operations for loading, resizing, and transforming images."""

    def __init__(self):
        """Initialize image processor."""
        print("✅ Image Processor initialized")

    def load_image(self, source):
        """Load an image from a file path, raw bytes, or numpy array and return a BGR numpy array."""
        if isinstance(source, str):
            image = cv2.imread(source)
            if image is None:
                raise ValueError(f"Could not load image from: {source}")
            return image

        elif isinstance(source, bytes):
            nparr = np.frombuffer(source, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Could not decode image from bytes")
            return image

        elif isinstance(source, np.ndarray):
            return source

        else:
            raise ValueError(f"Unsupported image source type: {type(source)}")

    def resize_image(self, image, target_size=None, max_size=None, maintain_aspect=True):
        """Resize image to an exact target_size or scale it down to fit within max_size."""
        h, w = image.shape[:2]

        if target_size is not None:
            target_w, target_h = target_size
            if maintain_aspect:
                scale = min(target_w / w, target_h / h)
                new_w = int(w * scale)
                new_h = int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        elif max_size is not None:
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            else:
                return image

        else:
            return image

    def crop_image(self, image, x, y, width, height):
        """Crop a rectangular region from the image, clamping coordinates to valid bounds."""
        h, w = image.shape[:2]
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        width = min(width, w - x)
        height = min(height, h - y)
        return image[y:y+height, x:x+width].copy()

    def add_padding(self, image, padding, color=(0, 0, 0)):
        """Add padding around the image using the given BGR color."""
        if isinstance(padding, int):
            top = bottom = left = right = padding
        else:
            top, bottom, left, right = padding

        return cv2.copyMakeBorder(
            image, top, bottom, left, right,
            cv2.BORDER_CONSTANT, value=color
        )

    def create_black_square(self, image, x, y, width, height):
        """Replace a rectangular region with a solid black rectangle and return the result."""
        result = image.copy()
        cv2.rectangle(result, (x, y), (x + width, y + height), (0, 0, 0), -1)
        return result

    def normalize_image(self, image):
        """Ensure the image is BGR uint8, converting from grayscale or float if necessary."""
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        return image

    def enhance_image(self, image, brightness=1.0, contrast=1.0, saturation=1.0):
        """Apply brightness, contrast, and saturation adjustments to the image."""
        img_float = image.astype(np.float32)

        if brightness != 1.0:
            img_float = img_float * brightness

        if contrast != 1.0:
            mean = img_float.mean(axis=(0, 1), keepdims=True)
            img_float = (img_float - mean) * contrast + mean

        if saturation != 1.0:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
            img_float = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

        return np.clip(img_float, 0, 255).astype(np.uint8)

    def apply_blur(self, image, blur_type='gaussian', kernel_size=5):
        """Apply gaussian, median, or bilateral blur to the image."""
        if blur_type == 'gaussian':
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif blur_type == 'median':
            return cv2.medianBlur(image, kernel_size)
        elif blur_type == 'bilateral':
            return cv2.bilateralFilter(image, kernel_size, 75, 75)
        else:
            raise ValueError(f"Unknown blur type: {blur_type}")

    def rotate_image(self, image, angle):
        """Rotate the image by the given angle (degrees), expanding the canvas to avoid clipping."""
        h, w = image.shape[:2]
        center = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        return cv2.warpAffine(image, M, (new_w, new_h))

    def flip_image(self, image, direction='horizontal'):
        """Flip the image horizontally, vertically, or both."""
        if direction == 'horizontal':
            return cv2.flip(image, 1)
        elif direction == 'vertical':
            return cv2.flip(image, 0)
        elif direction == 'both':
            return cv2.flip(image, -1)
        else:
            raise ValueError(f"Unknown flip direction: {direction}")

    def convert_to_grayscale(self, image):
        """Convert a BGR image to grayscale; return unchanged if already single-channel."""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            return image

    def image_to_bytes(self, image, format='png'):
        """Encode the image to PNG or JPEG bytes."""
        if format.lower() in ['jpg', 'jpeg']:
            success, buffer = cv2.imencode('.jpg', image)
        else:
            success, buffer = cv2.imencode('.png', image)

        if not success:
            raise ValueError("Failed to encode image")

        return buffer.tobytes()

    def bytes_to_image(self, image_bytes):
        """Decode raw image bytes to a BGR numpy array."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image from bytes")

        return image

    def get_image_info(self, image):
        """Return a dict with width, height, channel count, dtype, size in MB, aspect ratio, and pixel count."""
        h, w = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1

        return {
            'width': w,
            'height': h,
            'channels': channels,
            'dtype': str(image.dtype),
            'size_mb': image.nbytes / (1024 * 1024),
            'aspect_ratio': w / h,
            'total_pixels': h * w
        }
