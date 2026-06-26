from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from bookings.models import Booking
from bookings.services import create_booking, confirm_booking, reject_booking, cancel_booking
from services.models import TimeSlot


@role_required('customer')
def create_booking_view(request, slot_pk):
    slot = get_object_or_404(TimeSlot, pk=slot_pk)
    if request.method == 'POST':
        try:
            booking = create_booking(request.user, slot)
            messages.success(request, 'رزرو با موفقیت ثبت شد. در انتظار تأیید ارائه‌دهنده.')
            return redirect('customer:bookings')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('services:detail', pk=slot.service.pk)


@role_required('customer')
def customer_bookings(request):
    bookings = Booking.objects.filter(customer=request.user).select_related(
        'service', 'provider', 'time_slot'
    )
    reviewed_ids = set(
        request.user.reviews.values_list('booking_id', flat=True)
    )
    return render(request, 'bookings/customer/booking_list.html', {
        'bookings': bookings,
        'reviewed_ids': reviewed_ids,
    })


@role_required('customer')
def customer_cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if not booking.can_cancel():
        messages.error(request, 'مهلت لغو رزرو به پایان رسیده است.')
        return redirect('customer:bookings')
    if request.method == 'POST':
        cancel_booking(booking, request.user)
        messages.success(request, 'رزرو لغو شد.')
    return redirect('customer:bookings')


@role_required('provider')
def provider_bookings(request):
    bookings = Booking.objects.filter(provider=request.user).select_related(
        'service', 'customer', 'time_slot'
    )
    return render(request, 'bookings/provider/booking_list.html', {'bookings': bookings})


@role_required('provider')
@require_POST
def provider_confirm_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, provider=request.user)
    if booking.status == Booking.Status.PENDING:
        confirm_booking(booking, request.user)
        messages.success(request, 'رزرو تأیید شد.')
    return redirect('provider:bookings')


@role_required('provider')
@require_POST
def provider_reject_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, provider=request.user)
    if booking.status == Booking.Status.PENDING:
        reject_booking(booking, request.user)
        messages.success(request, 'رزرو رد شد.')
    return redirect('provider:bookings')


@role_required('provider')
@require_POST
def provider_cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, provider=request.user)
    if booking.status in [Booking.Status.PENDING, Booking.Status.CONFIRMED]:
        cancel_booking(booking, request.user)
        messages.success(request, 'رزرو لغو شد و به مشتری اطلاع داده شد.')
    return redirect('provider:bookings')


@role_required('admin')
def admin_booking_list(request):
    bookings = Booking.objects.select_related('service', 'customer', 'provider', 'time_slot').all()
    return render(request, 'bookings/admin/booking_list.html', {'bookings': bookings})


@role_required('admin')
def admin_force_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        cancel_booking(booking, request.user)
        messages.success(request, 'رزرو توسط ادمین لغو شد.')
    return redirect('bookings:admin_list')


@role_required('admin')
def admin_force_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST' and booking.status == Booking.Status.PENDING:
        confirm_booking(booking, request.user)
        messages.success(request, 'رزرو توسط ادمین تأیید شد.')
    return redirect('bookings:admin_list')
