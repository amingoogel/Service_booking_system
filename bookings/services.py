import uuid

from django.db import transaction

from bookings.models import Booking
from notifications_app.models import Notification
from notifications_app.utils import send_realtime_notification


def create_notification(user, notification_type, message, link=''):
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        link=link,
    )
    send_realtime_notification(user.id, {
        'id': notification.id,
        'type': notification_type,
        'message': message,
        'link': link,
        'created_at': notification.created_at.isoformat(),
    })
    return notification


@transaction.atomic
def create_booking(customer, time_slot):
    service = time_slot.service
    if not service.provider.is_active_provider:
        raise ValueError('ارائه‌دهنده غیرفعال است.')
    if service.status != service.Status.ACTIVE:
        raise ValueError('سرویس غیرفعال است.')
    if not time_slot.is_active:
        raise ValueError('بازه زمانی غیرفعال است.')
    if time_slot.is_booked:
        raise ValueError('این بازه قبلاً رزرو شده است.')

    booking = Booking.objects.create(
        customer=customer,
        provider=service.provider,
        service=service,
        time_slot=time_slot,
        price_snapshot=service.price,
        duration_snapshot=service.duration_minutes,
        status=Booking.Status.PENDING,
    )
    create_notification(
        service.provider,
        Notification.NotificationType.NEW_BOOKING,
        f'رزرو جدید برای سرویس «{service.name}» توسط {customer.get_full_name() or customer.username}',
        link=f'/provider/bookings/',
    )
    return booking


def confirm_booking(booking, user):
    booking.status = Booking.Status.CONFIRMED
    booking.save()
    create_notification(
        booking.customer,
        Notification.NotificationType.BOOKING_CONFIRMED,
        f'رزرو شما برای «{booking.service.name}» تأیید شد.',
        link='/customer/bookings/',
    )


def reject_booking(booking, user):
    booking.status = Booking.Status.REJECTED
    booking.save()
    create_notification(
        booking.customer,
        Notification.NotificationType.BOOKING_REJECTED,
        f'رزرو شما برای «{booking.service.name}» رد شد.',
        link='/customer/bookings/',
    )


def cancel_booking(booking, user):
    booking.status = Booking.Status.CANCELED
    booking.canceled_by = user
    booking.save()
    if user == booking.customer:
        target = booking.provider
        msg = f'مشتری رزرو «{booking.service.name}» را لغو کرد.'
    else:
        target = booking.customer
        msg = f'ارائه‌دهنده رزرو «{booking.service.name}» را لغو کرد.'
    create_notification(
        target,
        Notification.NotificationType.BOOKING_CANCELED,
        msg,
        link='/customer/bookings/' if target == booking.customer else '/provider/bookings/',
    )


def process_payment(booking):
    if booking.payment_status == Booking.PaymentStatus.PAID:
        raise ValueError('این رزرو قبلاً پرداخت شده است.')
    from payments.models import Payment
    payment = Payment.objects.create(
        booking=booking,
        amount=booking.price_snapshot,
        transaction_id=f'TXN-{uuid.uuid4().hex[:12].upper()}',
    )
    booking.payment_status = Booking.PaymentStatus.PAID
    booking.save()
    create_notification(
        booking.customer,
        Notification.NotificationType.PAYMENT_SUCCESS,
        f'پرداخت رزرو «{booking.service.name}» با موفقیت انجام شد. شماره فاکتور: {booking.invoice_number}',
        link=f'/reports/invoice/{booking.pk}/',
    )
    create_notification(
        booking.provider,
        Notification.NotificationType.PAYMENT_SUCCESS,
        f'پرداخت جدید برای رزرو «{booking.service.name}» - {booking.price_snapshot} تومان',
        link='/provider/bookings/',
    )
    return payment
