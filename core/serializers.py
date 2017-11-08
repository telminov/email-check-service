from rest_framework import serializers


class CheckEmail(serializers.Serializer):
    email = serializers.EmailField()
