from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.decorators import role_required
from accounts.forms import RegisterForm, LoginForm, ProfileForm, CustomPasswordChangeForm, AdminUserForm
from accounts.models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        messages.success(self.request, 'ثبت‌نام با موفقیت انجام شد. وارد شوید.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ثبت‌نام انجام نشد. لطفاً خطاهای فرم را بررسی کنید.')
        return super().form_invalid(form)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'با موفقیت وارد شدید.')
            return redirect('home')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'با موفقیت خارج شدید.')
    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل به‌روزرسانی شد.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    form = CustomPasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'رمز عبور تغییر کرد.')
        return redirect('accounts:profile')
    return render(request, 'accounts/change_password.html', {'form': form})


@role_required('admin')
def admin_user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin/user_list.html', {'users': users})


@role_required('admin')
def admin_user_create(request):
    form = AdminUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        if not form.cleaned_data.get('password'):
            user.set_password('123456')
        else:
            user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(request, 'کاربر ایجاد شد.')
        return redirect('accounts:admin_users')
    return render(request, 'accounts/admin/user_form.html', {'form': form, 'title': 'ایجاد کاربر'})


@role_required('admin')
def admin_user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = AdminUserForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'کاربر ویرایش شد.')
        return redirect('accounts:admin_users')
    return render(request, 'accounts/admin/user_form.html', {'form': form, 'title': 'ویرایش کاربر'})


@role_required('admin')
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'نمی‌توانید خودتان را حذف کنید.')
        else:
            user.delete()
            messages.success(request, 'کاربر حذف شد.')
        return redirect('accounts:admin_users')
    return render(request, 'accounts/admin/user_confirm_delete.html', {'user_obj': user})
