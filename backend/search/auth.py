import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions

class DummyUser:
    """A dummy user class to satisfy DRF's request.user expectations."""
    def __init__(self, provider: str, access_token: str):
        self.provider = provider
        self.access_token = access_token
        self.is_authenticated = True

class StatelessTokenAuthentication(authentication.BaseAuthentication):
    """
    Validates a JWT provided in the Authorization header.
    Expects format: `Bearer <jwt_token>`
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if parts[0].lower() != 'bearer':
            return None
        
        if len(parts) == 1:
            raise exceptions.AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(parts) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header. Token string should not contain spaces.')
            
        token = parts[1]
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')
            
        provider = payload.get('provider')
        access_token = payload.get('access_token')
        
        if not provider or not access_token:
            raise exceptions.AuthenticationFailed('Invalid token payload.')
            
        # Return our DummyUser and the raw token for DRF's request.user and request.auth
        return (DummyUser(provider=provider, access_token=access_token), token)
