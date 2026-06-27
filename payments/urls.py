from django.urls import path

from payments import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:booking_pk>/', views.payment_view, name='pay'),
]
