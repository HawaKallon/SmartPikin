from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, School  # Import the CustomUser model


# Base class to avoid repetition
class BaseUserForm(forms.ModelForm):
    """Base class for user forms to handle common fields."""
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Enter First Name'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']


# Form for registering an Admin
class AdminRegistrationForm(UserCreationForm):
    """Form for registering an admin user."""

    class Meta(BaseUserForm.Meta):
        model = CustomUser
        fields = BaseUserForm.Meta.fields + ['password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
        return user


# Form for registering a Teacher
class TeacherRegistrationForm(UserCreationForm):
    """Form for registering a teacher."""

    class Meta(BaseUserForm.Meta):
        model = CustomUser
        fields = BaseUserForm.Meta.fields + ['password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
        return user


# Form for registering a Student
class StudentRegistrationForm(UserCreationForm):
    """Form for registering a student."""
    guardian_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Guardian Name'})
    )

    class Meta(BaseUserForm.Meta):
        model = CustomUser
        fields = BaseUserForm.Meta.fields + ['password1', 'password2', 'guardian_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user


# Form for registering a Guardian
class GuardianRegistrationForm(UserCreationForm):
    """Form for registering a guardian."""
    contact_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Contact Number'})
    )

    class Meta(BaseUserForm.Meta):
        model = CustomUser
        fields = BaseUserForm.Meta.fields + ['password1', 'password2', 'contact_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'guardian'
        if commit:
            user.save()
        return user


# Custom login form
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class CustomLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter Email', 'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'form-control'}))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user = authenticate(username=email, password=password)
            if self.user is None:
                raise forms.ValidationError(_("Invalid email or password."))
            if not self.user.is_active:
                raise forms.ValidationError(_("User account is disabled."))
        return self.cleaned_data

    def get_user(self):
        return self.user

    def get_user(self):
        return getattr(self, 'user', None)


from django import forms
from .models import TeacherProfile, StudentProfile, GuardianProfile, TutorProfile


class TeacherProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['school', 'favorite_subjects', 'years_of_experience', 'certifications', 'bio', 'teacher_status',
                  'government_pin_code', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['school', 'grade', 'date_of_birth', 'guardian', 'profile_image']
        widgets = {
            'date_of_birth': forms.SelectDateWidget(years=range(2000, 2024)),  # Adjust the year range as needed
        }


class GuardianProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = GuardianProfile
        fields = ['relationship_to_student', 'phone_number', 'profile_image']


class TutorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = ['subjects_expert_in', 'experience_years', 'hourly_rate', 'bio', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


from django import forms
from ai_core.models import ReportCardImage


class ReportCardForm(forms.ModelForm):
    class Meta:
        model = ReportCardImage
        fields = ['student_name', 'image']
