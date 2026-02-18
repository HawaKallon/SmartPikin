from django.core.management.base import BaseCommand
from ai_core.models import ExamConfig

# Default instruction templates
NPSE_OBJ = 'Answer ALL questions. Each question has four options (A, B, C, D). Choose the best answer for each question. You have {time} minutes.'
BECE_OBJ = 'Answer ALL questions. Each question has four options (A, B, C, D). Select the most appropriate answer. You have {time} minutes.'
BECE_THEORY = 'Answer ALL questions clearly and concisely. Show your working where required. You have {time} minutes.'
WASSCE_OBJ = 'Answer ALL questions. Each question has four options (A, B, C, D). There is no penalty for wrong answers. You have {time} minutes.'
WASSCE_THEORY = 'Answer the required number of questions. Show all working clearly. Read each question carefully before answering. You have {time} minutes.'

EXAM_CONFIGS = [
    # ========================================
    # NPSE — Primary 6, objectives only
    # ========================================
    {'exam_type': 'NPSE', 'subject': 'Language Arts', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'NPSE', 'subject': 'Mathematics', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'NPSE', 'subject': 'General Paper', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'NPSE', 'subject': 'Quantitative Aptitude', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'NPSE', 'subject': 'Verbal Aptitude', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},

    # ========================================
    # BECE — JSS 3, objectives papers
    # ========================================
    # Core subjects
    {'exam_type': 'BECE', 'subject': 'English Language', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'Mathematics', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'Integrated Science', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Social Studies', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    # Elective / additional subjects
    {'exam_type': 'BECE', 'subject': 'French', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Arabic', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Agriculture', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Home Economics', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Religious and Moral Education', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Creative Arts', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Business Studies', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'ICT', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Civic Education', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Physical Health Education', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 45},

    # ========================================
    # BECE — JSS 3, theory papers
    # ========================================
    {'exam_type': 'BECE', 'subject': 'English Language', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'Mathematics', 'paper_type': 'theory', 'num_questions': 8, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'Integrated Science', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'Social Studies', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'French', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Arabic', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Agriculture', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'Home Economics', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'Religious and Moral Education', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Creative Arts', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Business Studies', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 60},
    {'exam_type': 'BECE', 'subject': 'ICT', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Civic Education', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 45},
    {'exam_type': 'BECE', 'subject': 'Physical Health Education', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 45},

    # ========================================
    # WASSCE — SS 3, objectives papers
    # ========================================
    # Sciences
    {'exam_type': 'WASSCE', 'subject': 'English Language', 'paper_type': 'objectives', 'num_questions': 80, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Mathematics', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Biology', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 50},
    {'exam_type': 'WASSCE', 'subject': 'Chemistry', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Physics', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Further Mathematics', 'paper_type': 'objectives', 'num_questions': 40, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Agricultural Science', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 50},
    # Arts / Humanities
    {'exam_type': 'WASSCE', 'subject': 'Literature in English', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Government', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'History', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Geography', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Christian Religious Studies', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 50},
    {'exam_type': 'WASSCE', 'subject': 'Islamic Studies', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 50},
    {'exam_type': 'WASSCE', 'subject': 'French', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    # Business / Commercial
    {'exam_type': 'WASSCE', 'subject': 'Economics', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Commerce', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Financial Accounting', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    {'exam_type': 'WASSCE', 'subject': 'Computer Science', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 60},
    # Other
    {'exam_type': 'WASSCE', 'subject': 'Food and Nutrition', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 50},
    {'exam_type': 'WASSCE', 'subject': 'Civic Education', 'paper_type': 'objectives', 'num_questions': 50, 'time_minutes': 50},

    # ========================================
    # WASSCE — SS 3, theory papers
    # ========================================
    {'exam_type': 'WASSCE', 'subject': 'English Language', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Mathematics', 'paper_type': 'theory', 'num_questions': 10, 'time_minutes': 150},
    {'exam_type': 'WASSCE', 'subject': 'Biology', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Chemistry', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 120},
    {'exam_type': 'WASSCE', 'subject': 'Physics', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 120},
    {'exam_type': 'WASSCE', 'subject': 'Further Mathematics', 'paper_type': 'theory', 'num_questions': 8, 'time_minutes': 150},
    {'exam_type': 'WASSCE', 'subject': 'Agricultural Science', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Literature in English', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Government', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'History', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Geography', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Christian Religious Studies', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Islamic Studies', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'French', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Economics', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Commerce', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Financial Accounting', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 120},
    {'exam_type': 'WASSCE', 'subject': 'Computer Science', 'paper_type': 'theory', 'num_questions': 6, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Food and Nutrition', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 90},
    {'exam_type': 'WASSCE', 'subject': 'Civic Education', 'paper_type': 'theory', 'num_questions': 5, 'time_minutes': 90},
]


def _get_instructions(config):
    """Generate instructions based on exam type and paper type."""
    t = config['time_minutes']
    exam = config['exam_type']
    paper = config['paper_type']
    if exam == 'NPSE':
        return NPSE_OBJ.format(time=t)
    if paper == 'objectives':
        return (BECE_OBJ if exam == 'BECE' else WASSCE_OBJ).format(time=t)
    return (BECE_THEORY if exam == 'BECE' else WASSCE_THEORY).format(time=t)


class Command(BaseCommand):
    help = 'Seed ExamConfig with NPSE, BECE, and WASSCE exam configurations'

    def handle(self, *args, **options):
        created_count = 0
        for config in EXAM_CONFIGS:
            _, created = ExamConfig.objects.get_or_create(
                exam_type=config['exam_type'],
                subject=config['subject'],
                paper_type=config['paper_type'],
                defaults={
                    'num_questions': config['num_questions'],
                    'time_minutes': config['time_minutes'],
                    'instructions': _get_instructions(config),
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_count} new exam configs ({ExamConfig.objects.count()} total)'
        ))
