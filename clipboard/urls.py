from django.urls import path
from .views import DeleteAllImagesView, PostClipboardView, GetClipboardView, DeleteImagesView


urlpatterns = [
    path('clipboard/', PostClipboardView.as_view(), name='clipboard'),
    path('clipboard/<int:clipboard_id>/', GetClipboardView.as_view(), name='clipboard_list'),
    path('clipboard/<int:clipboard_id>/images/',
         DeleteAllImagesView.as_view(), name='delete_all_images'),
    path('clipboard/<int:clipboard_id>/<int:image_id>/',
         DeleteImagesView.as_view(), name='delete_image')

]
