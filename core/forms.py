# forms.py
from django import forms
from django.forms import TextInput, Select, Textarea, FileInput, DateInput
from .models import Application


class BasicInfoForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['first_name', 'last_name', 'date_of_birth']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'date_of_birth': DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get user from the view
        school = kwargs.pop('school', None)  # Get school from the view (optional)
        super().__init__(*args, **kwargs)

        if user:
            self.instance.user = user  # Set the pre-filled user
        if school:
            self.instance.school = school  # Set the pre-filled school


from django import forms
from .models import Application


class SchoolLevelForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['school_level', 'class_level']
        widgets = {
            'school_level': forms.Select(attrs={'class': 'form-select'}),
            'class_level': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        # Get user and school from kwargs if they are passed in
        self.user = kwargs.pop('user', None)  # Get user if passed
        self.school = kwargs.pop('school', None)  # Get school if passed

        # Call the parent constructor with the remaining arguments
        super().__init__(*args, **kwargs)

        # Set the user and school fields if they were passed
        if self.user:
            self.instance.user = self.user  # Set the user
        if self.school:
            self.instance.school = self.school  # Set the school


from django import forms
from .models import Application
from django.forms import TextInput, Textarea


class ParentContactForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['parent_contact', 'address']
        widgets = {
            'parent_contact': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter parent/guardian contact'}),
            'address': Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Get user and school from kwargs if they are passed
        self.user = kwargs.pop('user', None)  # Get user if passed
        self.school = kwargs.pop('school', None)  # Get school if passed

        # Call the parent constructor with the remaining arguments
        super().__init__(*args, **kwargs)

        # Set the user and school fields if they were passed
        if self.user:
            self.instance.user = self.user  # Set the user
        if self.school:
            self.instance.school = self.school  # Set the school


class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['previous_school', 'previous_result', 'applicant_image']
        widgets = {
            'previous_school': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter previous school (optional)'}),
            'previous_result': FileInput(attrs={'class': 'form-control'}),
            'applicant_image': FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Call the parent constructor
        # No need to pre-fill school here, as it's not required for this form

from django import forms
from django.forms import TextInput, FileInput
from .models import Application

class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['previous_school', 'previous_result', 'applicant_image']
        widgets = {
            'previous_school': TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter previous school (optional)'}),
            'previous_result': FileInput(attrs={'class': 'form-control'}),
            'applicant_image': FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        # We handle user and school kwargs if needed, but we don't need to pass 'school' here.
        self.user = kwargs.pop('user', None)  # Get user if passed
        super().__init__(*args, **kwargs)  # Call the parent constructor

        # Set the user field if it's passed
        if self.user:
            self.instance.user = self.user  # Set the user on the application instance
