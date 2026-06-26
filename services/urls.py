from django.urls import path

from services import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list_view, name='list'),
    path('<int:pk>/', views.service_detail_view, name='detail'),
    path('admin/list/', views.admin_service_list, name='admin_list'),
    path('admin/<int:pk>/edit/', views.admin_service_edit, name='admin_edit'),
    path('admin/<int:pk>/delete/', views.admin_service_delete, name='admin_delete'),
]
