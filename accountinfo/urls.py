from django.urls import path
from accountinfo import views
from .views import *

urlpatterns = [
    path('profile/<int:user_id>', delete_user),
    path('profile', profile_edit),
    path('signin', signin),
    path('signup', signup),
]