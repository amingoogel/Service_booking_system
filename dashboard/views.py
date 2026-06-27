from datetime import timedelta
import json

from django.db.models import Sum, Count
from django.utils import timezone
from django.shortcuts import render

from accounts.decorators import role_required
from accounts.models import User
from bookings.models import Booking
from services.models import Service


@role_required('admin')
def admin_dashboard(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    day_ago = now - timedelta(days=1)

    context = {
        'total_users': User.objects.count(),
        'providers_count': User.objects.filter(role=User.Role.PROVIDER).count(),
        'customers_count': User.objects.filter(role=User.Role.CUSTOMER).count(),
        'total_bookings': Booking.objects.count(),
        'daily_bookings': Booking.objects.filter(created_at__gte=day_ago).count(),
        'weekly_bookings': Booking.objects.filter(created_at__gte=week_ago).count(),
        'active_services': Service.objects.filter(status=Service.Status.ACTIVE).count(),
        'inactive_services': Service.objects.filter(status=Service.Status.INACTIVE).count(),
        'total_revenue': Booking.objects.filter(
            payment_status=Booking.PaymentStatus.PAID
        ).aggregate(total=Sum('price_snapshot'))['total'] or 0,
        'top_services': Service.objects.annotate(
            booking_count=Count('bookings')
        ).order_by('-booking_count')[:5],
        'status_counts': {
            s[0]: Booking.objects.filter(status=s[0]).count()
            for s in Booking.Status.choices
        },
        'chart_labels': json.dumps(['در انتظار', 'تأیید', 'رد', 'لغو']),
        'chart_data': json.dumps([
            Booking.objects.filter(status='pending').count(),
            Booking.objects.filter(status='confirmed').count(),
            Booking.objects.filter(status='rejected').count(),
            Booking.objects.filter(status='canceled').count(),
        ]),
    }
    return render(request, 'dashboard/admin.html', context)


@role_required('provider')
def provider_dashboard(request):
    user = request.user
    context = {
        'services_count': Service.objects.filter(provider=user).count(),
        'total_bookings': Booking.objects.filter(provider=user).count(),
        'total_revenue': Booking.objects.filter(
            provider=user, payment_status=Booking.PaymentStatus.PAID
        ).aggregate(total=Sum('price_snapshot'))['total'] or 0,
        'status_counts': {
            s[0]: Booking.objects.filter(provider=user, status=s[0]).count()
            for s in Booking.Status.choices
        },
        'chart_labels': json.dumps(['در انتظار', 'تأیید', 'رد', 'لغو']),
        'chart_data': json.dumps([
            Booking.objects.filter(provider=user, status='pending').count(),
            Booking.objects.filter(provider=user, status='confirmed').count(),
            Booking.objects.filter(provider=user, status='rejected').count(),
            Booking.objects.filter(provider=user, status='canceled').count(),
        ]),
        'recent_bookings': Booking.objects.filter(provider=user).select_related(
            'service', 'customer'
        )[:5],
    }
    return render(request, 'dashboard/provider.html', context)
