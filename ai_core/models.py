from django.conf import settings
from django.db import models
from core.models import ClassLevel
from django.utils.translation import gettext_lazy as _


# Create your models here.
class DocumentChunk(models.Model):
    document_type = models.CharField(max_length=100)  # e.g., "WAEC Syllabus", "History Textbook"
    chunk_text = models.TextField()  # The extracted text chunk
    embedding = models.BinaryField()  # Serialized embedding vector
    metadata = models.JSONField()  # Additional metadata like topic, page number


class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', _('Pending')
    COMPLETED = 'Completed', _('Completed')
    EXPIRED = 'Expired', _('Expired')


class ReportCard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_cards'
    )
    student_name = models.CharField(max_length=150)
    class_level = models.CharField(max_length=20, choices=ClassLevel.choices)
    subjects = models.JSONField()  # e.g., {"Math": 90, "English": 85}
    attendance_percentage = models.FloatField()
    teacher_comments = models.TextField(blank=True, null=True)
    payment_status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    generated_analysis = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.class_level}"

    def is_analysis_available(self):
        return self.payment_status == PaymentStatus.COMPLETED


class ReportCardImage(models.Model):
    student_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='report_cards/')
    upload_date = models.DateTimeField(auto_now_add=True)


class ResourceType(models.TextChoices):
    MULTIPLE_CHOICE = "Multiple Choice Questions", "Multiple Choice Questions"
    ESSAY = "Essay", "Essay"
    SCENARIO_BASED = "Scenario Based", "Scenario Based"
    CLASS_EXERCISE = "Class Exercise", "Class Exercise"
    HOMEWORK = "Homework", "Homework"
    INTERACTIVE_SESSION = "Interactive Session", "Interactive Session"
    EXPERIMENT = "Experiment", "Experiment"
    PRACTICAL = "Practical", "Practical"


class DifficultyLevel(models.TextChoices):
    SIMPLE = "Simple", "Simple"
    AVERAGE = "Average", "Average"
    HARD = "Hard", "Hard"
    LOGICAL = "Logical", "Logical"


class SubjectChoices(models.TextChoices):
    ENGLISH = "English", "English"
    MATHEMATICS = "Mathematics", "Mathematics"


class ResourceModel(models.Model):
    class_level = models.CharField(max_length=10, choices=ClassLevel.choices)
    topic = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=30, choices=ResourceType.choices)
    difficulty_level = models.CharField(max_length=20, choices=DifficultyLevel.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    number_of_questions = models.PositiveIntegerField(default=5)
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)  # Add this field
    subject = models.CharField(max_length=20, choices=SubjectChoices.choices,
                               default=SubjectChoices.ENGLISH)  # Added subject field

    def __str__(self):
        return f"{self.class_level} - {self.topic} ({self.resource_type} - {self.difficulty_level})"


class QuizSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_sessions')
    topic = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=ClassLevel.choices)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=5)
    quiz_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic} ({self.score}/{self.total_questions})"


class FlashcardSet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcard_sets')
    topic = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=ClassLevel.choices)
    cards = models.JSONField()
    total_cards = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic} ({self.total_cards} cards)"


# === Exam Simulator ===

class ExamType(models.TextChoices):
    NPSE = 'NPSE', 'NPSE'
    BECE = 'BECE', 'BECE'
    WASSCE = 'WASSCE', 'WASSCE'


class PaperType(models.TextChoices):
    OBJECTIVES = 'objectives', 'Objectives (MCQ)'
    THEORY = 'theory', 'Theory'


class ExamConfig(models.Model):
    exam_type = models.CharField(max_length=10, choices=ExamType.choices)
    subject = models.CharField(max_length=100)
    paper_type = models.CharField(max_length=15, choices=PaperType.choices)
    num_questions = models.PositiveIntegerField()
    time_minutes = models.PositiveIntegerField()
    instructions = models.TextField(blank=True)

    class Meta:
        unique_together = ('exam_type', 'subject', 'paper_type')

    def __str__(self):
        return f"{self.exam_type} - {self.subject} ({self.paper_type})"


class ExamSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_sessions')
    exam_config = models.ForeignKey(ExamConfig, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    questions_data = models.JSONField()
    answers_data = models.JSONField(default=list)
    score = models.PositiveIntegerField(null=True, blank=True)
    total_marks = models.PositiveIntegerField(null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)
    grade = models.CharField(max_length=5, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    topic_breakdown = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.exam_config} ({self.percentage or 0}%)"
