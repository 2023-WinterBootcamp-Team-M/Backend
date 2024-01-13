from django.urls import path
from .views import DeleteImagesView

urlpatterns = [
    path('clipboard/<int:clipboard_id>/<int:image_id>/',
         DeleteImagesView.as_view(), name='delete_image')
]
