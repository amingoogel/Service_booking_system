from django.urls import path

from reports import views

app_name = 'reports'

urlpatterns = [
    path('invoice/<int:booking_pk>/', views.invoice_pdf, name='invoice'),
    path('customer/bookings/', views.customer_bookings_pdf, name='customer_bookings'),
    path('provider/bookings/', views.provider_bookings_pdf, name='provider_bookings'),
    path('admin/stats/', views.admin_stats_pdf, name='admin_stats'),
]
