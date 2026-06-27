from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle

from accounts.decorators import role_required
from bookings.models import Booking
from reports.pdf_utils import fa_cell, fa_paragraph, get_pdf_styles


def _build_pdf_response(filename, story):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@role_required('customer', 'provider', 'admin')
def invoice_pdf(request, booking_pk):
    booking = get_object_or_404(
        Booking.objects.select_related('customer', 'provider', 'service', 'time_slot'),
        pk=booking_pk,
    )
    if request.user.is_customer and booking.customer != request.user:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('home')
    if request.user.is_provider and booking.provider != request.user:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('home')

    title_style, normal, _ = get_pdf_styles()
    story = [
        fa_paragraph('فاکتور پرداخت', title_style),
        fa_paragraph(f'تاریخ تولید: {timezone.localtime().strftime("%Y/%m/%d %H:%M")}', normal),
        Spacer(1, 12),
        fa_paragraph(f'شماره فاکتور: {booking.invoice_number}', normal),
        fa_paragraph(f'مشتری: {booking.customer.get_full_name() or booking.customer.username}', normal),
        fa_paragraph(f'ارائه‌دهنده: {booking.provider.get_full_name() or booking.provider.username}', normal),
        fa_paragraph(f'سرویس: {booking.service.name}', normal),
        fa_paragraph(f'مدت زمان: {booking.duration_snapshot} دقیقه', normal),
        fa_paragraph(
            f'تاریخ و ساعت رزرو: {timezone.localtime(booking.time_slot.start_datetime).strftime("%Y/%m/%d %H:%M")}',
            normal,
        ),
        fa_paragraph(f'مبلغ پرداختی: {booking.price_snapshot:,.0f} تومان', normal),
        fa_paragraph(f'وضعیت پرداخت: {booking.get_payment_status_display()}', normal),
    ]
    return _build_pdf_response(f'{booking.invoice_number}.pdf', story)


@role_required('customer')
def customer_bookings_pdf(request):
    bookings = Booking.objects.filter(customer=request.user).select_related('service', 'provider', 'time_slot')
    title_style, normal, cell_style = get_pdf_styles()
    story = [
        fa_paragraph('گزارش رزروهای مشتری', title_style),
        fa_paragraph(f'تاریخ تولید: {timezone.localtime().strftime("%Y/%m/%d %H:%M")}', normal),
        fa_paragraph(f'مشتری: {request.user.get_full_name() or request.user.username}', normal),
        Spacer(1, 12),
    ]
    data = [[
        fa_cell('فاکتور', cell_style),
        fa_cell('سرویس', cell_style),
        fa_cell('تاریخ', cell_style),
        fa_cell('وضعیت', cell_style),
        fa_cell('مبلغ', cell_style),
    ]]
    for b in bookings:
        data.append([
            fa_cell(b.invoice_number, cell_style),
            fa_cell(b.service.name, cell_style),
            fa_cell(timezone.localtime(b.time_slot.start_datetime).strftime('%Y/%m/%d %H:%M'), cell_style),
            fa_cell(b.get_status_display(), cell_style),
            fa_cell(f'{b.price_snapshot:,.0f}', cell_style),
        ])
    table = Table(data, colWidths=[3 * cm, 4 * cm, 3.5 * cm, 3 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(table)
    return _build_pdf_response('customer_bookings.pdf', story)


@role_required('provider')
def provider_bookings_pdf(request):
    bookings = Booking.objects.filter(provider=request.user).select_related('service', 'customer', 'time_slot')
    title_style, normal, cell_style = get_pdf_styles()
    story = [
        fa_paragraph('گزارش رزروهای ارائه‌دهنده', title_style),
        fa_paragraph(f'تاریخ تولید: {timezone.localtime().strftime("%Y/%m/%d %H:%M")}', normal),
        fa_paragraph(f'ارائه‌دهنده: {request.user.get_full_name() or request.user.username}', normal),
        Spacer(1, 12),
    ]
    data = [[
        fa_cell('فاکتور', cell_style),
        fa_cell('سرویس', cell_style),
        fa_cell('مشتری', cell_style),
        fa_cell('تاریخ', cell_style),
        fa_cell('وضعیت', cell_style),
        fa_cell('مبلغ', cell_style),
    ]]
    for b in bookings:
        data.append([
            fa_cell(b.invoice_number, cell_style),
            fa_cell(b.service.name, cell_style),
            fa_cell(b.customer.username, cell_style),
            fa_cell(timezone.localtime(b.time_slot.start_datetime).strftime('%Y/%m/%d %H:%M'), cell_style),
            fa_cell(b.get_status_display(), cell_style),
            fa_cell(f'{b.price_snapshot:,.0f}', cell_style),
        ])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(table)
    return _build_pdf_response('provider_bookings.pdf', story)


@role_required('admin')
def admin_stats_pdf(request):
    from accounts.models import User
    from services.models import Service
    from django.db.models import Sum, Count

    title_style, normal, _ = get_pdf_styles()
    total_users = User.objects.count()
    providers = User.objects.filter(role=User.Role.PROVIDER).count()
    customers = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_bookings = Booking.objects.count()
    active_services = Service.objects.filter(status=Service.Status.ACTIVE).count()
    inactive_services = Service.objects.filter(status=Service.Status.INACTIVE).count()
    total_revenue = Booking.objects.filter(payment_status=Booking.PaymentStatus.PAID).aggregate(
        total=Sum('price_snapshot')
    )['total'] or 0

    story = [
        fa_paragraph('گزارش آماری مدیریت', title_style),
        fa_paragraph(f'تاریخ تولید گزارش: {timezone.localtime().strftime("%Y/%m/%d %H:%M")}', normal),
        Spacer(1, 12),
        fa_paragraph(f'تعداد کل کاربران: {total_users}', normal),
        fa_paragraph(f'  - ارائه‌دهندگان: {providers}', normal),
        fa_paragraph(f'  - مشتریان: {customers}', normal),
        fa_paragraph(f'تعداد کل رزروها: {total_bookings}', normal),
        fa_paragraph(f'سرویس‌های فعال: {active_services}', normal),
        fa_paragraph(f'سرویس‌های غیرفعال: {inactive_services}', normal),
        fa_paragraph(f'درآمد کل (فرضی): {total_revenue:,.0f} تومان', normal),
    ]

    top_services = Service.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]
    story.append(Spacer(1, 12))
    story.append(fa_paragraph('پررزروترین سرویس‌ها:', normal))
    for s in top_services:
        story.append(fa_paragraph(f'  - {s.name}: {s.booking_count} رزرو', normal))

    return _build_pdf_response('admin_stats.pdf', story)
