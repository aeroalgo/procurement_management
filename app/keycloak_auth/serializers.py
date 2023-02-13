from rest_framework import serializers


class CodeSerializer(serializers.Serializer):  # noqa
    code = serializers.CharField(max_length=150, min_length=20)


class RefreshTokenSerializer(serializers.Serializer):  # noqa
    refresh_token = serializers.CharField(max_length=1000, min_length=20)


class LogoutSerializer(serializers.Serializer):  # noqa
    refresh_token = serializers.CharField(max_length=1000, min_length=20)
