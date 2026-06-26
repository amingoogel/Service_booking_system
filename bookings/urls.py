from django.urls import path

from bookings import views

app_name = 'bookings'

urlpatterns = [
    path('admin/list/', views.admin_booking_list, name='admin_list'),
    path('admin/<int:pk>/force-cancel/', views.admin_force_cancel, name='admin_force_cancel'),
    path('admin/<int:pk>/force-confirm/', views.admin_force_confirm, name='admin_force_confirm'),
]
