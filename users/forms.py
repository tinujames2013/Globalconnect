from django import forms
from adminpanel.models import Profile,Job,Application,NotificationPreference,CandidateDocument, Resume

from django.forms import inlineformset_factory



class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = [
            'title', 'full_name', 'date_of_birth', 'headline', 'summary',
            'email', 'phone', 'location',
            'linkedin', 'github', 'website',
            'photo', 'template_key',
            'experiences', 'educations', 'school', 'college',
            'skills', 'languages', 'awards',
            'extra_info_1', 'extra_info_2', 'extra_info_3',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'experiences': forms.Textarea(attrs={'rows': 4}),
            'educations': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.Textarea(attrs={'rows': 2}),
            'languages': forms.Textarea(attrs={'rows': 2}),
            'awards': forms.Textarea(attrs={'rows': 2}),
            'extra_info_3': forms.Textarea(attrs={'rows': 3}),
        }




class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
        widgets = {
            'resume': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.odt,.xls,.xlsx,.ppt,.pptx',
            }),
            'cover_letter': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.odt,.xls,.xlsx,.ppt,.pptx',
            }),
        }
        labels = {
            'resume': 'Upload Resume',
            'cover_letter': 'Upload Cover Letter (Optional)',
        }
        help_texts = {
            'resume': 'Allowed file types: PDF, DOC, DOCX,  ',
            'cover_letter': 'Allowed file types: PDF, DOC, DOCX,  ',
        }






class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'email', 'mobile', 'company', 'date_of_birth', 'about_me', 'experience', 'skills','profile_picture']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'skills': forms.TextInput(attrs={'placeholder': 'Comma-separated skills, e.g., Python, Django'}),
        }



class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'email', 'mobile', 'date_of_birth', 'about_me', 'experience', 'skills']

class DocumentUploadForm(forms.Form):
    resume = forms.FileField(label="Upload Resume")
    additional_documents = forms.FileField(label="Additional Documents (Optional)", required=False)
from django import forms

class JobSearchForm(forms.Form):
    job_title = forms.CharField(required=False, label="Job Title")
    location = forms.CharField(required=False, label="Location")
    category = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Category'),
            ('IT', 'IT'),
            ('Finance', 'Finance'),
            ('Marketing', 'Marketing'),
        ]
    )
    salary_min = forms.IntegerField(required=False, label="Min Salary")
    salary_max = forms.IntegerField(required=False, label="Max Salary")
    job_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All'),
            ('Full Time', 'Full Time'),
            ('Part Time', 'Part Time'),
            ('premium', 'Premium'),
            ('free', 'Free'),
        ]
    )





class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = ['email_alerts', 'new_job_alerts', 'application_status_updates']

class WithdrawApplicationForm(forms.Form):
    confirm_withdrawal = forms.BooleanField(required=True, label="I confirm I want to withdraw my application.")



class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = CandidateDocument
        fields = ['resume', 'portfolio', 'certifications']
        widgets = {
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'portfolio': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'certifications': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
