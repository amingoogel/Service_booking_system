from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm

from accounts.models import User
from services.validators import validate_phone


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='ایمیل')
    phone = forms.CharField(required=False, label='شماره تماس', validators=[validate_phone])
    role = forms.ChoiceField(
        choices=[(User.Role.CUSTOMER, 'مشتری'), (User.Role.PROVIDER, 'ارائه‌دهنده')],
        label='نقش',
        initial=User.Role.CUSTOMER,
    )
    first_name = forms.CharField(required=True, label='نام')
    last_name = forms.CharField(required=True, label='نام خانوادگی')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'نام کاربری یا رمز عبور اشتباه است.',
        'inactive': 'این حساب کاربری غیرفعال است.',
    }
    username = forms.CharField(label='نام کاربری', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_image']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
            'phone': 'شماره تماس',
            'profile_image': 'تصویر پروفایل',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        if 'phone' in self.fields:
            self.fields['phone'].validators.append(validate_phone)


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='رمز عبور فعلی', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='رمز عبور جدید', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='تکرار رمز عبور جدید', widget=forms.PasswordInput)


class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, label='رمز عبور جدید')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'is_active_provider']
        labels = {
            'username': 'نام کاربری',
            'email': 'ایمیل',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'phone': 'شماره تماس',
            'role': 'نقش',
            'is_active': 'فعال',
            'is_active_provider': 'ارائه‌دهنده فعال',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
