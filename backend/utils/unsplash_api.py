"""Unsplash API client for fetching random images used as puzzle sources and decoys."""

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
    """Wraps the Unsplash REST API and falls back to procedural noise images when unavailable."""

    def __init__(self, access_key=None):
        """Initialize with an Unsplash access key; sets use_fallback=True if no key is found."""
        self.access_key = access_key or Config.UNSPLASH_ACCESS_KEY

        if not self.access_key:
            print("⚠️ Warning: No Unsplash API key found. Using fallback method.")
            self.use_fallback = True
        else:
            self.use_fallback = False
            print("✅ Unsplash API initialized")

        self.base_url = Config.UNSPLASH_API_URL

    _DEFAULT_QUERIES = [
        'flowers', 'butterflies', 'birds', 'fruits', 'rainbow',
        'balloons', 'playground', 'candy', 'cats', 'dogs',
        'jellyfish', 'coral reef', 'parrots', 'sunflowers', 'hot air balloon',
        'fireworks', 'autumn leaves', 'tropical beach', 'peacock', 'koi fish'
    ]

    _BRIGHT_COLORS = ['yellow', 'orange', 'red', 'purple', 'magenta', 'green', 'teal', 'blue']

    def get_random_image(self, query=None, orientation='landscape', size='regular'):
        """Fetch a single random image from Unsplash and return (bgr_array, thumb_url).
        Returns a procedural fallback image and empty string on any error."""
        if self.use_fallback:
            return self._get_random_image_fallback(), ''

        try:
            url = f"{self.base_url}{Config.UNSPLASH_RANDOM_ENDPOINT}"
            headers = {'Authorization': f'Client-ID {self.access_key}'}

            active_query = query if query else random.choice(self._DEFAULT_QUERIES)

            params = {
                'orientation': orientation,
                'count': 1,
                'query': active_query,
                'content_filter': 'high',  # child-safe content only
                'color': random.choice(self._BRIGHT_COLORS),
            }

            response = _get_thread_session().get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                image_data = data[0] if isinstance(data, list) and len(data) > 0 else data

                image_url = image_data['urls'][size]
                thumb_url = image_data['urls'].get('small', image_url)

                img_response = _get_thread_session().get(image_url, timeout=10)

                if img_response.status_code == 200:
                    image = Image.open(io.BytesIO(img_response.content))
                    image_np = np.array(image)

                    if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                    else:
                        image_bgr = image_np

                    return image_bgr, thumb_url
                else:
                    print(f"❌ Failed to download image: {img_response.status_code}")
                    return self._get_random_image_fallback(), ''

            elif response.status_code == 403:
                # Rate limit hit for this request — use fallback but don't lock the session
                # permanently so future requests can retry
                print("⚠️ Unsplash API rate limit reached for this request. Using fallback.")
                return self._get_random_image_fallback(), ''

            else:
                print(f"❌ Unsplash API error: {response.status_code}")
                return self._get_random_image_fallback(), ''

        except Exception as e:
            print(f"❌ Error fetching from Unsplash: {e}")
            return self._get_random_image_fallback(), ''

    def _get_random_image_fallback(self):
        """Generate a random-coloured noise image as a stand-in when Unsplash is unavailable."""
        width = random.randint(400, 800)
        height = random.randint(400, 800)

        base_color = np.random.randint(0, 255, 3)
        image = np.zeros((height, width, 3), dtype=np.uint8)

        for i in range(3):
            image[:, :, i] = np.random.randint(
                max(0, base_color[i] - 50),
                min(255, base_color[i] + 50),
                (height, width),
                dtype=np.uint8
            )

        noise = np.random.normal(0, 15, (height, width, 3)).astype(np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        image = cv2.GaussianBlur(image, (5, 5), 0)

        return image
