from ai_core.models import ReportCard
from ai_core.forms import StepOneForm, StepTwoForm, StepThreeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from django.urls import reverse


class ReportCardWizardView(LoginRequiredMixin, SessionWizardView):
    form_list = [StepOneForm, StepTwoForm, StepThreeForm]
    template_name = "ai_core/report_card_wizard.html"

    def done(self, form_list, **kwargs):
        step_one_data = form_list[0].cleaned_data
        step_two_data = form_list[1].cleaned_data
        step_three_data = form_list[2].cleaned_data

        # Save the report card
        report_card = ReportCard.objects.create(
            user=self.request.user,
            student_name=step_one_data['student_name'],
            class_level=step_one_data['class_level'],
            attendance_percentage=step_one_data['attendance_percentage'],
            teacher_comments=step_one_data.get('teacher_comments', ''),
            subjects=step_two_data['subjects'],  # This is now validated JSON
            payment_status="Completed" if step_three_data['payment_confirmation'] else "Pending"
        )

        return redirect(reverse('ai_core:report_card_wizard', kwargs={'pk': report_card.pk}))
