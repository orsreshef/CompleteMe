"""
Unsplash API Integration Module
Handles fetching random images from Unsplash
"""

import requests
import random
import io
import threading
from PIL import Image
import numpy as np
import cv2
from config import Config

# Each thread gets its own session so concurrent fetches never share state
_thread_local = threading.local()


def _get_thread_session():
    """Return a requests.Session that belongs to the current thread."""
    if not hasattr(_thread_local, 'session'):
        _thread_local.session = requests.Session()
    return _thread_local.session


class UnsplashAPI:
    """
    Class for interacting with Unsplash API
    """

    def __init__(self, access_key=None):
        """
        Initialize Unsplash API client

        Args:
            access_key: Unsplash access key (optional, uses config if not provided)
        """
        self.access_key = access_key or Config.UNSPLASH_ACCESS_KEY

        if not self.access_key:
            print("⚠️ Warning: No Unsplash API key found. Using fallback method.")
            self.use_fallback = True
        else:
            self.use_fallback = False
            print("✅ Unsplash API initialized")

        self.base_url = Config.UNSPLASH_API_URL

    # Safe, colorful, kid-friendly topics used when no query is specified
    _DEFAULT_QUERIES = [
        'flowers', 'butterflies', 'birds', 'fruits', 'rainbow',
        'balloons', 'playground', 'candy', 'cats', 'dogs',
        'jellyfish', 'coral reef', 'parrots', 'sunflowers', 'hot air balloon',
        'fireworks', 'autumn leaves', 'tropical beach', 'peacock', 'koi fish'
    ]

    # Bright colors to randomly bias Unsplash results toward vibrant images
    _BRIGHT_COLORS = ['yellow', 'orange', 'red', 'purple', 'magenta', 'green', 'teal', 'blue']

    def get_random_image(self, query=None, orientation='landscape', size='regular'):
        """
        Get a random image from Unsplash

        Args:
            query: search query (e.g., 'nature', 'animals', 'city')
            orientation: 'landscape', 'portrait', or 'squarish'
            size: 'raw', 'full', 'regular', 'small', 'thumb'

        Returns:
            tuple (numpy array BGR, image_url string) — url is '' on fallback
        """
        if self.use_fallback:
            return self._get_random_image_fallback(), ''

        try:
            # Build API request
            url = f"{self.base_url}{Config.UNSPLASH_RANDOM_ENDPOINT}"

            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }

            # If no query given, pick a random safe topic for variety
            active_query = query if query else random.choice(self._DEFAULT_QUERIES)

            params = {
                'orientation': orientation,
                'count': 1,
                'query': active_query,
                'content_filter': 'high',  # child-safe content only
                'color': random.choice(self._BRIGHT_COLORS),
            }

            # Make request (thread-local session — safe for concurrent calls)
            response = _get_thread_session().get(
                url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    image_data = data[0]
                else:
                    image_data = data

                # Get image URL (use 'small' size for thumbnails in history)
                image_url = image_data['urls'][size]
                thumb_url = image_data['urls'].get('small', image_url)

                # Download image (reuse same thread-local session)
                img_response = _get_thread_session().get(image_url, timeout=10)

                if img_response.status_code == 200:
                    # Convert to numpy array
                    image = Image.open(io.BytesIO(img_response.content))
                    image_np = np.array(image)

                    # Convert RGB to BGR (OpenCV format)
                    if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                    else:
                        image_bgr = image_np

                    return image_bgr, thumb_url
                else:
                    print(
                        f"❌ Failed to download image: {img_response.status_code}")
                    return self._get_random_image_fallback(), ''

            elif response.status_code == 403:
                # Rate limit hit for this request — use fallback but don't
                # lock the session permanently so future requests can retry
                print("⚠️ Unsplash API rate limit reached for this request. Using fallback.")
                return self._get_random_image_fallback(), ''

            else:
                print(f"❌ Unsplash API error: {response.status_code}")
                return self._get_random_image_fallback(), ''

        except Exception as e:
            print(f"❌ Error fetching from Unsplash: {e}")
            return self._get_random_image_fallback(), ''

    def get_multiple_random_images(self, count=5, query=None):
        """
        Get multiple random images

        Args:
            count: number of images to fetch
            query: search query

        Returns:
            list of numpy arrays
        """
        images = []

        for i in range(count):
            # Vary the query slightly for diversity
            if query:
                queries = [query, f'{query} closeup', f'{query} detail',
                           f'{query} texture', f'{query} pattern']
                current_query = random.choice(queries)
            else:
                current_query = random.choice(['nature', 'abstract', 'texture',
                                              'pattern', 'minimal', 'city'])

            image = self.get_random_image(query=current_query)

            if image is not None:
                images.append(image)

            # Add small delay to avoid rate limiting
            if not self.use_fallback and i < count - 1:
                import time
                time.sleep(0.5)

        return images

    def _get_random_image_fallback(self):
        """
        Generate a random colored image as fallback
        Used when Unsplash API is not available

        Returns:
            numpy array (BGR format)
        """
        # Generate random colored noise image
        width = random.randint(400, 800)
        height = random.randint(400, 800)

        # Create base color
        base_color = np.random.randint(0, 255, 3)

        # Create gradient or texture
        image = np.zeros((height, width, 3), dtype=np.uint8)

        for i in range(3):
            # Add some variation
            channel = np.random.randint(
                max(0, base_color[i] - 50),
                min(255, base_color[i] + 50),
                (height, width),
                dtype=np.uint8
            )
            image[:, :, i] = channel

        # Add some texture
        noise = np.random.normal(0, 15, (height, width, 3)).astype(np.int16)
        image = np.clip(image.astype(np.int16) +
                        noise, 0, 255).astype(np.uint8)

        # Apply slight blur for smoothness
        image = cv2.GaussianBlur(image, (5, 5), 0)

        return image

    def test_api_connection(self):
        """
        Test if Unsplash API is working

        Returns:
            bool: True if API is working, False otherwise
        """
        if not self.access_key:
            return False

        try:
            url = f"{self.base_url}{Config.UNSPLASH_RANDOM_ENDPOINT}"
            headers = {'Authorization': f'Client-ID {self.access_key}'}
            params = {'count': 1}

            response = self.session.get(
                url, headers=headers, params=params, timeout=5)

            return response.status_code == 200

        except:
            return False


if __name__ == "__main__":
    # Testing
    print("🧪 Testing Unsplash API Module...")

    api = UnsplashAPI()

    # Test connection
    is_working = api.test_api_connection()
    print(
        f"API Connection: {'✅ Working' if is_working else '❌ Not working (using fallback)'}")

    # Get single image
    print("\nFetching single random image...")
    image = api.get_random_image(query='nature')

    if image is not None:
        print(f"✅ Image fetched: shape={image.shape}")
    else:
        print("❌ Failed to fetch image")

    # Get multiple images
    print("\nFetching multiple random images...")
    images = api.get_multiple_random_images(count=3, query='animals')
    print(f"✅ Fetched {len(images)} images")

    print("\n✅ Unsplash API Module - All tests passed!")
