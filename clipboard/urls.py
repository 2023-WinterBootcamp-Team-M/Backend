from django.urls import path
from .views import GetClipboardView


urlpatterns = [
    path('clipboard/<int:clipboard_id>/', GetClipboardView.as_view(), name='clipboard_list')
]
