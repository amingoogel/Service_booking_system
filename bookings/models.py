from django.conf import settings
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار تأیید'
        CONFIRMED = 'confirmed', 'تأیید شده'
        REJECTED = 'rejected', 'رد شده'
        CANCELED = 'canceled', 'لغو شده'

    class PaymentStatus(models.TextChoices):
        UNPAID = 'unpaid', 'پرداخت نشده'
        PAID = 'paid', 'پرداخت شده'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='مشتری',
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_bookings',
        verbose_name='ارائه‌دهنده',
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='سرویس',
    )
    time_slot = models.OneToOneField(
        'services.TimeSlot',
        on_delete=models.CASCADE,
        related_name='booking',
        verbose_name='بازه زمانی',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='وضعیت',
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        verbose_name='وضعیت پرداخت',
    )
    price_snapshot = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='قیمت ثبت‌شده')
    duration_snapshot = models.PositiveIntegerField(verbose_name='مدت ثبت‌شده (دقیقه)')
    invoice_number = models.CharField(max_length=20, unique=True, blank=True, verbose_name='شماره فاکتور')
    cancel_deadline = models.DateTimeField(null=True, blank=True, verbose_name='مهلت لغو')
    canceled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='canceled_bookings',
        verbose_name='لغو شده توسط',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'رزرو'
        verbose_name_plural = 'رزروها'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Booking.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1001
            self.invoice_number = f'INV-{next_num}'
        if not self.cancel_deadline and self.time_slot_id:
            from datetime import timedelta
            self.cancel_deadline = self.time_slot.start_datetime - timedelta(hours=2)
        super().save(*args, **kwargs)

    def can_cancel(self):
        if self.status not in [self.Status.PENDING, self.Status.CONFIRMED]:
            return False
        if self.cancel_deadline and timezone.now() > self.cancel_deadline:
            return False
        return True

    def seconds_until_cancel_deadline(self):
        if not self.cancel_deadline:
            return 0
        delta = self.cancel_deadline - timezone.now()
        return max(0, int(delta.total_seconds()))

    def __str__(self):
        return f'{self.invoice_number} - {self.service.name}'
