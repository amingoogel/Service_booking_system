from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import role_required
from bookings.models import Booking
from reviews.forms import ReviewForm
from reviews.models import Review


@role_required('customer')
def create_review(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, customer=request.user)
    if booking.status != Booking.Status.CONFIRMED:
        messages.error(request, 'فقط برای رزروهای تأیید شده می‌توانید نظر بدهید.')
        return redirect('customer:bookings')
    if hasattr(booking, 'review'):
        messages.info(request, 'شما قبلاً نظر دادید.')
        return redirect('customer:bookings')
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.booking = booking
        review.customer = request.user
        review.service = booking.service
        review.save()
        messages.success(request, 'نظر شما ثبت شد.')
        return redirect('customer:bookings')
    return render(request, 'reviews/review_form.html', {'form': form, 'booking': booking})


@role_required('customer')
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, customer=request.user)
    if not review.can_edit():
        messages.error(request, 'مهلت ویرایش نظر (۲۴ ساعت) به پایان رسیده است.')
        return redirect('customer:bookings')
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'نظر ویرایش شد.')
        return redirect('customer:bookings')
    return render(request, 'reviews/review_form.html', {'form': form, 'booking': review.booking, 'edit': True})


@role_required('provider')
def provider_reviews(request):
    reviews = Review.objects.filter(service__provider=request.user).select_related('customer', 'service')
    return render(request, 'reviews/provider_reviews.html', {'reviews': reviews})


@role_required('admin')
def admin_reviews(request):
    reviews = Review.objects.select_related('customer', 'service').all()
    return render(request, 'reviews/admin_reviews.html', {'reviews': reviews})


@role_required('admin')
def admin_delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'نظر حذف شد.')
    return redirect('reviews:admin_list')
