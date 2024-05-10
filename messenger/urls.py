from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search_group, name='search'),
    path('join-request/<str:code>/delete/', views.delete_join_request, name='delete_join_request'),
    path('join-requests/<str:code>/accept/', views.accept_join_request, name='accept_join_request'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<str:code>/join/', views.send_join_request, name='send_join_request'),
    path('leave-group/<str:code>/leave/', views.leave_group, name='leave_group'),
    path('groups/<str:code>/messages/', views.group_messages, name='group_messages'),
    path('groups/<str:code>/send-message/', views.send_message, name='send_message'),
]
