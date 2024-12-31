from rest_framework import serializers


class RexelRequestSerializer(serializers.Serializer):
    """Serializer voor validatie van Rexel data."""
    productNumber = serializers.CharField(max_length=255, required=True)
    partNumber = serializers.CharField(max_length=255, required=True)
