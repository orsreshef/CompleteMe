"""Image processing utilities used during puzzle creation."""

import numpy as np
import cv2


class ImageProcessor:
    """General-purpose image processing operations for loading, resizing, and transforming images."""

    def __init__(self):
        """Initialize image processor."""
        print("✅ Image Processor initialized")

    def load_image(self, source):
        """Load an image from a file path, raw bytes, or numpy array and return a BGR numpy array."""
        if isinstance(source, str):
            # imread reads the file from disk AND decodes it in one call
            image = cv2.imread(source)
            if image is None:
                raise ValueError(f"Could not load image from: {source}")
            return image

        elif isinstance(source, bytes):
            # frombuffer just reinterprets raw bytes as a numpy array — no decoding yet (JPEG/PNG
            nparr = np.frombuffer(source, np.uint8)
            # imdecode does the real work: turns the still-compressed bytes into actual pixels
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Could not decode image from bytes")
            return image

        elif isinstance(source, np.ndarray):
            # already a decoded image — nothing to do
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
            # INTER_AREA gives the best quality specifically when shrinking images
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

    def create_black_square(self, image, x, y, width, height):
        """Replace a rectangular region with a solid black rectangle and return the result."""
        result = image.copy()
        cv2.rectangle(result, (x, y), (x + width, y + height), (0, 0, 0), -1)
        return result
