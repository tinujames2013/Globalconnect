from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from adminpanel.models import Profile,Job, Application,NotificationPreference,CandidateDocument,CustomUser,Resume
from .forms import (ProfileEditForm, ProfileForm, DocumentUploadForm,JobSearchForm, 
                    CandidateDocument, ApplicationForm,NotificationPreferenceForm,
                    ResumeForm, )

from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from django.contrib.auth.models import User  # Import the User model

from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string

try:
    from weasyprint import HTML
except ImportError:
    HTML = None


class ResumeListView(ListView):
    model = Resume
    template_name = 'users/list.html'

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user) if self.request.user.is_authenticated else Resume.objects.none()


@login_required
def resume_create(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            messages.success(request, "Resume created successfully.")
            return redirect('users:preview', pk=resume.pk)
    else:
        form = ResumeForm()

    return render(request, 'users/edit.html', {
        'form': form,
        'is_create': True,
    })


@login_required
def resume_edit(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume updated successfully.")
            return redirect('users:preview', pk=resume.pk)
    else:
        form = ResumeForm(instance=resume)

    return render(request, 'users/edit.html', {
        'form': form,
        'is_create': False,
        'resume': resume,
    })


@login_required
def change_template(request, pk, key):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    valid_templates = dict(Resume.TEMPLATE_CHOICES).keys()

    if key not in valid_templates:
        raise Http404("Invalid template")

    resume.template_key = key
    resume.save(update_fields=['template_key'])

    messages.info(request, f"Template changed to {key}.")
    return redirect('users:preview', pk=resume.pk)

@login_required
def preview_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)

    # Map user’s template choice
    template_map = {
        'classic': 'users/classic.html',
        'sidebar': 'users/sidebar.html',
        'modern': 'users/modern.html',
        'elegant': 'users/elegant.html',
        'professional': 'users/professional.html',
        'creative': 'users/creative.html',
    }

    tpl = template_map.get(resume.template_key, 'users/classic.html')

    # ✅ Preprocess split fields
    skills = [s.strip() for s in resume.skills.split(",")] if resume.skills else []
    languages = [l.strip() for l in resume.languages.split(",")] if resume.languages else []
    awards = [a.strip() for a in resume.awards.split("\n")] if resume.awards else []
    experiences = [e.strip() for e in resume.experiences.split("\n")] if resume.experiences else []
    educations = [ed.strip() for ed in resume.educations.split("\n")] if resume.educations else []

    # 👉 Always render preview.html and pass the actual template (tpl)
    return render(request, tpl, {
    'resume': resume,
    'skills': skills,
    'languages': languages,
    'awards': awards,
    'experiences': experiences,
    'educations': educations,
})



@login_required
def resume_delete(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)

    if request.method == 'POST':
        resume.delete()
        messages.info(request, "Resume deleted successfully.")
        return redirect('users:list')

    return render(request, 'users/confirm_delete.html', {'resume': resume})


@login_required
def resume_pdf(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)

    # Preprocess split fields (same as preview)
    skills = [s.strip() for s in resume.skills.split(",")] if resume.skills else []
    languages = [l.strip() for l in resume.languages.split(",")] if resume.languages else []
    awards = [a.strip() for a in resume.awards.split("\n")] if resume.awards else []
    experiences = [e.strip() for e in resume.experiences.split("\n")] if resume.experiences else []
    educations = [ed.strip() for ed in resume.educations.split("\n")] if resume.educations else []

    # Map template_key to PDF template
    template_map = {
        'classic': 'users/classic_pdf.html',
        'sidebar': 'users/sidebar_pdf.html',
        'modern': 'users/modern_pdf.html',
        'elegant': 'users/elegant_pdf.html',
        'professional': 'users/professional_pdf.html',
        'creative': 'users/creative_pdf.html',
    }

    tpl = template_map.get(resume.template_key, 'users/classic_pdf.html')

    # ✅ Pass all fields to template
    html_content = render_to_string(tpl, {
        'resume': resume,
        'skills': skills,
        'languages': languages,
        'awards': awards,
        'experiences': experiences,
        'educations': educations,
    })

    if HTML is None:  # fallback if WeasyPrint not installed
        return HttpResponse(html_content)

    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.title}.pdf"'
    return response

FREE_VISIBLE_TYPES = {"Contract", "Freelance", "Commission"}
PAID_ONLY_TYPES = {"Part Time", "Full Time"}


def home(request):
    """
    Display all jobs on the home page.
    Free users -> can only apply to FREE_VISIBLE_TYPES
    Premium users -> can apply to all jobs
    """
    jobs = Job.objects.filter(status="active")

    is_premium = False
    if request.user.is_authenticated:
        is_premium = request.user.check_premium_status()  # your custom method

    return render(request, "users/users_home.html", {
        "jobs": jobs,
        "FREE_VISIBLE_TYPES": FREE_VISIBLE_TYPES,
        "PAID_ONLY_TYPES": PAID_ONLY_TYPES,
        "IS_PREMIUM": is_premium,
    })



@login_required
def create_profile(request):
    if hasattr(request.user, 'profile'):
        messages.info(request, "Profile already exists. You can edit it.")
        return redirect('users:edit_profile')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile created successfully!")
            return redirect('users:view_profile')
    else:
        form = ProfileForm()

    return render(request, 'users/create_profile.html', {'form': form})

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)  # Handle file uploads
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('users:view_profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/edit_profile.html', {'form': form})




@login_required
def edit_candidate_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('users/candidate_profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def view_profile(request, username=None):
    if username:
        user = get_object_or_404(CustomUser, username=username)
        profile = get_object_or_404(Profile, user=user)
    else:
        profile = get_object_or_404(Profile, user=request.user)

    # Optionally, you can add more logic here if needed, for example:
    # if request.user != profile.user and not request.user.is_recruiter:
    #     raise PermissionDenied("You are not allowed to view this profile.")
    
    return render(request, 'users/view_profile.html', {'profile': profile})


def my_profile(request):
    if request.user.is_authenticated:
        return redirect('users:view_profile_by_username', username=request.user.username)
    else:
        return redirect('sitevisitor:login')


@login_required
def candidate_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    saved_jobs = request.user.saved_jobs.all()  # Assumes a SavedJob model with a relation to the user.
    applications = request.user.applications.all()  # Assumes an Application model with a relation to the user.
    notifications = request.user.notifications.filter(is_read=False)
    return render(request, 'users/candidate_dashboard.html', {
        'profile': profile,
        'saved_jobs': saved_jobs,
        'applications': applications,
        'notifications': notifications,
    })


@login_required
def upload_documents(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.cleaned_data['resume']
            additional_documents = form.cleaned_data.get('additional_documents')
            # Save documents to the storage
            messages.success(request, "Documents uploaded successfully!")
            return redirect('users/candidate_dashboard')
    else:
        form = DocumentUploadForm()
    return render(request, 'users/upload_documents.html', {'form': form})


FREE_VISIBLE_TYPES = {"Contract", "Freelance", "Commission"}
PAID_ONLY_TYPES = {"Part Time", "Full Time"}

def job_list(request):
    search_query = request.GET.get('search', '')
    job_type = request.GET.get('job_type', '')
    job_region = request.GET.get('job_region', '')

    qs = Job.objects.filter(status="active")
    if search_query:
        qs = qs.filter(job_title__icontains=search_query)
    if job_type:
        qs = qs.filter(job_type=job_type)
    if job_region:
        qs = qs.filter(job_region=job_region)

    paginator = Paginator(qs.order_by("-posted_at"), 9)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)

    return render(request, 'users/job_list.html', {
        'jobs': jobs,
        'FREE_VISIBLE_TYPES': FREE_VISIBLE_TYPES,
        'PAID_ONLY_TYPES': PAID_ONLY_TYPES,
    })


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, status="active")

    is_premium = False
    if request.user.is_authenticated:
        is_premium = request.user.check_premium_status()

    # Gatekeeping logic
    limited_view = (job.job_type in PAID_ONLY_TYPES) and (not is_premium)
    requires_upgrade = (job.job_type in PAID_ONLY_TYPES) and (not is_premium)

    return render(request, 'users/job_detail.html', {
        'job': job,
        'limited_view': limited_view,
        'requires_upgrade': requires_upgrade,
        'is_premium': is_premium,
        'FREE_VISIBLE_TYPES': FREE_VISIBLE_TYPES,
        'PAID_ONLY_TYPES': PAID_ONLY_TYPES,
    })



@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, status="active")

    # Gate: free users cannot apply for paid-only jobs
    if (job.job_type in PAID_ONLY_TYPES) and (not request.user.check_premium_status()):
        messages.warning(request, "Upgrade to premium to apply for this job.")
        return redirect("payments:upgrade")

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.applicant = request.user
            app.save()
            messages.success(request, "Application submitted successfully.")
            return redirect('users:job_detail', job_id=job.id)
        else:
            messages.error(request, "Please fix the errors and submit again.")
    else:
        form = ApplicationForm()

    return render(request, 'users/job_application.html', {'form': form, 'job': job})






def job_expired(request, job_id):
    return render(request, 'users/job_expired.html')



def job_search(request):
    form = JobSearchForm()
    return render(request, 'users/job_search.html', {'form': form})


def job_search_results(request):
    form = JobSearchForm(request.GET)
    jobs = Job.objects.all()

    if form.is_valid():
        job_title = form.cleaned_data.get('job_title')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')
        salary_min = form.cleaned_data.get('salary_min')
        salary_max = form.cleaned_data.get('salary_max')
        job_type = form.cleaned_data.get('job_type')

        if job_title:
            jobs = jobs.filter(job_title__icontains=job_title)
        if location:
            jobs = jobs.filter(job_location__icontains=location)
        if category:
            jobs = jobs.filter(job_category__icontains=category)  # ⚠️ you need job_category in model
        if salary_min is not None:
            jobs = jobs.filter(salary__gte=salary_min)
        if salary_max is not None:
            jobs = jobs.filter(salary__lte=salary_max)
        if job_type:
            jobs = jobs.filter(job_type=job_type)

    return render(request, 'users/job_search_results.html', {
        'jobs': jobs,
        'form': form
    })





def application_status(request):
    applications = Application.objects.filter(applicant=request.user)
    return render(request, 'users/application_status.html', {'applications': applications})



def candidate_notifications(request):
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification preferences updated successfully.")
            return redirect('users/candidate_notifications')
    else:
        form = NotificationPreferenceForm(instance=preferences)
    return render(request, 'users/candidate_notifications.html', {'form': form})

def candidate_email_preview(request):
    # Example data to simulate an email preview
    email_content = {
        'subject': "Your Application Status Update",
        'body': "Dear Candidate,\n\nYour application status has been updated. Please check your profile for more details.",
    }
    return render(request, 'users/candidate_email_preview.html', {'email_content': email_content})



@login_required
def upload_documents(request):
    try:
        documents = CandidateDocument.objects.get(user=request.user)
    except CandidateDocument.DoesNotExist:
        documents = None

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, instance=documents)
        if form.is_valid():
            document_instance = form.save(commit=False)
            document_instance.user = request.user
            document_instance.save()
            messages.success(request, "Documents uploaded successfully.")
            return redirect('users/upload_documents')
    else:
        form = DocumentUploadForm(instance=documents)

    return render(request, 'users/upload_documents.html', {'form': form, 'documents': documents})

@login_required
def view_resume(request):
    try:
        documents = CandidateDocument.objects.get(user=request.user)
    except CandidateDocument.DoesNotExist:
        documents = None

    return render(request, 'users/view_resume.html', {'documents': documents})




def apply_for_job(request, job_id):
    """
    Handles the job application process.
    """
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user  # Assuming user is authenticated
            application.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('users:job_detail', job_id=job.id)
        else:
            messages.error(request, "There was an error in your application. Please fix the issues and try again.")
    else:
        form = ApplicationForm()

    return render(request, 'users/job_application.html', {
        'form': form,
        'job': job,
    })

def application_list(request):
    """
    View for listing all applications for the logged-in user.
    """
    applications = Application.objects.filter(applicant=request.user)
    return render(request, 'users/application_status.html', {
        'applications': applications,
    })


def view_application(request, id):
    application = get_object_or_404(Application, id=id)
    return render(request, 'users/my_applications.html', {'application': application})

from django.contrib.auth.decorators import login_required

@login_required
def my_applications(request):
    """
    View for candidates to see their applications and statuses.
    """
    applications = request.user.applications.select_related('job')
    return render(request, 'users/my_applications.html', {'applications': applications})


def logout_view(request):
    logout(request)
    return redirect('sitevisitor:home')


