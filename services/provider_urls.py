from django.urls import path

from bookings import views as booking_views
from services import views

app_name = 'provider'

urlpatterns = [
    path('services/', views.provider_service_list, name='service_list'),
    path('services/create/', views.provider_service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.provider_service_edit, name='service_edit'),
    path('services/<int:pk>/delete/', views.provider_service_delete, name='service_delete'),
    path('services/<int:service_pk>/timeslots/', views.provider_timeslot_list, name='timeslot_list'),
    path('services/<int:service_pk>/timeslots/create/', views.provider_timeslot_create, name='timeslot_create'),
    path('services/<int:service_pk>/timeslots/<int:pk>/edit/', views.provider_timeslot_edit, name='timeslot_edit'),
    path('services/<int:service_pk>/timeslots/<int:pk>/toggle/', views.provider_timeslot_toggle, name='timeslot_toggle'),
    path('bookings/', booking_views.provider_bookings, name='bookings'),
    path('bookings/<int:pk>/confirm/', booking_views.provider_confirm_booking, name='confirm_booking'),
    path('bookings/<int:pk>/reject/', booking_views.provider_reject_booking, name='reject_booking'),
    path('bookings/<int:pk>/cancel/', booking_views.provider_cancel_booking, name='cancel_booking'),
]
