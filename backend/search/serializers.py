"""
Serializers for the GitHub search API endpoints.
"""
from rest_framework import serializers

ENTITY_TYPES = ["users", "repositories"]


class SearchRequestSerializer(serializers.Serializer):
    """Validates the POST /api/search/ request body."""

    query = serializers.CharField(
        min_length=3,
        max_length=256,
        trim_whitespace=True,
        help_text="The search term. Must be at least 3 characters.",
    )
    entity_type = serializers.ChoiceField(
        choices=ENTITY_TYPES,
        help_text="The type of entity to search for: 'users' or 'repositories'.",
    )


class OwnerSerializer(serializers.Serializer):
    """Represents the owner/author of a repository."""

    login = serializers.CharField()
    avatar_url = serializers.URLField()
    html_url = serializers.URLField()


class RepositoryItemSerializer(serializers.Serializer):
    """Represents a single repository search result."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    full_name = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    html_url = serializers.URLField()
    stargazers_count = serializers.IntegerField()
    forks_count = serializers.IntegerField()
    open_issues_count = serializers.IntegerField()
    language = serializers.CharField(allow_null=True)
    owner = OwnerSerializer()
    updated_at = serializers.DateTimeField()
    watchers_count = serializers.IntegerField()
    topics = serializers.ListField(child=serializers.CharField(), default=list)


class UserItemSerializer(serializers.Serializer):
    """Represents a single user search result."""

    id = serializers.IntegerField()
    login = serializers.CharField()
    avatar_url = serializers.URLField()
    html_url = serializers.URLField()
    type = serializers.CharField()
    score = serializers.FloatField()


class SearchResponseSerializer(serializers.Serializer):
    """Shape of a successful /api/search/ response."""

    total_count = serializers.IntegerField()
    entity_type = serializers.ChoiceField(choices=ENTITY_TYPES)
    items = serializers.ListField(child=serializers.DictField())
    cached = serializers.BooleanField(
        default=False,
        help_text="True if the result was served from Redis cache.",
    )
