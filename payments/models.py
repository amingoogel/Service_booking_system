from django.db import models


class Payment(models.Model):
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name='رزرو',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='مبلغ')
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان پرداخت')
    transaction_id = models.CharField(max_length=50, unique=True, verbose_name='شناسه تراکنش')
    is_successful = models.BooleanField(default=True, verbose_name='موفق')

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'

    def __str__(self):
        return f'{self.transaction_id} - {self.amount}'
