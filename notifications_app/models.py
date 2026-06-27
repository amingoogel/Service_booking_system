from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        NEW_BOOKING = 'new_booking', 'رزرو جدید'
        BOOKING_CONFIRMED = 'booking_confirmed', 'تأیید رزرو'
        BOOKING_REJECTED = 'booking_rejected', 'رد رزرو'
        BOOKING_CANCELED = 'booking_canceled', 'لغو رزرو'
        PAYMENT_SUCCESS = 'payment_success', 'پرداخت موفق'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='کاربر',
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        verbose_name='نوع',
    )
    message = models.TextField(verbose_name='پیام')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    link = models.CharField(max_length=200, blank=True, verbose_name='لینک')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.get_notification_type_display()}'
