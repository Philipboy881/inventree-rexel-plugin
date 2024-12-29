from django.http import JsonResponse
from django.views import View


class RexelView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        # Voer je zoeklogica uit op basis van de query
        if query:
            # Simuleer zoekresultaten voor dit voorbeeld
            results = [
                {'name': 'Product 1', 'price': 10.99},
                {'name': 'Product 2', 'price': 15.49},
            ]
            return JsonResponse({'results': results})
        else:
            return JsonResponse({'error': 'No query provided'}, status=400)
