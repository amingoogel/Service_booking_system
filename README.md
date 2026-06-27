# سیستم مدیریت و رزرو خدمات

پروژه نهایی درس آزمایشگاه مهندسی نرم‌افزار - دانشگاه شهید چمران اهواز

## معرفی

سامانه جامع مدیریت و رزرو خدمات با سه نقش کاربری:
- **Admin**: مدیریت کاربران، سرویس‌ها، رزروها و گزارش‌های آماری
- **Provider**: تعریف سرویس و بازه زمانی، مدیریت رزروها
- **Customer**: جستجو، رزرو، پرداخت و ثبت نظر

## کتابخانه‌های مورد استفاده

- Django 5+
- Django Channels (WebSocket برای اعلان‌های Real-time)
- Daphne (ASGI server)
- ReportLab (تولید PDF)
- Pillow (مدیریت تصاویر)
- Bootstrap 5 RTL (رابط کاربری)
- Chart.js (نمودارهای داشبورد)

## ساختار پروژه

```
accounts/          - احراز هویت، پروفایل، مدیریت کاربران
services/          - سرویس‌ها، دسته‌بندی، بازه‌های زمانی
bookings/          - رزرو و لغو
payments/          - درگاه پرداخت (شبیه‌سازی)
reviews/           - نظرات و امتیازات
notifications_app/ - اعلان‌ها + WebSocket
reports/           - گزارش‌های PDF
dashboard/         - داشبوردهای Admin و Provider
```

## راه‌اندازی

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

برای WebSocket از Daphne استفاده کنید:
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## حساب‌های نمونه

| نقش | نام کاربری | رمز |
|-----|-----------|-----|
| Admin | admin | 123456 |
| Provider | provider1 | 123456 |
| Customer | customer1 | 123456 |

## قوانین کسب‌وکار

- همه رزروها ابتدا **Pending** هستند
- غیرفعال کردن Provider → سرویس‌هایش Inactive می‌شوند
- رزروهای قبلی با snapshot قیمت/مدت ثبت می‌شوند
- لغو رزرو تا ۲ ساعت قبل از شروع مجاز است
- ویرایش نظر تا ۲۴ ساعت، حذف فقط توسط Admin
- جستجو با Debounce ۳۰۰ms

## تست‌ها

```bash
python manage.py test
```

## گزارش‌های PDF

- فاکتور پرداخت (INV-xxxx)
- گزارش رزرو مشتری
- گزارش رزرو Provider
- گزارش آماری Admin (با تاریخ تولید)
