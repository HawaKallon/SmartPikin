import os
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView
from core.models import LessonPlan
from groq import Groq
import markdown2
import pdfkit
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Configure Groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)


class MathLessonNoteGeneratorView(LoginRequiredMixin, View):
    template_name = 'ai_core/math_lesson_note_generator.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Check if this is a follow-up request
        follow_up_request = request.POST.get('follow_up_request')
        lesson_note_id = request.POST.get('lesson_note_id')

        if follow_up_request and lesson_note_id:
            # Generate follow-up content based on existing lesson note
            lesson_note = get_object_or_404(LessonPlan, id=lesson_note_id, user=request.user)
            follow_up_content = self.generate_follow_up_content(
                lesson_note.topic, lesson_note.level, follow_up_request
            )
            follow_up_content_html = markdown2.markdown(follow_up_content, extras=["tables"])

            # Combine the original lesson note and the follow-up content
            combined_content = lesson_note.content + follow_up_content_html

            # Update the lesson note in the database with combined content
            lesson_note.content = combined_content
            lesson_note.save()

            return render(request, self.template_name, {
                'topic': lesson_note.topic,
                'level': lesson_note.level,
                'lesson_note': lesson_note.content,
                'follow_up_content': follow_up_content_html,
                'lesson_note_id': lesson_note.id,
            })
        else:
            # Original lesson note generation process
            topic = request.POST.get('topic')
            level = request.POST.get('level')
            if not topic:
                messages.error(request, "Please enter a topic.")
                return render(request, self.template_name)

            # Generate the initial lesson note
            lesson_note = self.generate_math_lesson_note(topic, level)
            if lesson_note:
                lesson_note_html = markdown2.markdown(lesson_note, extras=["tables"])

                # Save the lesson note to the database
                saved_note = LessonPlan.objects.create(
                    user=request.user,
                    topic=topic,
                    level=level,
                    content=lesson_note_html
                )
                return render(request, self.template_name, {
                    'topic': topic,
                    'level': level,
                    'lesson_note': lesson_note_html,
                    'lesson_note_id': saved_note.id
                })
            else:
                messages.error(request, "Failed to generate lesson note. Please try again.")
                return render(request, self.template_name)

    def generate_math_lesson_note(self, topic, level):
        """Generate a comprehensive mathematics lesson note using the Groq API."""
        try:
            prompt = (
                f"Create a detailed and practical lesson note for teaching the topic '{topic}' in mathematics "
                f"for {level} students. The note should include the following structured sections:\n\n"

                f"1. **Theory**: Provide an in-depth explanation of the theoretical foundation of '{topic}'.\n"

                f"2. **Formula**: List the key formulas involved, including a step-by-step derivation to build understanding.\n"

                f"3. **Visual Representation**: Provide graphical explanations where applicable to help students visualize the concepts. "
                f"Use flowcharts, graphs, or any visual model that can clarify abstract ideas. For example, illustrate concepts such as relationships between variables, geometric shapes, function graphs, or process flows. "
                f"These visuals should be created using Mermaid syntax or other diagramming tools that support interactive diagrams or charts that clearly communicate the relationships and logic behind the topic.\n"

                f"4. **Real-World Applications**: Describe practical applications of '{topic}', especially within an African context, "
                f"highlighting how it can be applied to solve problems in fields like agriculture, economics, technology, and local industries in Sierra Leone.\n"

                f"5. **Example Problems**: Include example problems ranging from basic to advanced difficulty, with step-by-step solutions for each problem.\n"

                f"6. **Class Exercises**: Provide a set of exercises for students to practice in class, covering different levels of complexity.\n"

                f"7. **Homework Assignments**: List several homework assignments that reinforce the key concepts, with a mix of problem types.\n"
                f"9. **Follow-Up Questions and Recommendations**: Conclude with a section that suggests potential follow-up questions for students to extend their thinking and deepen their knowledge. Provide recommendations for additional resources, such as articles, videos, or online tools that could further reinforce their understanding of '{topic}'.\n\n"

                f"Ensure the lesson note is comprehensive, accessible, culturally relevant, and tailored to the educational context in Sierra Leone. \n"
                f"The content should actively promote critical thinking, problem-solving, and practical understanding, aligning with the EduBridge mission to connect theory with real-life applications.\n\n"

                f"Ensure the lesson note is comprehensive, accessible, culturally relevant, and suitable for the educational context in Sierra Leone. "
                f"The content should encourage critical thinking and practical understanding, following the EduBridge mission to connect theory with real-life applications."
            )

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return None

    def generate_follow_up_content(self, topic, level, follow_up_request):
        """Generate additional content based on a follow-up request."""
        try:
            prompt = (
                f"Based on the topic '{topic}' for {level} students, provide additional information as follows:\n"
                f"{follow_up_request}\n\n"
                f"Ensure the response is educational, relevant, and tailored for students in Sierra Leone."
            )
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating follow-up content: {e}")
            return None




import datetime


@login_required
def download_math_lesson(request, id):
    """Generate and download the lesson note as a PDF with robust options."""
    lesson_note = get_object_or_404(LessonPlan, id=id, user=request.user)
    lesson_note_html = lesson_note.content

    if not lesson_note_html:
        messages.error(request, "No lesson note available to download.")
        return redirect('ai_core:math_lesson_note_generator')

    # PDF options for improved robustness and quality
    options = {
        "enable-local-file-access": None,
        "page-size": "A4",
        "margin-top": "1in",
        "margin-right": "1in",
        "margin-bottom": "1in",
        "margin-left": "1in",
        "encoding": "UTF-8",
        "dpi": 300,  # High DPI for better image and text quality
        "zoom": "1.2",
        "no-outline": None,
        "footer-right": "[page] of [topage]",  # Page numbering in footer
        "header-left": f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d')}",  # Date on header
        "footer-left": "Math Lesson Plan",  # Document title in footer
        "footer-font-size": "10",
        "header-font-size": "10",
        "print-media-type": None,  # Forces media type to print for improved CSS compatibility
        "minimum-font-size": 12,  # Ensures minimum readable font size
        "disable-smart-shrinking": None,  # Avoids text scaling down too much
    }

    # Optional: Add a watermark or background image if needed (replace path accordingly)
    #options["background"] = "/path/to/watermark-image.png"  # Uncomment if a watermark is desired

    try:
        pdf = pdfkit.from_string(lesson_note_html, False, options=options)
    except IOError:
        messages.error(request, "Error generating PDF. Please try again later.")
        return redirect('ai_core:math_lesson_note_generator')

    # Create the HTTP response with PDF content
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="math_lesson_note.pdf"'

    return response


class MathLessonNoteListView(LoginRequiredMixin, ListView):
    model = LessonPlan
    template_name = 'ai_core/math_lesson_note_list.html'
    context_object_name = 'lesson_notes'

    def get_queryset(self):
        return LessonPlan.objects.filter(user=self.request.user).order_by('-created_at')
