import jwt
import requests
import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

class AuthConfig:
    @staticmethod
    def get_provider_config(provider: str):
        if provider == "github":
            return {
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "scope": "public_repo",  # Allows starring and forking public repos
            }
        elif provider == "gitlab":
            return {
                "client_id": settings.GITLAB_CLIENT_ID,
                "client_secret": settings.GITLAB_CLIENT_SECRET,
                "authorize_url": "https://gitlab.com/oauth/authorize",
                "token_url": "https://gitlab.com/oauth/token",
                "scope": "api",  # GitLab needs 'api' or 'read_api'+'write_repository'
            }
        elif provider == "codeberg":
            return {
                "client_id": settings.CODEBERG_CLIENT_ID,
                "client_secret": settings.CODEBERG_CLIENT_SECRET,
                "authorize_url": "https://codeberg.org/login/oauth/authorize",
                "token_url": "https://codeberg.org/login/oauth/access_token",
                "scope": "repo",
            }
        return None

class OAuthLoginView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, provider):
        config = AuthConfig.get_provider_config(provider)
        if not config:
            return Response({"error": "Unsupported provider"}, status=status.HTTP_400_BAD_REQUEST)
            
        redirect_uri = request.GET.get('redirect_uri', 'http://localhost:5173/oauth/callback')
        
        # Build the authorization URL
        params = [
            f"client_id={config['client_id']}",
            f"redirect_uri={redirect_uri}",
            f"scope={config['scope']}",
            f"response_type=code"
        ]
        
        if provider == "codeberg":
            # Codeberg/Gitea uses specific scope formatting or might not strictly require it, but we pass it.
            pass
            
        url = f"{config['authorize_url']}?{'&'.join(params)}"
        return Response({"url": url})

class OAuthCallbackView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, provider):
        config = AuthConfig.get_provider_config(provider)
        if not config:
            return Response({"error": "Unsupported provider"}, status=status.HTTP_400_BAD_REQUEST)
            
        code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri", 'http://localhost:5173/oauth/callback')
        
        if not code:
            return Response({"error": "Authorization code is missing"}, status=status.HTTP_400_BAD_REQUEST)
            
        payload = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.post(config["token_url"], data=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to exchange code for token: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)
            
        access_token = data.get("access_token")
        if not access_token:
            return Response({"error": "Provider did not return an access token"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create our own JWT to securely store the provider and access_token
        # It's better than returning the raw provider token in clear text to the frontend, although the frontend will store our JWT.
        jwt_payload = {
            "provider": provider,
            "access_token": access_token,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
            "iat": datetime.datetime.now(datetime.timezone.utc),
        }
        
        token = jwt.encode(jwt_payload, settings.SECRET_KEY, algorithm='HS256')
        
        return Response({
            "token": token,
            "provider": provider,
        })
