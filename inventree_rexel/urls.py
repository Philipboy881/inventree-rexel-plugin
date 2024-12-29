from django.urls import path
from . import views

urlpatterns = [
    path('rexel/', views.RexelView.as_view(), name='rexel_search'),  # Definieer de URL voor de zoekfunctie
]
