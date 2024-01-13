from django.urls import path
from .views import PostClipboardView, GetClipboardView

urlpatterns = [
    path('clipboard/', PostClipboardView.as_view(), name='clipboard'),
    path('clipboard/<int:clipboard_id>/', GetClipboardView.as_view(), name='clipboard_list')

]
