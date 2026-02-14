import json

from django import forms

from core.models import ClassLevel


class StepOneForm(forms.Form):
    student_name = forms.CharField(
        max_length=150,
        label="Student Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter the student's full name"}),
    )
    class_level = forms.ChoiceField(
        choices=ClassLevel.choices,
        label="Class Level",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    attendance_percentage = forms.FloatField(
        label="Attendance Percentage",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g., 95.5"}),
    )
    teacher_comments = forms.CharField(
        label="Teacher Comments",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional comments from the teacher"}),
    )




class StepTwoForm(forms.Form):
    subjects = forms.CharField(
        widget=forms.HiddenInput(),
        label="Subjects and Grades",
    )

    def clean_subjects(self):
        data = self.cleaned_data['subjects']
        try:
            subjects = json.loads(data)  # Parse JSON string to Python dict
            if not isinstance(subjects, dict):
                raise forms.ValidationError("Invalid data format. Expected a dictionary of subjects and grades.")
            for subject, grade in subjects.items():
                if not isinstance(subject, str) or not subject.strip():
                    raise forms.ValidationError("Each subject must be a non-empty string.")
                if not isinstance(grade, (int, float)):
                    raise forms.ValidationError("Each grade must be a number.")
            return subjects
        except (ValueError, TypeError):
            raise forms.ValidationError("Invalid JSON data for subjects.")



class StepThreeForm(forms.Form):
    payment_confirmation = forms.BooleanField(
        label="I confirm payment for this analysis.",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
