from django.urls import path

from accounts import views

urlpatterns = [
    path('users/', views.admin_user_list, name='admin_users'),
    path('users/create/', views.admin_user_create, name='admin_user_create'),
    path('users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
]
