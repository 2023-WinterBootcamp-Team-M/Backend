from django.urls import path
from .views import DeleteAllImagesView


urlpatterns = [
    path('clipboard/<int:clipboard_id>/images/',
         DeleteAllImagesView.as_view(), name='delete_all_images')
]
