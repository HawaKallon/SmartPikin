from django.urls import path
from django.views.generic import TemplateView

from core.views.application import ApplicationFormWizard, download_application
from core.views.home import HomePage, TeacherListView, TeacherProfileDetailView, SchoolListView, SchoolDetailView
from core.views.tutor import TutorListView

app_name = 'core'

urlpatterns = [
    path('', HomePage.as_view(), name='home_page'),
    path('teachers/', TeacherListView.as_view(), name='teacher-list'),
    path('tutors/', TutorListView.as_view(), name='tutor-list'),

    path("teacher/<int:pk>/", TeacherProfileDetailView.as_view(), name="teacher_profile_detail"),
    path('schools/', SchoolListView.as_view(), name='school-list'),
    path("school/<int:pk>/", SchoolDetailView.as_view(), name="school_profile_detail"),
    path(
        'school/<int:pk>/apply/',
        ApplicationFormWizard.as_view(),
        name='application_form_wizard'
    ),
    path('application/<int:application_id>/download/', download_application, name='download_application'),
    path('about/', TemplateView.as_view(template_name='core/marketing.html'), name='marketing'),
]
