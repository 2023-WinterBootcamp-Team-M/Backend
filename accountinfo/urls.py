from django.urls import path
from .views import *

urlpatterns = [
    path('options', User_options_edit),
    path('options/<int:user_id>', User_options),
    path('profile/<int:user_id>', get_delete_user),
    path('sign-out',signout),
    path('profile', profile_edit),
    path('sign-in', signin),
    path('sign-up', signup),
]