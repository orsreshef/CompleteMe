"""
Image Processing Module
General image processing utilities for puzzle creation
"""

import numpy as np
import cv2
from PIL import Image
import io


class ImageProcessor:
    """
    Class for general image processing operations
    """

    def __init__(self):
        """Initialize image processor"""
        print("✅ Image Processor initialized")

    def load_image(self, source):
        """
        Load image from various sources

        Args:
            source: file path, URL, or bytes

        Returns:
            numpy array (BGR format)
        """
        if isinstance(source, str):
            # Load from file path
            image = cv2.imread(source)
            if image is None:
                raise ValueError(f"Could not load image from: {source}")
            return image

        elif isinstance(source, bytes):
            # Load from bytes
            nparr = np.frombuffer(source, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Could not decode image from bytes")
            return image

        elif isinstance(source, np.ndarray):
            # Already a numpy array
            return source

        else:
            raise ValueError(f"Unsupported image source type: {type(source)}")

    def resize_image(self, image, target_size=None, max_size=None, maintain_aspect=True):
        """
        Resize image to target size or within max size

        Args:
            image: input image
            target_size: tuple (width, height) for exact size
            max_size: int for maximum dimension
            maintain_aspect: whether to maintain aspect ratio

        Returns:
            resized image
        """
        h, w = image.shape[:2]

        if target_size is not None:
            target_w, target_h = target_size
            if maintain_aspect:
                # Calculate scaling to fit within target size
                scale = min(target_w / w, target_h / h)
                new_w = int(w * scale)
                new_h = int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        elif max_size is not None:
            # Scale down if larger than max_size
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
        """
        Crop a rectangular region from image

        Args:
            image: input image
            x, y: top-left corner coordinates
            width, height: dimensions of crop

        Returns:
            cropped image
        """
        # Ensure coordinates are within bounds
        h, w = image.shape[:2]
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        width = min(width, w - x)
        height = min(height, h - y)

        return image[y:y+height, x:x+width].copy()

    def add_padding(self, image, padding, color=(0, 0, 0)):
        """
        Add padding around image

        Args:
            image: input image
            padding: int or tuple (top, bottom, left, right)
            color: padding color (BGR)

        Returns:
            padded image
        """
        if isinstance(padding, int):
            top = bottom = left = right = padding
        else:
            top, bottom, left, right = padding

        return cv2.copyMakeBorder(
            image, top, bottom, left, right,
            cv2.BORDER_CONSTANT, value=color
        )

    def create_black_square(self, image, x, y, width, height):
        """
        Replace a region with black square

        Args:
            image: input image
            x, y: top-left corner
            width, height: dimensions

        Returns:
            image with black square
        """
        result = image.copy()
        cv2.rectangle(result, (x, y), (x + width, y + height), (0, 0, 0), -1)
        return result

    def normalize_image(self, image):
        """
        Normalize image to standard format
        Ensures consistent size and color space

        Args:
            image: input image

        Returns:
            normalized image
        """
        # Convert to BGR if grayscale
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Ensure uint8
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        return image

    def enhance_image(self, image, brightness=1.0, contrast=1.0, saturation=1.0):
        """
        Enhance image brightness, contrast, and saturation

        Args:
            image: input image
            brightness: brightness factor (1.0 = no change)
            contrast: contrast factor (1.0 = no change)
            saturation: saturation factor (1.0 = no change)

        Returns:
            enhanced image
        """
        # Convert to float for processing
        img_float = image.astype(np.float32)

        # Adjust brightness
        if brightness != 1.0:
            img_float = img_float * brightness

        # Adjust contrast
        if contrast != 1.0:
            mean = img_float.mean(axis=(0, 1), keepdims=True)
            img_float = (img_float - mean) * contrast + mean

        # Adjust saturation
        if saturation != 1.0:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] = hsv[:, :, 1] * saturation
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            img_float = cv2.cvtColor(hsv.astype(
                np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

        # Clip and convert back to uint8
        img_enhanced = np.clip(img_float, 0, 255).astype(np.uint8)

        return img_enhanced

    def apply_blur(self, image, blur_type='gaussian', kernel_size=5):
        """
        Apply blur to image

        Args:
            image: input image
            blur_type: 'gaussian', 'median', or 'bilateral'
            kernel_size: size of blur kernel

        Returns:
            blurred image
        """
        if blur_type == 'gaussian':
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif blur_type == 'median':
            return cv2.medianBlur(image, kernel_size)
        elif blur_type == 'bilateral':
            return cv2.bilateralFilter(image, kernel_size, 75, 75)
        else:
            raise ValueError(f"Unknown blur type: {blur_type}")

    def rotate_image(self, image, angle):
        """
        Rotate image by given angle

        Args:
            image: input image
            angle: rotation angle in degrees

        Returns:
            rotated image
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)

        # Get rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Calculate new dimensions
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        # Adjust rotation matrix
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        # Rotate
        rotated = cv2.warpAffine(image, M, (new_w, new_h))

        return rotated

    def flip_image(self, image, direction='horizontal'):
        """
        Flip image horizontally or vertically

        Args:
            image: input image
            direction: 'horizontal', 'vertical', or 'both'

        Returns:
            flipped image
        """
        if direction == 'horizontal':
            return cv2.flip(image, 1)
        elif direction == 'vertical':
            return cv2.flip(image, 0)
        elif direction == 'both':
            return cv2.flip(image, -1)
        else:
            raise ValueError(f"Unknown flip direction: {direction}")

    def convert_to_grayscale(self, image):
        """
        Convert image to grayscale

        Args:
            image: input image (BGR)

        Returns:
            grayscale image
        """
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            return image

    def image_to_bytes(self, image, format='png'):
        """
        Convert image to bytes

        Args:
            image: input image
            format: output format ('png', 'jpg')

        Returns:
            image as bytes
        """
        # Encode image
        if format.lower() in ['jpg', 'jpeg']:
            success, buffer = cv2.imencode('.jpg', image)
        else:
            success, buffer = cv2.imencode('.png', image)

        if not success:
            raise ValueError("Failed to encode image")

        return buffer.tobytes()

    def bytes_to_image(self, image_bytes):
        """
        Convert bytes to image

        Args:
            image_bytes: image as bytes

        Returns:
            numpy array (BGR)
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image from bytes")

        return image

    def get_image_info(self, image):
        """
        Get information about the image

        Args:
            image: input image

        Returns:
            dict: image information
        """
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


if __name__ == "__main__":
    # Testing
    print("🧪 Testing Image Processor Module...")

    # Create test image
    test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)

    processor = ImageProcessor()

    # Test resize
    resized = processor.resize_image(test_image, target_size=(100, 100))
    print(f"✅ Image resized: {resized.shape}")

    # Test crop
    cropped = processor.crop_image(test_image, 50, 50, 100, 100)
    print(f"✅ Image cropped: {cropped.shape}")

    # Test black square
    with_square = processor.create_black_square(test_image, 50, 50, 50, 50)
    print(f"✅ Black square added")

    # Test enhance
    enhanced = processor.enhance_image(
        test_image, brightness=1.2, contrast=1.1)
    print(f"✅ Image enhanced")

    # Test blur
    blurred = processor.apply_blur(test_image, blur_type='gaussian')
    print(f"✅ Blur applied")

    # Test rotation
    rotated = processor.rotate_image(test_image, 45)
    print(f"✅ Image rotated: {rotated.shape}")

    # Test conversion
    gray = processor.convert_to_grayscale(test_image)
    print(f"✅ Converted to grayscale: {gray.shape}")

    # Test bytes conversion
    image_bytes = processor.image_to_bytes(test_image)
    recovered = processor.bytes_to_image(image_bytes)
    print(f"✅ Bytes conversion: {len(image_bytes)} bytes")

    # Test info
    info = processor.get_image_info(test_image)
    print(
        f"✅ Image info: {info['width']}x{info['height']}, {info['size_mb']:.2f} MB")

    print("✅ Image Processor Module - All tests passed!")
