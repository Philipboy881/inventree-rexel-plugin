"""API views for the Order History plugin."""

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


class RexelView(APIView):
    """
    API-endpoint om onderdelen van Rexel te importeren.
    """

    def post(self, request, *args, **kwargs):
        # Haal gegevens op uit het verzoek
        data = request.data
        product_number = data.get('productNumber')
        part_number = data.get('partNumber')

        # Validatie van invoer
        if not product_number or not part_number:
            return Response(
                {'error': 'Invalid input. Both productNumber and partNumber are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verwerk de invoer (voorbeeld)
        # In een echte situatie zou je een externe API-aanroep of databaseverwerking uitvoeren
        processed_data = {
            'productNumber': product_number,
            'partNumber': part_number,
            'status': 'success',
            'message': f'Processed part {part_number} for product {product_number}.'
        }

        return Response(processed_data, status=status.HTTP_200_OK)
