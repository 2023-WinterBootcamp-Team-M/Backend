from django.urls import path
from .views import PostClipboardView

urlpatterns = [
    path('clipboard/', PostClipboardView.as_view(), name='clipboard')
]
