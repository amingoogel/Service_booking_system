from datetime import timedelta

from django.utils import timezone

from services.models import TimeSlot


def validate_no_overlap(service, start_datetime, end_datetime, exclude_pk=None):
    qs = TimeSlot.objects.filter(service=service, is_active=True)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    for slot in qs:
        if start_datetime < slot.end_datetime and end_datetime > slot.start_datetime:
            raise ValueError('بازه زمانی با بازه‌های موجود تداخل دارد.')


def validate_slot_duration(service, start_datetime, end_datetime):
    expected = timedelta(minutes=service.duration_minutes)
    actual = end_datetime - start_datetime
    if actual != expected:
        raise ValueError(
            f'مدت بازه باید {service.duration_minutes} دقیقه باشد '
            f'(از {start_datetime} تا {end_datetime}).'
        )


def validate_slot_times(start_datetime, end_datetime):
    if start_datetime >= end_datetime:
        raise ValueError('زمان پایان باید از زمان شروع بزرگتر باشد.')
    if start_datetime < timezone.now():
        raise ValueError('تاریخ و ساعت شروع نمی‌تواند از زمان فعلی گذشته باشد.')
