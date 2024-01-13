from django.urls import path
from .views import classify_bookmark
urlpatterns = [
    path('classify',classify_bookmark, name='classify_bookmark'),
]