from django.urls import path
from .views import *

urlpatterns = [
    path('setting/edit', User_options_edit),
    path('setting/<int:user_id>', User_options),
    path('profile/delete/<int:user_id>', delete_user),
    path('profile/<int:user_id>', profile),

    path('profile', profile_edit),
    path('signin', signin),
    path('signup', signup),
]