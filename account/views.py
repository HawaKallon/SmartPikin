from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView, RedirectView
from .forms import TeacherRegistrationForm, StudentRegistrationForm, GuardianRegistrationForm, CustomLoginForm
from .models import CustomUser


class BaseRegisterView(CreateView):
    """Base view for user registration that handles common functionality."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Registration successful. Welcome, {form.cleaned_data['first_name']}!")
        return response


class TeacherRegisterView(BaseRegisterView):
    model = CustomUser
    form_class = TeacherRegistrationForm
    template_name = "account/resgistration/teacher/register.html"
    success_url = reverse_lazy('core:home_page')

    def form_valid(self, form):
        form.instance.role = 'teacher'
        return super().form_valid(form)


class StudentRegisterView(BaseRegisterView):
    model = CustomUser
    form_class = StudentRegistrationForm
    template_name = "account/resgistration/student/register.html"
    success_url = reverse_lazy('core:home_page')

    def form_valid(self, form):
        form.instance.role = 'student'
        return super().form_valid(form)


class GuardianRegisterView(BaseRegisterView):
    model = CustomUser
    form_class = GuardianRegistrationForm
    template_name = "account/resgistration/guardian/register.html"
    success_url = reverse_lazy('core:home_page')

    def form_valid(self, form):
        form.instance.role = 'guardian'
        return super().form_valid(form)


class CustomLoginView(FormView):
    form_class = CustomLoginForm
    template_name = "account/login.html"
    success_url = reverse_lazy('core:home_page')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"Welcome back, {user.first_name}!")
        return super().form_valid(form)


class CustomLogoutView(RedirectView):
    url = reverse_lazy('account:login')

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been logged out.")
        return super().get(request, *args, **kwargs)


from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import TeacherProfile, StudentProfile, GuardianProfile, TutorProfile
from .forms import TeacherProfileUpdateForm, StudentProfileUpdateForm, GuardianProfileUpdateForm, TutorProfileUpdateForm


class TeacherProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = TeacherProfile
    form_class = TeacherProfileUpdateForm
    template_name = 'account/profiles/teacher_profile_update.html'
    success_url = reverse_lazy('core:home_page')

    def get_object(self):
        user = self.request.user
        # Check if the user has a TeacherProfile; if not, create one
        teacher_profile, created = TeacherProfile.objects.get_or_create(user=user)
        if created:
            messages.info(self.request, "A new Teacher Profile has been created for you. Please update your information.")
        return teacher_profile

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)
class StudentProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileUpdateForm
    template_name = 'account/profiles/student_profile_update.html'
    success_url = reverse_lazy('core:home_page')

    def get_object(self):
        return self.request.user.studentprofile

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)


class GuardianProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = GuardianProfile
    form_class = GuardianProfileUpdateForm
    template_name = 'account/profiles/guardian_profile_update.html'
    success_url = reverse_lazy('core:home_page')

    def get_object(self):
        return self.request.user.guardianprofile

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)


class TutorProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = TutorProfile
    form_class = TutorProfileUpdateForm
    template_name = 'account/profiles/tutor_profile_update.html'
    success_url = reverse_lazy('core:home_page')

    def get_object(self):
        return self.request.user.tutorprofile

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)
