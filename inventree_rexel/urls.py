from django.urls import path
from inventree_rexel.views import import_rexel_hello_world  # Vervang 'your_app_name' met de naam van je app

urlpatterns = [
    path('plugin/inventree_rexel/', import_rexel_hello_world),  # Nieuwe route voor de API
]
