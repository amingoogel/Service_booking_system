from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from accounts.decorators import role_required
from services.forms import ServiceForm, TimeSlotForm, ServiceSearchForm
from services.models import Service, TimeSlot, Category


def home_view(request):
    services = Service.objects.filter(
        status=Service.Status.ACTIVE,
        provider__is_active_provider=True,
    ).select_related('provider', 'category')[:6]
    return render(request, 'home.html', {'featured_services': services})


def service_list_view(request):
    form = ServiceSearchForm(request.GET or None)
    services = Service.objects.filter(
        status=Service.Status.ACTIVE,
        provider__is_active_provider=True,
    ).select_related('provider', 'category')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            services = services.filter(Q(name__icontains=q) | Q(description__icontains=q))
        category = form.cleaned_data.get('category')
        if category:
            services = services.filter(category=category)
        provider = form.cleaned_data.get('provider')
        if provider:
            services = services.filter(provider=provider)
        min_price = form.cleaned_data.get('min_price')
        if min_price is not None:
            services = services.filter(price__gte=min_price)
        max_price = form.cleaned_data.get('max_price')
        if max_price is not None:
            services = services.filter(price__lte=max_price)

    context = {'services': services, 'form': form}
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('services/_service_cards.html', context, request=request)
        return JsonResponse({'html': html, 'count': services.count()})
    return render(request, 'services/service_list.html', context)


def service_detail_view(request, pk):
    service = get_object_or_404(
        Service.objects.select_related('provider', 'category'),
        pk=pk,
        status=Service.Status.ACTIVE,
        provider__is_active_provider=True,
    )
    from django.utils import timezone
    slots = service.time_slots.filter(
        is_active=True,
        start_datetime__gte=timezone.now(),
    ).exclude(
        booking__status__in=['pending', 'confirmed']
    ).order_by('start_datetime')
    reviews = service.reviews.select_related('customer').all()[:10]
    return render(request, 'services/service_detail.html', {
        'service': service,
        'slots': slots,
        'reviews': reviews,
    })


@role_required('provider')
def provider_service_list(request):
    services = Service.objects.filter(provider=request.user)
    return render(request, 'services/provider/service_list.html', {'services': services})


@role_required('provider')
def provider_service_create(request):
    form = ServiceForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        service = form.save(commit=False)
        service.provider = request.user
        service.save()
        messages.success(request, 'سرویس ایجاد شد.')
        return redirect('provider:service_list')
    return render(request, 'services/provider/service_form.html', {'form': form, 'title': 'ایجاد سرویس'})


@role_required('provider')
def provider_service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    form = ServiceForm(request.POST or None, request.FILES or None, instance=service)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'سرویس ویرایش شد. رزروهای قبلی بدون تغییر باقی می‌مانند.')
        return redirect('provider:service_list')
    return render(request, 'services/provider/service_form.html', {'form': form, 'title': 'ویرایش سرویس'})


@role_required('provider')
def provider_service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, provider=request.user)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'سرویس حذف شد.')
        return redirect('provider:service_list')
    return render(request, 'services/provider/service_confirm_delete.html', {'service': service})


@role_required('provider')
def provider_timeslot_list(request, service_pk):
    service = get_object_or_404(Service, pk=service_pk, provider=request.user)
    slots = service.time_slots.all()
    return render(request, 'services/provider/timeslot_list.html', {'service': service, 'slots': slots})


@role_required('provider')
def provider_timeslot_create(request, service_pk):
    service = get_object_or_404(Service, pk=service_pk, provider=request.user)
    form = TimeSlotForm(request.POST or None, service=service, auto_end=True)
    if request.method == 'POST' and form.is_valid():
        slot = form.save(commit=False)
        slot.service = service
        slot.save()
        messages.success(request, 'بازه زمانی ایجاد شد.')
        return redirect('provider:timeslot_list', service_pk=service.pk)
    if request.method == 'POST':
        messages.error(request, 'بازه زمانی ایجاد نشد. خطاهای فرم را بررسی کنید.')
    return render(request, 'services/provider/timeslot_form.html', {
        'form': form, 'service': service, 'title': 'ایجاد بازه زمانی',
    })


@role_required('provider')
def provider_timeslot_edit(request, service_pk, pk):
    service = get_object_or_404(Service, pk=service_pk, provider=request.user)
    slot = get_object_or_404(TimeSlot, pk=pk, service=service)
    form = TimeSlotForm(request.POST or None, instance=slot, service=service)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'بازه زمانی ویرایش شد.')
        return redirect('provider:timeslot_list', service_pk=service.pk)
    return render(request, 'services/provider/timeslot_form.html', {
        'form': form, 'service': service, 'title': 'ویرایش بازه زمانی',
    })


@role_required('provider')
def provider_timeslot_toggle(request, service_pk, pk):
    service = get_object_or_404(Service, pk=service_pk, provider=request.user)
    slot = get_object_or_404(TimeSlot, pk=pk, service=service)
    slot.is_active = not slot.is_active
    slot.save()
    messages.success(request, f'بازه {"فعال" if slot.is_active else "غیرفعال"} شد.')
    return redirect('provider:timeslot_list', service_pk=service.pk)


@role_required('admin')
def admin_service_list(request):
    services = Service.objects.select_related('provider', 'category').all()
    return render(request, 'services/admin/service_list.html', {'services': services})


@role_required('admin')
def admin_service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, request.FILES or None, instance=service)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'سرویس ویرایش شد.')
        return redirect('services:admin_list')
    return render(request, 'services/provider/service_form.html', {'form': form, 'title': 'ویرایش سرویس (ادمین)'})


@role_required('admin')
def admin_service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'سرویس حذف شد.')
        return redirect('services:admin_list')
    return render(request, 'services/provider/service_confirm_delete.html', {'service': service})
