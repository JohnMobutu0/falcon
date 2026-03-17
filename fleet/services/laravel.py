import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LaravelAPIError(Exception):
    pass

class LaravelClient:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url or settings.LARAVEL_API_BASE_URL
        self.api_key = api_key or settings.LARAVEL_API_KEY

    def _request(self, method, endpoint, user_token=None, json=None):
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
        }
        if user_token:
            headers['Authorization'] = f'Bearer {user_token}'
        url = self.base_url + endpoint
        try:
            response = requests.request(method, url, json=json, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error("Laravel API timeout")
            raise LaravelAPIError("Request to Laravel timed out")
        except requests.exceptions.HTTPError as e:
            # Try to extract error message from response
            error_msg = "Unknown error"
            if response.content:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_data.get('message', 'Unknown error'))
                except:
                    error_msg = response.text
            logger.error(f"Laravel API HTTP error {response.status_code}: {error_msg}")
            raise LaravelAPIError(f"Laravel error: {error_msg}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Laravel API request failed: {e}")
            raise LaravelAPIError(f"Communication error: {e}")

    # Placeholder methods – you'll fill these once you know the endpoints
    def get_member(self, user_id, user_token):
        # Example: self._request('GET', f'/members/{user_id}', user_token)
        pass

    def get_balance(self, user_id, user_token):
        pass

    def create_transaction(self, user_id, amount, type, description, reference, user_token):
        pass