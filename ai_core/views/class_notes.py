
import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
import markdown
import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from ai_core.models import ResourceModel, ResourceType, ClassLevel, DifficultyLevel
from ai_core.utils import extract_text_from_pdf

logger = logging.getLogger(__name__)
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

chat = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")

system_prompt = (
    "You are a highly experienced educator specializing in creating study materials for Sierra Leonean students. "
    "A student has shared their own notes or study material with you. Your job is to generate useful study content "
    "based on what they uploaded.\n\n"
    "Based on the output type requested, generate:\n\n"
    "**Questions & Answers:** Generate clear, well-structured questions with answers based on the student's notes. "
    "Include a mix of short-answer, multiple-choice (with 4 options), and explanation questions.\n\n"
    "**Summary Notes:** Condense the material into a clean, organized summary with key points, definitions, "
    "and important concepts highlighted.\n\n"
    "**Practice Problems:** Generate practice exercises and problems the student can work through to test "
    "their understanding of the material.\n\n"
    "**Key Concepts:** Extract and explain the most important concepts, terms, and ideas from the notes.\n\n"
    "Always present content in a clear, well-formatted way. Use headings, bullet points, and numbering. "
    "Align content with WAEC standards where applicable."
)

human_prompt = (
    "Here are the student's notes:\n\n{student_notes}\n\n"
    "Generate {output_type} based on this material. "
    "Difficulty level: {difficulty_level}. "
    "Number of items to generate: {num_items}.\n\n"
    "Make the output clear, well-organized, and useful for exam revision."
)

prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])


class StudyFromNotesView(LoginRequiredMixin, View):
    template_name = "ai_core/study_from_notes.html"

    def get(self, request):
        return render(request, self.template_name, {
            "output_types": [
                ("questions", "Questions & Answers"),
                ("summary", "Summary Notes"),
                ("practice", "Practice Problems"),
                ("concepts", "Key Concepts"),
            ],
            "difficulty_levels": DifficultyLevel.choices,
        })

    def post(self, request):
        pasted_text = request.POST.get("pasted_text", "").strip()
        pdf_file = request.FILES.get("pdf_file")
        output_type = request.POST.get("output_type", "questions")
        difficulty_level = request.POST.get("difficulty_level", "Average")
        num_items = int(request.POST.get("num_items", 10))

        output_type_labels = {
            "questions": "Questions & Answers",
            "summary": "Summary Notes",
            "practice": "Practice Problems",
            "concepts": "Key Concepts",
        }

        # Extract text from uploaded PDF
        pdf_text = extract_text_from_pdf(pdf_file) if pdf_file else None

        # Combine sources
        student_notes = ""
        if pasted_text:
            student_notes += pasted_text
        if pdf_text:
            if student_notes:
                student_notes += "\n\n---\n\n"
            student_notes += pdf_text

        if not student_notes:
            messages.error(request, "Please paste your notes or upload a PDF.")
            return render(request, self.template_name, {
                "output_types": [
                    ("questions", "Questions & Answers"),
                    ("summary", "Summary Notes"),
                    ("practice", "Practice Problems"),
                    ("concepts", "Key Concepts"),
                ],
                "difficulty_levels": DifficultyLevel.choices,
            })

        # Truncate very long notes to avoid token limits
        if len(student_notes) > 12000:
            student_notes = student_notes[:12000] + "\n\n[Notes truncated for processing...]"

        try:
            formatted = prompt.format_messages(
                student_notes=student_notes,
                output_type=output_type_labels.get(output_type, output_type),
                difficulty_level=difficulty_level,
                num_items=num_items,
            )
            response = chat.invoke(formatted)
            content_html = markdown.markdown(response.content)
        except Exception as e:
            logger.error(f"Error generating study material: {e}")
            messages.error(request, "Something went wrong generating your study material. Please try again.")
            return render(request, self.template_name, {
                "output_types": [
                    ("questions", "Questions & Answers"),
                    ("summary", "Summary Notes"),
                    ("practice", "Practice Problems"),
                    ("concepts", "Key Concepts"),
                ],
                "difficulty_levels": DifficultyLevel.choices,
            })

        return render(request, self.template_name, {
            "output_types": [
                ("questions", "Questions & Answers"),
                ("summary", "Summary Notes"),
                ("practice", "Practice Problems"),
                ("concepts", "Key Concepts"),
            ],
            "difficulty_levels": DifficultyLevel.choices,
            "result_content": content_html,
            "output_type_label": output_type_labels.get(output_type, output_type),
            "difficulty_level": difficulty_level,
            "num_items": num_items,
            "selected_output_type": output_type,
            "selected_difficulty": difficulty_level,
        })
