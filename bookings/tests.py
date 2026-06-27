from decimal import Decimal
from datetime import timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from bookings.models import Booking
from bookings.services import create_booking, process_payment
from reviews.models import Review
from services.models import Category, Service, TimeSlot


class AuthTests(TestCase):
    def test_register_and_login(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '09123456789',
            'role': 'customer',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

        login_ok = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_ok)


class ServiceTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username='prov', password='pass', role=User.Role.PROVIDER, email='p@p.com'
        )
        self.category = Category.objects.create(name='Test', slug='test')

    def test_create_service(self):
        service = Service.objects.create(
            provider=self.provider,
            category=self.category,
            name='Test Service',
            description='A test service description',
            price=Decimal('100'),
            duration_minutes=30,
        )
        self.assertEqual(service.name, 'Test Service')
        self.assertEqual(service.price, Decimal('100'))


class TimeSlotTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username='prov2', password='pass', role=User.Role.PROVIDER, email='p2@p.com'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            name='Slot Service',
            description='Service for slot testing here',
            price=Decimal('200'),
            duration_minutes=60,
        )

    def test_create_timeslot(self):
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(minutes=60)
        slot = TimeSlot.objects.create(
            service=self.service,
            start_datetime=start,
            end_datetime=end,
        )
        self.assertTrue(slot.is_available)


class BookingTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username='prov3', password='pass', role=User.Role.PROVIDER, email='p3@p.com'
        )
        self.customer = User.objects.create_user(
            username='cust', password='pass', role=User.Role.CUSTOMER, email='c@c.com'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            name='Book Service',
            description='Booking test service description',
            price=Decimal('300'),
            duration_minutes=30,
        )
        start = timezone.now() + timedelta(days=2)
        self.slot = TimeSlot.objects.create(
            service=self.service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        )

    def test_booking(self):
        booking = create_booking(self.customer, self.slot)
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertEqual(booking.price_snapshot, Decimal('300'))

    def test_double_booking_prevented(self):
        create_booking(self.customer, self.slot)
        customer2 = User.objects.create_user(
            username='cust2', password='pass', role=User.Role.CUSTOMER, email='c2@c.com'
        )
        with self.assertRaises(ValueError):
            create_booking(customer2, self.slot)


class PaymentTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username='prov4', password='pass', role=User.Role.PROVIDER, email='p4@p.com'
        )
        self.customer = User.objects.create_user(
            username='cust3', password='pass', role=User.Role.CUSTOMER, email='c3@c.com'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            name='Pay Service',
            description='Payment test service description',
            price=Decimal('500'),
            duration_minutes=60,
        )
        start = timezone.now() + timedelta(days=3)
        self.slot = TimeSlot.objects.create(
            service=self.service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=60),
        )
        self.booking = create_booking(self.customer, self.slot)
        self.booking.status = Booking.Status.CONFIRMED
        self.booking.save()

    def test_payment(self):
        payment = process_payment(self.booking)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, Booking.PaymentStatus.PAID)
        self.assertTrue(payment.transaction_id)

    def test_double_payment_prevented(self):
        process_payment(self.booking)
        with self.assertRaises(ValueError):
            process_payment(self.booking)


class ReviewTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user(
            username='prov5', password='pass', role=User.Role.PROVIDER, email='p5@p.com'
        )
        self.customer = User.objects.create_user(
            username='cust4', password='pass', role=User.Role.CUSTOMER, email='c4@c.com'
        )
        self.service = Service.objects.create(
            provider=self.provider,
            name='Review Service',
            description='Review test service description here',
            price=Decimal('100'),
            duration_minutes=30,
        )
        start = timezone.now() + timedelta(days=1)
        slot = TimeSlot.objects.create(
            service=self.service,
            start_datetime=start,
            end_datetime=start + timedelta(minutes=30),
        )
        self.booking = create_booking(self.customer, slot)
        self.booking.status = Booking.Status.CONFIRMED
        self.booking.save()

    def test_create_review(self):
        review = Review.objects.create(
            booking=self.booking,
            customer=self.customer,
            service=self.service,
            rating=5,
            comment='عالی بود',
        )
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.can_edit())
