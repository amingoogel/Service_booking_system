from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from services.validators import validate_price, validate_duration_minutes


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

    def __str__(self):
        return self.name


class Service(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'فعال'
        INACTIVE = 'inactive', 'غیرفعال'

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services',
        limit_choices_to={'role': 'provider'},
        verbose_name='ارائه‌دهنده',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
        verbose_name='دسته‌بندی',
    )
    name = models.CharField(max_length=200, verbose_name='نام سرویس')
    description = models.TextField(verbose_name='توضیحات')
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_price, MinValueValidator(Decimal('1'))],
        verbose_name='قیمت',
    )
    duration_minutes = models.PositiveIntegerField(
        validators=[validate_duration_minutes],
        verbose_name='مدت زمان (دقیقه)',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='وضعیت',
    )
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        null=True,
        verbose_name='تصویر سرویس',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'سرویس'
        verbose_name_plural = 'سرویس‌ها'
        ordering = ['-created_at']

    def get_image_url(self):
        if self.image:
            return self.image.url
        return '/static/images/default-service.svg'

    @property
    def average_rating(self):
        from django.db.models import Avg
        result = self.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'] or 0, 1)

    @property
    def review_count(self):
        return self.reviews.count()

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name='سرویس',
    )
    start_datetime = models.DateTimeField(verbose_name='زمان شروع')
    end_datetime = models.DateTimeField(verbose_name='زمان پایان')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'بازه زمانی'
        verbose_name_plural = 'بازه‌های زمانی'
        ordering = ['start_datetime']

    @property
    def is_booked(self):
        from bookings.models import Booking
        try:
            return self.booking.status in [Booking.Status.PENDING, Booking.Status.CONFIRMED]
        except Booking.DoesNotExist:
            return False

    @property
    def is_available(self):
        return self.is_active and not self.is_booked

    def __str__(self):
        return f'{self.service.name} - {self.start_datetime}'
