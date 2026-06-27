from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render

from accounts.decorators import role_required
from bookings.models import Booking
from bookings.services import process_payment


@role_required('customer')
def payment_view(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, customer=request.user)
    if booking.payment_status == Booking.PaymentStatus.PAID:
        messages.info(request, 'این رزرو قبلاً پرداخت شده است.')
        return redirect('customer:bookings')
    if booking.status != Booking.Status.CONFIRMED:
        messages.error(request, 'فقط رزروهای تأیید شده قابل پرداخت هستند.')
        return redirect('customer:bookings')
    if request.method == 'POST':
        try:
            payment = process_payment(booking)
            messages.success(request, f'پرداخت موفق! شناسه تراکنش: {payment.transaction_id}')
            return redirect('reports:invoice', booking_pk=booking.pk)
        except ValueError as e:
            messages.error(request, str(e))
    return render(request, 'payments/payment.html', {'booking': booking})
