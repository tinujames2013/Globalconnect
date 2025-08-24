from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # ---------------- AUTH ----------------
    path("logout/", views.logout_view, name="logout"),

    # ---------------- DASHBOARD ----------------
    path("dashboard/", views.candidate_dashboard, name="candidate_dashboard"),

    # ---------------- PROFILES ----------------
    path("profile/create/", views.create_profile, name="create_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.view_profile, name="view_profile_by_username"),
    path("profile/", views.view_profile, name="view_profile"),
    path("profile/edit/candidate/", views.edit_candidate_profile, name="edit_candidate_profile"),
    path("my-profile/", views.my_profile, name="my_profile"),

    # ---------------- RESUMES ----------------
    path("resumes/", views.ResumeListView.as_view(), name="list"),
    path("resume/create/", views.resume_create, name="create"),
    path("resume/<int:pk>/edit/", views.resume_edit, name="edit"),
    path("resume/<int:pk>/delete/", views.resume_delete, name="delete"),
    path("resume/<int:pk>/preview/", views.preview_resume, name="preview"),
    path("resume/<int:pk>/pdf/", views.resume_pdf, name="pdf"),
    path("resume/<int:pk>/template/<str:key>/", views.change_template, name="change_template"),

    # ---------------- DOCUMENTS ----------------
    path("documents/upload/", views.upload_documents, name="upload_documents"),
    path("resume/view/", views.view_resume, name="view_resume"),

    # ---------------- JOBS ----------------
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/search/", views.job_search, name="job_search"),
    path("jobs/search/results/", views.job_search_results, name="job_search_results"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<int:job_id>/apply/", views.apply_for_job, name="apply_for_job"),
    path("jobs/<int:job_id>/expired/", views.job_expired, name="job_expired"),

    # ---------------- APPLICATIONS ----------------
    path("applications/", views.application_list, name="application_list"),
    path("applications/<int:id>/", views.view_application, name="view_application"),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("application-status/", views.application_status, name="application_status"),

    # ---------------- NOTIFICATIONS ----------------
    path("notifications/", views.candidate_notifications, name="candidate_notifications"),
    path("notifications/email-preview/", views.candidate_email_preview, name="candidate_email_preview"),

    # ---------------- HOME ----------------
    path('home/', views.home, name='users_home'),


]
