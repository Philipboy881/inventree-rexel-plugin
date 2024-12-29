from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView

from . import helpers  # Zorg ervoor dat helpers een functie bevat om met de API te communiceren


class RexelView(APIView):
    """View for handling search requests from the RexelPanel."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Handle the search request and return results."""
        # Haal de zoekterm op uit de queryparameters
        search_term = request.query_params.get('query', '').strip()

        # Controleer of een zoekterm aanwezig is
        if not search_term:
            return Response({'error': 'No search term provided'}, status=400)

        # Gebruik een helper-functie om de API-aanroep te doen of data te zoeken
        try:
            results = helpers.search_rexel_api(search_term)  # Zorg dat je `helpers.search_rexel_api` implementeert
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        # Retourneer de resultaten
        return Response({'results': results})
