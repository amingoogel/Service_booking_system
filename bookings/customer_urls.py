from django.urls import path

from bookings import views

app_name = 'customer'

urlpatterns = [
    path('book/<int:slot_pk>/', views.create_booking_view, name='book'),
    path('bookings/', views.customer_bookings, name='bookings'),
    path('bookings/<int:pk>/cancel/', views.customer_cancel_booking, name='cancel_booking'),
]
