from datetime import timedelta

from django import forms
from django.utils import timezone

from services.models import Category, Service, TimeSlot
from services.validators import (
    validate_description,
    validate_duration_minutes,
    validate_price,
    validate_service_name,
    validate_time_slot_start,
)
from services.utils import validate_no_overlap, validate_slot_duration, validate_slot_times

DATETIME_LOCAL_FORMATS = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration_minutes', 'category', 'status', 'image']
        labels = {
            'name': 'نام سرویس',
            'description': 'توضیحات',
            'price': 'قیمت (تومان)',
            'duration_minutes': 'مدت زمان (دقیقه)',
            'category': 'دسته‌بندی',
            'status': 'وضعیت',
            'image': 'تصویر سرویس',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].validators.append(validate_service_name)
        self.fields['description'].validators.append(validate_description)
        self.fields['price'].validators.append(validate_price)
        self.fields['duration_minutes'].validators.append(validate_duration_minutes)

    def clean_price(self):
        value = self.cleaned_data['price']
        validate_price(value)
        return value


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['start_datetime', 'end_datetime', 'is_active']
        labels = {
            'start_datetime': 'زمان شروع',
            'end_datetime': 'زمان پایان',
            'is_active': 'فعال',
        }
        widgets = {
            'start_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M',
            ),
            'end_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M',
            ),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, service=None, auto_end=False, **kwargs):
        self.service = service
        self.auto_end = auto_end
        super().__init__(*args, **kwargs)
        self.fields['start_datetime'].input_formats = DATETIME_LOCAL_FORMATS
        self.fields['start_datetime'].validators.append(validate_time_slot_start)

        if auto_end and service:
            self.fields.pop('end_datetime')
            self.fields['start_datetime'].help_text = (
                f'زمان پایان به‌صورت خودکار {service.duration_minutes} دقیقه بعد از شروع محاسبه می‌شود.'
            )

        if not auto_end and 'end_datetime' in self.fields:
            self.fields['end_datetime'].input_formats = DATETIME_LOCAL_FORMATS

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_datetime')
        if not start or not self.service:
            return cleaned

        end = cleaned.get('end_datetime')
        if self.auto_end:
            end = start + timedelta(minutes=self.service.duration_minutes)
            cleaned['end_datetime'] = end

        if end:
            try:
                validate_slot_times(start, end)
                validate_slot_duration(self.service, start, end)
                validate_no_overlap(
                    self.service, start, end,
                    exclude_pk=self.instance.pk if self.instance.pk else None,
                )
            except ValueError as e:
                raise forms.ValidationError(str(e))
        return cleaned


class ServiceSearchForm(forms.Form):
    q = forms.CharField(required=False, label='جستجو')
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='همه دسته‌ها',
        label='دسته‌بندی',
    )
    provider = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='همه ارائه‌دهندگان',
        label='ارائه‌دهنده',
    )
    min_price = forms.DecimalField(required=False, label='حداقل قیمت')
    max_price = forms.DecimalField(required=False, label='حداکثر قیمت')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import User
        self.fields['provider'].queryset = User.objects.filter(role=User.Role.PROVIDER, is_active=True)
        for name, field in self.fields.items():
            if name in ('category', 'provider'):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
