from django.core.management.base import BaseCommand
from account.models import Subject


class Command(BaseCommand):
    help = 'Create Sierra Leonean academic subjects'

    def handle(self, *args, **options):
        # Academic subjects based on Sierra Leonean curriculum
        dummy_subjects = [
            {"name": "Mathematics", "description": "Basic to advanced mathematical concepts, including algebra, geometry, and calculus."},
            {"name": "Physics", "description": "The study of matter, energy, and the laws governing their interactions."},
            {"name": "Chemistry", "description": "Exploring chemical reactions, atomic structure, and the periodic table."},
            {"name": "Biology", "description": "The study of living organisms, ecosystems, and biological processes."},
            {"name": "English Language", "description": "Mastering the English language through reading, writing, and communication skills."},
            {"name": "Social Studies", "description": "Understanding societal structures, history, geography, and cultural studies."},
            {"name": "History", "description": "The history of Sierra Leone and the world, from ancient times to the modern era."},
            {"name": "Government and Civic Education", "description": "The study of governance, political systems, and citizens' rights and responsibilities."},
            {"name": "Physical Health Education", "description": "Promoting physical fitness, sports, and overall well-being."},
            {"name": "Health Science", "description": "Learning about the human body, diseases, healthcare, and wellness."},
            {"name": "Literature", "description": "Studying classic and contemporary literature from Sierra Leone and other regions."},
            {"name": "Geography", "description": "Understanding physical and human geography, climate, and ecosystems."},
            {"name": "French Language", "description": "Learning the French language for communication and cultural exchange."},
            {"name": "Information Technology", "description": "Basics of computer science, programming, and digital literacy."},
            {"name": "Agricultural Science", "description": "Exploring agricultural practices, food production, and sustainability."},
            {"name": "Economics", "description": "Introduction to economic principles, including microeconomics and macroeconomics."},
            {"name": "Art and Design", "description": "Fostering creativity through drawing, painting, and visual arts."},
            {"name": "Home Economics", "description": "Practical skills for managing a household, including cooking and budgeting."},
            {"name": "Business Studies", "description": "Introduction to business principles, entrepreneurship, and management."},
            {"name": "Religious and Moral Education", "description": "Studying different religions and moral values to foster ethical behavior."}
        ]

        # Create subjects in the database
        for subject_data in dummy_subjects:
            Subject.objects.create(**subject_data)

        self.stdout.write(self.style.SUCCESS("Sierra Leonean academic subjects have been created successfully."))
