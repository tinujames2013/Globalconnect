from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
from .forms import CustomUserRegistrationForm, ProfileForm
from adminpanel.models import CustomUser, EmailOTP, Job, Profile
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

def home(request):
    jobs = Job.objects.all()
    context = {
        'jobs': jobs,
        'meta_title': "Global Connect - Find jobs & recruiters",
        'meta_description': "Find your dream job or connect with top recruiters. Create CVs, apply & track."
    }
    return render(request, 'sitevisitor/home.html', context)



def login_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            if role == 'recruiter' and user.is_recruiter:
                login(request, user)
                return redirect('jobs:jobs_home')
            elif role == 'candidate' and user.is_candidate:
                login(request, user)
                return redirect('users:users_home')
            else:
                messages.error(request, "Role mismatch. Please select the correct role.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'sitevisitor/login.html')

def register_view(request):
    stage = "register"  # either "register" or "verify"
    otp_sent = False
    email = None

    if request.method == 'POST':
        # Step 1 → User submits registration form
        if 'send_otp' in request.POST:
            reg_form = CustomUserRegistrationForm(request.POST)
            if reg_form.is_valid():
                user = reg_form.save(commit=False)
                user.is_active = False  # user cannot log in until OTP verified
                user.save()

                # Generate OTP
                otp_code = str(random.randint(100000, 999999))
                EmailOTP.objects.update_or_create(
                    user=user, defaults={'otp_code': otp_code}
                )

                # Send OTP via email
                send_mail(
                    subject="Your OTP for Email Verification",
                    message=f"Dear {user.username},\n\nYour OTP is: {otp_code}\n\nThank you.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                messages.success(request, "OTP sent to your email.")
                stage = "verify"
                otp_sent = True
                email = user.email
                request.session['pending_user_id'] = user.id
            else:
                messages.error(request, "Please fix the errors below.")

        # Step 2 → User submits OTP for verification
        elif 'verify_otp' in request.POST:
            user_id = request.session.get('pending_user_id')
            if not user_id:
                messages.error(request, "Session expired. Please register again.")
                return redirect('sitevisitor:register')

            try:
                user = CustomUser.objects.get(id=user_id)
                otp_obj = EmailOTP.objects.get(user=user)
            except (CustomUser.DoesNotExist, EmailOTP.DoesNotExist):
                messages.error(request, "Invalid request.")
                return redirect('sitevisitor:register')

            entered_otp = request.POST.get('otp')
            if entered_otp == otp_obj.otp_code:
                # Activate user
                user.is_active = True
                user.is_email_verified = True
                user.save()
                otp_obj.delete()

                # Create empty profile (basic starter)
                Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        "name": user.username,
                        "email": user.email,
                    }
                )

                # Log user in
                login(request, user)
                messages.success(request, "Registration successful and email verified!")

                # Redirect based on role
                if user.is_candidate:
                    return redirect('users:users_home')
                elif user.is_recruiter:
                    return redirect('jobs:jobs_home')
                return redirect('sitevisitor:home')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                stage = "verify"
                otp_sent = True
                email = user.email

    else:
        reg_form = CustomUserRegistrationForm()

    return render(request, 'sitevisitor/register.html', {
        'stage': stage,
        'otp_sent': otp_sent,
        'email': email,
        'reg_form': CustomUserRegistrationForm()
    })


def create_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile created successfully!")
            return redirect('profile_detail', pk=profile.pk)
    else:
        form = ProfileForm()
    return render(request, 'sitevisitor/login.html', {'form': form})
