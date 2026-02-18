import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_POST
from groq import Groq

from ai_core.models import QuizSession
from core.models import ClassLevel

logger = logging.getLogger(__name__)
groq_client = Groq(api_key=settings.GROQ_API_KEY)


class QuizModeView(LoginRequiredMixin, View):
    template_name = 'ai_core/quiz_mode.html'

    def get(self, request):
        return render(request, self.template_name, {
            'class_levels': ClassLevel.choices,
        })

    def post(self, request):
        topic = request.POST.get('topic', '').strip()
        subject = request.POST.get('subject', '').strip()
        level = request.POST.get('level', '')
        num_questions = int(request.POST.get('num_questions', 5))

        if not topic or not subject:
            messages.error(request, "Please fill in all fields.")
            return render(request, self.template_name, {
                'class_levels': ClassLevel.choices,
            })

        quiz_data = self.generate_quiz(topic, subject, level, num_questions)

        if quiz_data is None:
            messages.error(request, "Failed to generate quiz. Please try again.")
            return render(request, self.template_name, {
                'class_levels': ClassLevel.choices,
            })

        return render(request, self.template_name, {
            'class_levels': ClassLevel.choices,
            'quiz_data': quiz_data,
            'topic': topic,
            'subject': subject,
            'level': level,
            'num_questions': num_questions,
        })

    def generate_quiz(self, topic, subject, level, num_questions):
        prompt = (
            f"Generate exactly {num_questions} multiple choice questions about {topic} "
            f"in {subject} for {level} students in Sierra Leone.\n"
            f"Return ONLY valid JSON (no markdown, no explanation, no code fences) in this exact format:\n"
            f'[{{"question": "...", "options": ["A", "B", "C", "D"], "correct": 0, "explanation": "..."}}]\n'
            f"Where 'correct' is the zero-based index of the correct option (0-3).\n"
            f"Make questions educational and appropriate for the level."
        )

        for attempt in range(2):
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                content = response.choices[0].message.content.strip()
                # Strip markdown code fences if present
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                quiz_data = json.loads(content)
                if isinstance(quiz_data, list) and len(quiz_data) > 0:
                    return quiz_data
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Quiz generation attempt {attempt + 1} failed: {e}")
                continue

        return None


@login_required
@require_POST
def save_quiz_score(request):
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '')
        subject = data.get('subject', '')
        level = data.get('level', '')
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)
        quiz_data = data.get('quiz_data', [])

        QuizSession.objects.create(
            user=request.user,
            topic=topic,
            subject=subject,
            level=level,
            score=score,
            total_questions=total_questions,
            quiz_data=quiz_data,
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error saving quiz score: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
