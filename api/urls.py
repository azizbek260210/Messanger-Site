from django.urls import path
from . import views

urlpatterns = [
    path('user-create/', views.user_create),
    path('user-update/', views.user_update),
    path('group-create/', views.group_create),
]
