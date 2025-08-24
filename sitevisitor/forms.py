from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from adminpanel.models import CustomUser, Profile
from django.contrib.auth import authenticate



class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']


class EmailOTPVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, label="Enter OTP")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'name', 'email', 'mobile', 'company', 'date_of_birth',
            'about_me', 'experience', 'skills', 'profile_picture'
        ]



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username/Email")


class CustomPasswordResetForm(PasswordResetForm):
    pass  # Use the default Django functionality


class CustomSetPasswordForm(SetPasswordForm):
    pass  # Use the default Django functionality

