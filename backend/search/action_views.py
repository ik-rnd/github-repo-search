import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from urllib.parse import quote

class RepoActionBaseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_action_url_and_method(self, provider, repo_full_name, action):
        if provider == "github":
            base_url = "https://api.github.com"
            if action == "star":
                return f"{base_url}/user/starred/{repo_full_name}", "PUT"
            elif action == "fork":
                return f"{base_url}/repos/{repo_full_name}/forks", "POST"
                
        elif provider == "gitlab":
            base_url = "https://gitlab.com/api/v4"
            encoded_repo = quote(repo_full_name, safe="")
            if action == "star":
                return f"{base_url}/projects/{encoded_repo}/star", "POST"
            elif action == "fork":
                return f"{base_url}/projects/{encoded_repo}/fork", "POST"
                
        elif provider == "codeberg":
            base_url = "https://codeberg.org/api/v1"
            if action == "star":
                return f"{base_url}/user/starred/{repo_full_name}", "PUT"
            elif action == "fork":
                return f"{base_url}/repos/{repo_full_name}/forks", "POST"
                
        return None, None

    def perform_action(self, request, action):
        repo_full_name = request.data.get("repo_full_name")
        # Ensure the provider matches the user's token provider
        provider = request.user.provider
        
        if not repo_full_name:
            return Response({"error": "repo_full_name is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        url, method = self.get_action_url_and_method(provider, repo_full_name, action)
        if not url:
            return Response({"error": f"Unsupported provider {provider}"}, status=status.HTTP_400_BAD_REQUEST)
            
        headers = {}
        if provider == "github":
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {request.user.access_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        else:
            headers = {
                "Authorization": f"Bearer {request.user.access_token}",
            }
            
        try:
            if method == "PUT":
                response = requests.put(url, headers=headers, timeout=15)
            else:
                response = requests.post(url, headers=headers, timeout=15)
                
            # Treat 204 (No Content), 201 (Created), and 200 (OK) as success
            if response.status_code in [200, 201, 204, 304]:
                return Response({"success": True})
            elif response.status_code == 404:
                return Response({"error": "Repository not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
            elif response.status_code == 304: # GitHub returns 304 if already starred
                return Response({"success": True, "message": "Already performed"})
            elif response.status_code == 403:
                return Response({"error": "Rate limit or permission denied"}, status=status.HTTP_403_FORBIDDEN)
            elif response.status_code == 401:
                return Response({"error": "Token is invalid or expired"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"error": f"Provider API returned {response.status_code}"}, status=status.HTTP_502_BAD_GATEWAY)
                
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to reach provider API: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

class StarRepoView(RepoActionBaseView):
    def post(self, request):
        return self.perform_action(request, "star")
        
class ForkRepoView(RepoActionBaseView):
    def post(self, request):
        return self.perform_action(request, "fork")
