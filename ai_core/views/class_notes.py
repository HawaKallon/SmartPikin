
import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
import markdown
import logging
from langchain_groq import ChatGroq
from groq import Groq
from langchain_core.prompts import ChatPromptTemplate

from ai_core.models import ResourceModel, ResourceType, ClassLevel, DifficultyLevel, DocumentChunk, SubjectChoices
import PyPDF2
from django.core.files.storage import default_storage
from ai_core.utils import extract_text_from_pdf, search_similar_chunks

logger = logging.getLogger(__name__)
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# Initialize Llama 3 with Groq LPU
chat = ChatGroq(temperature=0, model_name="deepseek-r1-distill-llama-70b")

# System and human prompts (unchanged)
system_prompt = (
    "You are a highly experienced educator with 20 years of experience in designing educational assessments "
    "for Sierra Leonean students. Your goal is to generate diverse types of exam questions based on the class level, "
    "topic, resource type, and difficulty level. Follow these guidelines to ensure that the questions are clear, effective, "
    "and aligned with WAEC standards:\n\n"

    "**Guidelines for Question Types:**\n\n"

    "1. **Multiple Choice Questions (MCQs):**\n"
    "   - Provide four options (A, B, C, D) with one correct answer.\n"
    "   - Ensure that the questions test basic understanding and conceptual clarity.\n"
    "   - The options should be distinct, with no patterns in the correct answers.\n\n"

    "2. **Essay Questions:**\n"
    "   - Provide open-ended questions that require detailed answers.\n"
    "   - The questions should encourage critical thinking, analysis, and application of concepts.\n\n"

    "3. **Scenario-Based Questions:**\n"
    "   - Present a real-life scenario or a problem situation.\n"
    "   - Follow with thought-provoking questions that ask students to apply their knowledge to solve or analyze the scenario.\n\n"

    "4. **Class Exercises:**\n"
    "   - Provide practice exercises for students to solve during class.\n"
    "   - These should encourage application of concepts in problem-solving contexts.\n\n"

    "5. **Homework Assignments:**\n"
    "   - Provide take-home tasks that promote deeper understanding of the topic.\n"
    "   - Ensure the tasks are related to the topic and help students practice what they’ve learned.\n\n"

    "6. **Interactive Sessions:**\n"
    "   - Provide discussion-based questions to encourage classroom interaction and peer learning.\n\n"

    "7. **Experiments & Practicals:**\n"
    "   - Provide step-by-step tasks for practical learning.\n"
    "   - Ensure the tasks can be completed with the available resources and are easy to follow.\n\n"

    "Ensure the content is organized, clear, and adheres to the curriculum standards for Sierra Leonean students."
)

human_prompt = (
    "Generate only  {resource_type} questions for {class_level} students on the topic '{topic}' and {subject}. "
    "Ensure the difficulty level is '{difficulty_level}'. Provide well-structured content that aligns with WAEC standards. "
    "The questions should be clear, concise, and encourage critical thinking. Based on the resource type, generate questions "
    "that will test the student's understanding, application, and analysis of the topic. Ensure all questions are appropriately "
    "structured and the answers are accurate. Present the questions in a neat and professional format. \n\n"

    "For MCQs: Provide four options (A, B, C, D) with one correct answer and ensure no patterns in the correct answers.\n"
    "For Essay Questions: Provide a detailed question that encourages long-form answers.\n"
    "For Scenario-Based Questions: Present a real-world scenario and ask relevant follow-up questions.\n"
    "For Class Exercises: Provide practical problems to solve in class.\n"
    "For Homework Assignments: Provide take-home questions for further practice.\n"
    "For Interactive Sessions: Encourage discussion with open-ended questions.\n"
    "For Experiments & Practicals: Provide step-by-step instructions for experiments."
)
prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])





class QuestionBankGeneratorView(LoginRequiredMixin, View):
    template_name = "ai_core/question_generator.html"

    def get(self, request):
        """Render the question generation form."""
        return render(
            request,
            self.template_name,
            {
                "class_levels": ClassLevel.choices,
                "subjects": SubjectChoices.choices,
                "resource_types": ResourceType.choices,
                "difficulty_levels": DifficultyLevel.choices,
            },
        )

    def post(self, request):
        """Generate questions based on user input."""
        class_level = request.POST.get("class_level")
        topic = request.POST.get("topic")
        subject = request.POST.get("subject")
        resource_type = request.POST.get("resource_type")
        difficulty_level = request.POST.get("difficulty_level")
        number_of_questions = int(request.POST.get("number_of_questions", 5))
        pdf_file = request.FILES.get("pdf_file")

        if not all([class_level, topic, subject, resource_type, difficulty_level]):
            messages.error(request, "Please fill out all fields.")
            return render(request, self.template_name)

        # Extract text from PDF (if uploaded)
        pdf_text = extract_text_from_pdf(pdf_file) if pdf_file else None

        # Retrieve relevant FAISS chunks
        relevant_chunks = self.retrieve_relevant_chunks(topic)

        # Generate questions
        resource_content = self.generate_question_content(
            class_level, topic, subject, resource_type, difficulty_level, number_of_questions, pdf_text, relevant_chunks
        )

        if resource_content:
            content_html = markdown.markdown(resource_content)
            saved_resource = ResourceModel.objects.create(
                class_level=class_level,
                topic=topic,
                subject=subject,
                resource_type=resource_type,
                number_of_questions=number_of_questions,
                difficulty_level=difficulty_level,
                content=content_html,
                pdf_file=pdf_file if pdf_file else None,
            )
            return render(
                request,
                self.template_name,
                {
                    "class_levels": ClassLevel.choices,
                    "subjects": SubjectChoices.choices,
                    "resource_types": ResourceType.choices,
                    "difficulty_levels": DifficultyLevel.choices,
                    "class_level": class_level,
                    "subject": subject,
                    "topic": topic,
                    "number_of_questions": number_of_questions,
                    "resource_type": resource_type,
                    "difficulty_level": difficulty_level,
                    "resource_content": content_html,
                    "resource_id": saved_resource.id,
                },
            )
        else:
            messages.error(request, "Failed to generate questions. Please try again.")
            return render(request, self.template_name)

    def retrieve_relevant_chunks(self, topic):
        """Retrieve relevant document chunks using cosine similarity search."""
        try:
            handbook_chunks = DocumentChunk.objects.filter(
                document_type__in=["Primary School Handbook", "JSS Handbook", "SSS Handbook"]
            )
            relevant = search_similar_chunks(topic, chunks=handbook_chunks, top_k=5)
            return [chunk.chunk_text for chunk in relevant]
        except Exception as e:
            logger.warning(f"Error retrieving chunks: {e}")
            return []

    def generate_question_content(self, class_level, topic, subject, resource_type, difficulty_level, number_of_questions, pdf_text=None, relevant_chunks=None):
        """Generate question content using AI based on input parameters."""
        try:
            formatted_prompt = prompt.format_messages(
                resource_type=resource_type,
                class_level=class_level,
                topic=topic,
                subject=subject,
                number_of_questions=number_of_questions,
                difficulty_level=difficulty_level,
            )

            if pdf_text:
                formatted_prompt.append(("system", f"Here is the text extracted from the uploaded PDF:\n\n{pdf_text}"))

            if relevant_chunks:
                chunks_text = "\n\n".join(relevant_chunks)
                formatted_prompt.append(("system", f"Here are some relevant excerpts from the handbooks:\n\n{chunks_text}"))

            response = chat.invoke(formatted_prompt)
            return response.content

        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return None
