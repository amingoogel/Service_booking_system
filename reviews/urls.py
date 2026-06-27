from django.urls import path

from reviews import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:booking_pk>/', views.create_review, name='create'),
    path('edit/<int:pk>/', views.edit_review, name='edit'),
    path('provider/', views.provider_reviews, name='provider_list'),
    path('admin/', views.admin_reviews, name='admin_list'),
    path('admin/<int:pk>/delete/', views.admin_delete_review, name='admin_delete'),
]
