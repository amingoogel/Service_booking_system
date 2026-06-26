from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'مدیر'
        PROVIDER = 'provider', 'ارائه‌دهنده'
        CUSTOMER = 'customer', 'مشتری'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=15, blank=True, verbose_name='شماره تماس')
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name='تصویر پروفایل',
    )
    is_active_provider = models.BooleanField(default=True, verbose_name='ارائه‌دهنده فعال')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_provider(self):
        return self.role == self.Role.PROVIDER

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def get_profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return '/static/images/default-avatar.svg'

    def __str__(self):
        return self.username
