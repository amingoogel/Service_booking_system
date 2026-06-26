from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('admin/users/', views.admin_user_list, name='admin_users'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
]
