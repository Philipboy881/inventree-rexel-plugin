from rest_framework import serializers


class RexelRequestSerializer(serializers.Serializer):
    """Serializer voor validatie van Rexel data."""
    product_number = serializers.CharField(
        max_length=255,
        required=True,
        source='product_number'
    )
    part_number = serializers.CharField(
        max_length=255,
        required=True,
        source='part_number'
    )
