from django.http import JsonResponse


def import_rexel_hello_world(request):
    """Return a simple 'Hello World' message."""
    return JsonResponse({"message": "Hello World"})
