from django.urls import path

from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.admin_dashboard, name='admin'),
    path('provider/', views.provider_dashboard, name='provider'),
]
