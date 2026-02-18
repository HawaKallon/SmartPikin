import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST
from groq import Groq

from ai_core.models import ExamConfig, ExamSession, ExamType

logger = logging.getLogger(__name__)
groq_client = Groq(api_key=settings.GROQ_API_KEY)

WAEC_GRADES = [
    (75, 'A1'), (70, 'B2'), (65, 'B3'), (60, 'C4'),
    (55, 'C5'), (50, 'C6'), (45, 'D7'), (40, 'E8'), (0, 'F9'),
]


def get_waec_grade(percentage):
    for threshold, grade in WAEC_GRADES:
        if percentage >= threshold:
            return grade
    return 'F9'


class ExamSimulatorView(LoginRequiredMixin, View):
    template_name = 'ai_core/exam_simulator.html'

    def get(self, request):
        configs = list(
            ExamConfig.objects.all()
            .values('id', 'exam_type', 'subject', 'paper_type', 'num_questions', 'time_minutes', 'instructions')
            .order_by('exam_type', 'subject', 'paper_type')
        )
        return render(request, self.template_name, {
            'exam_types': ExamType.choices,
            'configs': configs,
        })

    def post(self, request):
        config_id = request.POST.get('config_id')
        if not config_id:
            messages.error(request, "Please select an exam and subject.")
            return self.get(request)

        config = get_object_or_404(ExamConfig, id=config_id)

        if config.paper_type == 'theory':
            exam_questions = self.generate_theory_questions(config)
        else:
            exam_questions = self.generate_exam_questions(config)

        if exam_questions is None:
            messages.error(request, "Failed to generate exam questions. Please try again.")
            return self.get(request)

        session = ExamSession.objects.create(
            user=request.user,
            exam_config=config,
            questions_data=exam_questions,
            answers_data=[''] * len(exam_questions) if config.paper_type == 'theory' else [-1] * len(exam_questions),
            total_marks=len(exam_questions),
        )

        exam_meta = {
            'session_id': session.id,
            'exam_type': config.exam_type,
            'subject': config.subject,
            'paper_type': config.paper_type,
            'num_questions': config.num_questions,
            'time_minutes': config.time_minutes,
            'instructions': config.instructions,
        }

        configs = list(
            ExamConfig.objects.all()
            .values('id', 'exam_type', 'subject', 'paper_type', 'num_questions', 'time_minutes', 'instructions')
            .order_by('exam_type', 'subject', 'paper_type')
        )

        return render(request, self.template_name, {
            'exam_types': ExamType.choices,
            'configs': configs,
            'exam_data': exam_questions,
            'exam_meta': exam_meta,
        })

    def generate_exam_questions(self, config):
        """Generate MCQ questions for objectives paper."""
        prompt = (
            f"You are generating {config.exam_type} {config.subject} exam questions for Sierra Leonean students.\n"
            f"Generate exactly {config.num_questions} multiple choice questions that match the real "
            f"{config.exam_type} exam format, difficulty, and curriculum standards.\n\n"
            f"Return ONLY valid JSON (no markdown, no explanation, no code fences) in this exact format:\n"
            f'[{{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], '
            f'"correct": 0, "topic": "short topic name", "explanation": "brief explanation"}}]\n\n'
            f"Rules:\n"
            f'- "correct" is the zero-based index (0-3) of the correct option\n'
            f'- "topic" is the curriculum topic area (e.g., "Algebra", "Cell Biology", "Comprehension")\n'
            f"- Questions must match real {config.exam_type} difficulty and syllabus\n"
            f"- Cover diverse topics across the {config.subject} curriculum\n"
            f"- No repeated questions\n"
            f"- Options must be plausible distractors"
        )

        for attempt in range(2):
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=8000,
                )
                content = response.choices[0].message.content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                data = json.loads(content)
                if isinstance(data, list) and len(data) > 0:
                    return data
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Exam question generation attempt {attempt + 1} failed: {e}")
                continue
        return None

    def generate_theory_questions(self, config):
        """Generate theory/essay questions."""
        prompt = (
            f"You are generating {config.exam_type} {config.subject} theory exam questions for Sierra Leonean students.\n"
            f"Generate exactly {config.num_questions} theory/essay questions that match the real "
            f"{config.exam_type} exam format, difficulty, and curriculum standards.\n\n"
            f"Return ONLY valid JSON (no markdown, no explanation, no code fences) in this exact format:\n"
            f'[{{"question": "...", "topic": "short topic name", "marks": 10, '
            f'"marking_guide": "key points the answer should cover"}}]\n\n'
            f"Rules:\n"
            f'- "marks" is the mark allocation for each question (typically 10-25 marks)\n'
            f'- "topic" is the curriculum topic area\n'
            f'- "marking_guide" lists the key points expected in a correct answer\n'
            f"- Questions must match real {config.exam_type} theory paper difficulty\n"
            f"- Include a mix of short-answer and essay-type questions\n"
            f"- Some questions may have sub-parts (a, b, c)\n"
            f"- Cover diverse topics across the {config.subject} curriculum"
        )

        for attempt in range(2):
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=4000,
                )
                content = response.choices[0].message.content.strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                data = json.loads(content)
                if isinstance(data, list) and len(data) > 0:
                    return data
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Theory question generation attempt {attempt + 1} failed: {e}")
                continue
        return None


@login_required
@require_POST
def submit_exam(request):
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        answers = data.get('answers', [])

        session = get_object_or_404(ExamSession, id=session_id, user=request.user)

        if session.completed_at:
            return JsonResponse({'status': 'error', 'message': 'Exam already submitted'}, status=400)

        config = session.exam_config
        questions = session.questions_data

        if config.paper_type == 'theory':
            return _grade_theory(session, questions, answers, config)
        else:
            return _grade_objectives(session, questions, answers, config)

    except Exception as e:
        logger.error(f"Error submitting exam: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def _grade_objectives(session, questions, answers, config):
    """Grade an objectives (MCQ) exam."""
    score = 0
    topic_breakdown = {}
    for i, q in enumerate(questions):
        topic = q.get('topic', 'General')
        if topic not in topic_breakdown:
            topic_breakdown[topic] = {'correct': 0, 'total': 0}
        topic_breakdown[topic]['total'] += 1

        answer = answers[i] if i < len(answers) else -1
        if answer == q.get('correct', -1):
            score += 1
            topic_breakdown[topic]['correct'] += 1

    total = len(questions)
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    grade = get_waec_grade(percentage)

    feedback = generate_feedback(config, score, total, percentage, topic_breakdown)

    session.answers_data = answers
    session.score = score
    session.total_marks = total
    session.percentage = percentage
    session.grade = grade
    session.feedback = feedback
    session.topic_breakdown = topic_breakdown
    session.completed_at = timezone.now()
    session.save()

    review = []
    for i, q in enumerate(questions):
        answer = answers[i] if i < len(answers) else -1
        review.append({
            'question': q['question'],
            'options': q['options'],
            'correct': q.get('correct', 0),
            'selected': answer,
            'explanation': q.get('explanation', ''),
            'topic': q.get('topic', 'General'),
        })

    return JsonResponse({
        'status': 'ok',
        'paper_type': 'objectives',
        'score': score,
        'total': total,
        'percentage': percentage,
        'grade': grade,
        'topic_breakdown': topic_breakdown,
        'feedback': feedback,
        'review': review,
    })


def _grade_theory(session, questions, answers, config):
    """Grade a theory exam using AI."""
    total_marks = sum(q.get('marks', 10) for q in questions)
    total_earned = 0
    topic_breakdown = {}
    graded_answers = []

    for i, q in enumerate(questions):
        student_answer = answers[i] if i < len(answers) else ''
        topic = q.get('topic', 'General')
        marks = q.get('marks', 10)

        if topic not in topic_breakdown:
            topic_breakdown[topic] = {'earned': 0, 'total': 0}
        topic_breakdown[topic]['total'] += marks

        if not student_answer or not student_answer.strip():
            graded_answers.append({
                'question': q['question'],
                'student_answer': '',
                'marks_earned': 0,
                'marks_available': marks,
                'topic': topic,
                'ai_feedback': 'No answer provided.',
            })
            continue

        # AI grading
        grade_result = _ai_grade_answer(config, q, student_answer)
        earned = min(grade_result.get('marks', 0), marks)
        total_earned += earned
        topic_breakdown[topic]['earned'] += earned

        graded_answers.append({
            'question': q['question'],
            'student_answer': student_answer,
            'marks_earned': earned,
            'marks_available': marks,
            'topic': topic,
            'ai_feedback': grade_result.get('feedback', ''),
            'marking_guide': q.get('marking_guide', ''),
        })

    percentage = round((total_earned / total_marks) * 100, 1) if total_marks > 0 else 0
    grade = get_waec_grade(percentage)

    # Convert topic_breakdown to correct/total format for consistency
    topic_summary = {}
    for topic, data in topic_breakdown.items():
        topic_summary[topic] = {
            'correct': data['earned'],
            'total': data['total'],
        }

    feedback = generate_feedback(config, total_earned, total_marks, percentage, topic_summary)

    session.answers_data = answers
    session.score = total_earned
    session.total_marks = total_marks
    session.percentage = percentage
    session.grade = grade
    session.feedback = feedback
    session.topic_breakdown = topic_summary
    session.completed_at = timezone.now()
    session.save()

    return JsonResponse({
        'status': 'ok',
        'paper_type': 'theory',
        'score': total_earned,
        'total': total_marks,
        'percentage': percentage,
        'grade': grade,
        'topic_breakdown': topic_summary,
        'feedback': feedback,
        'review': graded_answers,
    })


def _ai_grade_answer(config, question, student_answer):
    """Use AI to grade a single theory answer."""
    prompt = (
        f"You are grading a {config.exam_type} {config.subject} theory exam answer.\n\n"
        f"Question: {question['question']}\n"
        f"Marks available: {question.get('marks', 10)}\n"
        f"Marking guide: {question.get('marking_guide', 'Grade based on accuracy, relevance, and completeness')}\n\n"
        f"Student's answer:\n{student_answer}\n\n"
        f"Grade this answer. Return ONLY valid JSON (no markdown, no code fences):\n"
        f'{{"marks": <number>, "feedback": "<brief feedback explaining the grade>"}}\n\n'
        f"Rules:\n"
        f"- marks must be between 0 and {question.get('marks', 10)}\n"
        f"- Be fair but strict — match real WAEC marking standards\n"
        f"- Award partial marks for partially correct answers\n"
        f"- feedback should be 1-2 sentences explaining what was good and what was missing"
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error grading theory answer: {e}")
        return {'marks': 0, 'feedback': 'Unable to grade this answer automatically. Please review manually.'}


def generate_feedback(config, score, total, percentage, topic_breakdown):
    weak = [t for t, d in topic_breakdown.items() if d['total'] > 0 and (d['correct'] / d['total']) < 0.5]
    strong = [t for t, d in topic_breakdown.items() if d['total'] > 0 and (d['correct'] / d['total']) >= 0.7]

    breakdown_text = "\n".join(
        f"- {t}: {d['correct']}/{d['total']} correct"
        for t, d in topic_breakdown.items()
    )

    prompt = (
        f"A student just completed a {config.exam_type} {config.subject} exam and scored "
        f"{score}/{total} ({percentage}%). Grade: {get_waec_grade(percentage)}\n\n"
        f"Topic breakdown:\n{breakdown_text}\n\n"
        f"Weak areas (below 50%): {', '.join(weak) if weak else 'None'}\n"
        f"Strong areas (above 70%): {', '.join(strong) if strong else 'None'}\n\n"
        f"Provide brief, encouraging feedback (3-5 sentences):\n"
        f"1. Acknowledge what they did well\n"
        f"2. Identify 2-3 specific topics to focus on\n"
        f"3. Give concrete study tips for their weak areas\n"
        f"4. End with encouragement\n\n"
        f"Keep it concise and student-friendly. No generic advice. No markdown formatting."
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating feedback: {e}")
        return "Great effort on completing this exam! Review the questions you missed and focus on the topics where you scored lowest."


@login_required
def exam_results(request, session_id):
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    if not session.completed_at:
        messages.error(request, "This exam hasn't been submitted yet.")
        return render(request, 'ai_core/exam_simulator.html', {
            'exam_types': ExamType.choices,
            'configs': list(
                ExamConfig.objects.all()
                .values('id', 'exam_type', 'subject', 'paper_type', 'num_questions', 'time_minutes', 'instructions')
                .order_by('exam_type', 'subject', 'paper_type')
            ),
        })

    config = session.exam_config
    review = []
    answers = session.answers_data or []

    if config.paper_type == 'theory':
        for i, q in enumerate(session.questions_data):
            student_answer = answers[i] if i < len(answers) else ''
            review.append({
                'question': q['question'],
                'student_answer': student_answer,
                'marks_earned': q.get('marks', 0),
                'marks_available': q.get('marks', 10),
                'topic': q.get('topic', 'General'),
                'marking_guide': q.get('marking_guide', ''),
            })
    else:
        for i, q in enumerate(session.questions_data):
            answer = answers[i] if i < len(answers) else -1
            review.append({
                'question': q['question'],
                'options': q['options'],
                'correct': q.get('correct', 0),
                'selected': answer,
                'explanation': q.get('explanation', ''),
                'topic': q.get('topic', 'General'),
            })

    return render(request, 'ai_core/exam_results.html', {
        'session': session,
        'config': config,
        'review': review,
    })


@login_required
def exam_history(request):
    sessions = (
        ExamSession.objects.filter(user=request.user, completed_at__isnull=False)
        .select_related('exam_config')
        .order_by('-completed_at')
    )
    return render(request, 'ai_core/exam_history.html', {
        'sessions': sessions,
    })
