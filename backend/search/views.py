"""
Views for the GitHub search API.

Endpoints:
    POST /api/search/
        Accepts { query, entity_type }, checks Redis cache first,
        falls back to GitHub API on a cache miss, then caches the result.

    POST /api/clear-cache/
        Flushes all keys in the Redis cache (the entire cache DB).
"""
from __future__ import annotations

import logging

from django.conf import settings
from django.core.cache import cache
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .git_client import GitAPIError, search_provider
from .serializers import SearchRequestSerializer, SearchResponseSerializer

logger = logging.getLogger(__name__)

CACHE_TTL: int = getattr(settings, "CACHE_TTL", 60 * 60 * 2)  # default 2 h


def _build_cache_key(provider: str, entity_type: str, query: str) -> str:
    """Return a deterministic Redis key for a given search."""
    return f"{provider}:{entity_type}:{query.lower().strip()}"


class SearchView(APIView):
    """
    Search Git users or repositories.

    Results are cached in Redis for 2 hours. A cache hit is indicated by
    the ``cached: true`` flag in the response body.
    """

    @extend_schema(
        request=SearchRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=SearchResponseSerializer,
                description="Successful search results (may be served from cache).",
                examples=[
                    OpenApiExample(
                        "Repository search",
                        value={
                            "total_count": 42,
                            "entity_type": "repositories",
                            "items": [
                                {
                                    "id": 1,
                                    "name": "django",
                                    "full_name": "django/django",
                                    "description": "The Web framework for perfectionists with deadlines.",
                                    "html_url": "https://github.com/django/django",
                                    "stargazers_count": 80000,
                                    "forks_count": 32000,
                                    "language": "Python",
                                    "owner": {
                                        "login": "django",
                                        "avatar_url": "https://avatars.githubusercontent.com/u/27804",
                                        "html_url": "https://github.com/django",
                                    },
                                }
                            ],
                            "cached": False,
                        },
                    )
                ],
            ),
            400: OpenApiResponse(description="Invalid request payload."),
            429: OpenApiResponse(description="GitHub API rate limit exceeded."),
            502: OpenApiResponse(description="GitHub API error."),
        },
        summary="Search Git",
        description=(
            "Search Git users or repositories by keyword. "
            "Results are cached in Redis for 2 hours; subsequent identical "
            "requests will be served from cache without hitting GitHub."
        ),
        tags=["Search"],
    )
    def post(self, request: Request) -> Response:
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid request.", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query: str = serializer.validated_data["query"]
        entity_type: str = serializer.validated_data["entity_type"]
        provider: str = serializer.validated_data["provider"]
        cache_key = _build_cache_key(provider, entity_type, query)

        # --- Cache lookup ---
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info("Cache hit for key '%s'.", cache_key)
            cached_data["cached"] = True
            return Response(cached_data, status=status.HTTP_200_OK)

        # --- Git API call ---
        logger.info(
            "Cache miss for key '%s'. Fetching from %s.", cache_key, provider
        )
        try:
            data = search_provider(provider=provider, entity_type=entity_type, query=query)
        except GitAPIError as exc:
            return Response(
                {"error": str(exc)},
                status=exc.status_code,
            )
        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            "total_count": data.get("total_count", 0),
            "entity_type": entity_type,
            "items": data.get("items", []),
            "cached": False,
        }

        # Store in Redis (fire and forget; errors are suppressed by IGNORE_EXCEPTIONS)
        cache.set(cache_key, payload, timeout=CACHE_TTL)

        return Response(payload, status=status.HTTP_200_OK)


class ClearCacheView(APIView):
    """
    Clear all cached search results from Redis.

    This is a convenience endpoint for development / administration.
    In production you may want to protect it with authentication.
    """

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                description="Cache cleared successfully.",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Cache cleared successfully."},
                    )
                ],
            )
        },
        summary="Clear Redis cache",
        description=(
            "Flush all GitHub search results stored in the Redis cache. "
            "After this call the next identical search will hit the GitHub API again."
        ),
        tags=["Cache"],
    )
    def post(self, request: Request) -> Response:
        cache.clear()
        logger.info("Redis cache cleared by request from %s.", request.META.get("REMOTE_ADDR"))
        return Response(
            {"message": "Cache cleared successfully."},
            status=status.HTTP_200_OK,
        )


class PingView(APIView):
    """
    Extremely lightweight endpoint to keep the Render free tier awake.
    """

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="Pong")},
        summary="Ping",
        description="Health check endpoint for cron-job.org to prevent Render from spinning down.",
        tags=["Health"],
    )
    def get(self, request: Request) -> Response:
        return Response({"status": "ok", "message": "pong"}, status=status.HTTP_200_OK)
