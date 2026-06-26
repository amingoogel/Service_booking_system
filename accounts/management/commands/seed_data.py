from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking
from services.models import Category, Service, TimeSlot


class Command(BaseCommand):
    help = 'بارگذاری داده‌های نمونه برای دمو'

    def handle(self, *args, **options):
        self.stdout.write('در حال ایجاد داده‌های نمونه...')

        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@site.com',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'مدیر',
                'last_name': 'سیستم',
            },
        )
        admin.set_password('123456')
        admin.save()

        providers_data = [
            ('provider1', 'علی', 'احمدی', '09123456789', 'تعمیرات موبایل'),
            ('provider2', 'مریم', 'رضایی', '09121234567', 'آرایشگری'),
            ('provider3', 'حسین', 'کریمی', '09131234567', 'مشاوره تحصیلی'),
        ]
        providers = []
        for username, fn, ln, phone, _ in providers_data:
            p, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@site.com',
                    'role': User.Role.PROVIDER,
                    'first_name': fn,
                    'last_name': ln,
                    'phone': phone,
                    'is_active_provider': True,
                },
            )
            p.set_password('123456')
            p.save()
            providers.append(p)

        customer, _ = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer1@site.com',
                'role': User.Role.CUSTOMER,
                'first_name': 'رضا',
                'last_name': 'محمدی',
                'phone': '09111111111',
            },
        )
        customer.set_password('123456')
        customer.save()

        categories = {}
        for name, slug in [
            ('تعمیرات', 'repair'),
            ('زیبایی', 'beauty'),
            ('آموزش', 'education'),
        ]:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'slug': slug})
            categories[name] = cat

        services_data = [
            (providers[0], categories['تعمیرات'], 'تعمیر صفحه موبایل', 'تعویض گلس و LCD انواع گوشی', Decimal('350000'), 60),
            (providers[0], categories['تعمیرات'], 'تعمیر برد گوشی', 'عیب‌یابی و تعمیر برد', Decimal('500000'), 90),
            (providers[1], categories['زیبایی'], 'اصلاح مو', 'اصلاح و استایل مو', Decimal('150000'), 45),
            (providers[1], categories['زیبایی'], 'رنگ مو', 'رنگ و مش', Decimal('400000'), 120),
            (providers[2], categories['آموزش'], 'مشاوره کنکور', 'مشاوره انتخاب رشته و برنامه‌ریزی', Decimal('200000'), 60),
            (providers[2], categories['آموزش'], 'کلاس ریاضی', 'تدریس ریاضی دبیرستان', Decimal('180000'), 90),
        ]

        now = timezone.now()
        for provider, category, name, desc, price, duration in services_data:
            service, created = Service.objects.get_or_create(
                provider=provider,
                name=name,
                defaults={
                    'category': category,
                    'description': desc,
                    'price': price,
                    'duration_minutes': duration,
                    'status': Service.Status.ACTIVE,
                },
            )
            if created:
                for day in range(1, 8):
                    start = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=day)
                    for hour in [9, 11, 14, 16]:
                        slot_start = start.replace(hour=hour)
                        slot_end = slot_start + timedelta(minutes=duration)
                        TimeSlot.objects.get_or_create(
                            service=service,
                            start_datetime=slot_start,
                            defaults={
                                'end_datetime': slot_end,
                                'is_active': True,
                            },
                        )

        self.stdout.write(self.style.SUCCESS('داده‌های نمونه با موفقیت ایجاد شد.'))
        self.stdout.write('ادمین: admin@site.com / 123456')
        self.stdout.write('ارائه‌دهنده: provider1 / 123456')
        self.stdout.write('مشتری: customer1 / 123456')
