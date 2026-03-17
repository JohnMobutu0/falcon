import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .jwt_helper import decode_jwt_token


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """Middleware that authenticates users based on a JWT cookie."""

    def process_request(self, request):
        # Look for the token cookie (name it 'auth_token')
        token = request.COOKIES.get('auth_token')
        if token:
            payload = decode_jwt_token(token)
            if payload:
                # Attach user info to the request --...user_name
                request.user_id = payload.get('user_id')
                request.user_name = payload.get('user_name')
                request.user_email = payload.get('email')
                # You could also create a Django user object on the fly
                # but for simplicity we'll just attach attributes.
            else:
                # Invalid token, clear any previous auth
                request.user_id = None
                request.user_name = None
                request.user_email = None
        else:
            request.user_id = None
            request.user_name = None
            request.user_email = None
