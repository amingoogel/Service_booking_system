import re
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_price(value):
    if value is None:
        raise ValidationError('قیمت باید عدد باشد.')
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError('قیمت باید عدد باشد.')
    str_value = str(value).strip()
    if not re.match(r'^\d+(\.\d+)?$', str_value.replace(',', '')):
        raise ValidationError('قیمت باید عدد صحیح یا اعشاری (با یک ممیز) باشد.')
    if decimal_value < 1:
        raise ValidationError('قیمت نمی‌تواند منفی یا صفر باشد. حداقل ۱ باشد.')


def validate_duration_minutes(value):
    if value is None:
        raise ValidationError('مدت زمان باید عدد باشد.')
    if not isinstance(value, int) or value <= 0:
        raise ValidationError('مدت زمان باید به دقیقه و عددی مثبت باشد (مثلاً ۳۰ یا ۶۰).')


def validate_service_name(value):
    if not value or len(value.strip()) < 3:
        raise ValidationError('نام سرویس باید حداقل ۳ کاراکتر باشد.')


def validate_description(value):
    if not value or not value.strip():
        raise ValidationError('توضیحات نمی‌تواند خالی باشد.')


def validate_phone(value):
    if not value:
        return
    cleaned = value.strip().replace(' ', '').replace('-', '')
    mobile_pattern = r'^09\d{9}$'
    landline_pattern = r'^0\d{2,3}\d{7,8}$'
    if re.match(mobile_pattern, cleaned):
        return
    if re.match(landline_pattern, cleaned):
        return
    raise ValidationError(
        'شماره تماس نامعتبر است. موبایل: ۰۹xxxxxxxxx (۱۱ رقم) یا '
        'تلفن ثابت: 0xx-xxxxxxxx'
    )


def validate_time_slot_start(value):
    if value and value < timezone.now():
        raise ValidationError('تاریخ و ساعت شروع نمی‌تواند از زمان فعلی گذشته باشد.')
