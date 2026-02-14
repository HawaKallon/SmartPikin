# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.http import JsonResponse
# from core.models import SummarizedContent
# import google.generativeai as genai
# import pdfplumber
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# def summarize_content_with_gemini(content):
#     """Summarizes educational content using the Google Gemini model."""
#     try:
#         # Initialize the generative model
#         model = genai.GenerativeModel("gemini-2.0-flash")
#         # Create a prompt specifically for summarization
#         prompt = (
#             f"Summarize the following educational content in a way that helps a teacher "
#             f"understand and teach the key concepts effectively in Sierra Leone: {content} "
#             f"Make sure to highlight the most important points, suggest teaching strategies, "
#             f"and mention any practical examples that could be relevant to students in West Africa."
#         )
#         # Generate content using the model
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         logger.error(f"Error generating summary: {e}")
#         return "An error occurred while generating the summary."
#
#
# def teacher_summarization_form(request):
#     """View to handle content summarization."""
#     if request.method == "POST":
#         text_content = request.POST.get('content')
#         file = request.FILES.get('file')
#
#         if file:
#             # Handle file upload (PDF or text)
#             if file.name.endswith('.pdf'):
#                 try:
#                     with pdfplumber.open(file) as pdf:
#                         text_content = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
#                 except Exception as e:
#                     logger.error(f"Error extracting text from PDF: {e}")
#                     messages.error(request, "Error processing the uploaded PDF file.")
#                     return render(request, "ai_core/teacher_summarization_form.html")
#             elif file.name.endswith('.txt'):
#                 try:
#                     text_content = file.read().decode('utf-8')
#                 except Exception as e:
#                     logger.error(f"Error reading text file: {e}")
#                     messages.error(request, "Error processing the uploaded text file.")
#                     return render(request, "ai_core/teacher_summarization_form.html")
#             else:
#                 messages.error(request, "Unsupported file type. Please upload a PDF or text file.")
#                 return render(request, "ai_core/teacher_summarization_form.html")
#
#         if not text_content:
#             messages.error(request, "Please provide some content to summarize.")
#             return render(request, "ai_core/teacher_summarization_form.html")
#
#         # Generate the summary using the Gemini model
#         summary = summarize_content_with_gemini(text_content)
#
#         # Save the summarized content to the database
#         summarized_content = SummarizedContent(
#             user=request.user,
#             original_content=text_content,
#             summarized_content=summary,
#             content_type='pdf' if file and file.name.endswith('.pdf') else 'text',  # Adjust as needed
#             uploaded_file=file if file else None
#         )
#         summarized_content.save()
#
#         return render(request, "ai_core/teacher_summarization_form.html", {
#             "summary": summary,
#             "summarized_content": summarized_content
#         })
#
#     return render(request, "ai_core/teacher_summarization_form.html")
import os
import markdown
import pdfkit
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from groq import Groq

from core.models import SummarizedContent
from django.views import View
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Configure Groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)


class SummarizationView(LoginRequiredMixin, View):
    template_name = 'ai_core/teacher_summarization_form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Get the content from the form (either pasted or uploaded)
        content = request.POST.get('content')  # Text from input
        file = request.FILES.get('file')  # Uploaded file (PDF, text, etc.)

        if file:
            # Handle file upload (PDF or text)
            if file.name.endswith('.pdf'):
                # Extract text from PDF
                text_content = self.extract_text_from_pdf(file)
            elif file.name.endswith('.txt'):
                # Read content from text file
                text_content = file.read().decode('utf-8')
            else:
                messages.error(request, "Unsupported file type. Please upload a PDF or text file.")
                return render(request, self.template_name)
        elif content:
            text_content = content
        else:
            messages.error(request, "Please provide content to summarize.")
            return render(request, self.template_name)

        # Generate the summary using Gemini model
        summary = self.summarize_content_with_gemini(text_content)

        # Convert summary to HTML using markdown
        summary_html = markdown.markdown(summary)

        # Save the summarized content to the database
        summarized_content = SummarizedContent.objects.create(
            user=request.user,
            original_content=text_content,
            summarized_content=summary,
            content_html=summary_html
        )

        return render(request, self.template_name, {
            'summary': summary,
            'summary_html': summary_html,
            'summarized_content_id': summarized_content.id
        })

    def summarize_content_with_gemini(self, content):
        """Summarize the educational content using Groq."""
        try:
            prompt = (
                f"Create a concise and informative summary of the following educational content, tailored to "
                f"facilitate effective teaching and learning in a West African context, particularly in Sierra Leone: "
                f"\n{content}. In your summary, identify the most critical concepts and key takeaways, highlight "
                "relevant cultural, social, or environmental contexts, and use local references or cultural analogies "
                "to explain technical concepts. Incorporate historical or cultural context that is relevant to the "
                "educational content, and highlight regional challenges or successes that can inform teaching "
                "strategies. Suggest practical, locally relevant examples or case studies to illustrate complex ideas "
                "and promote deeper comprehension, and offer actionable teaching strategies and tips for lesson "
                "planning, incorporating indigenous knowledge and regional perspective. Emphasize connections to "
                "existing curriculum standards and learning objectives in Sierra Leone, where applicable, "
                "and summarize the content in approximately 450-800 words, ensuring that the language is clear, "
                "concise, and accessible to educators in West Africa."
            )
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "An error occurred while generating the summary."

    def extract_text_from_pdf(self, file):
        """Extract text from PDF file."""
        import pdfplumber
        try:
            with pdfplumber.open(file) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""


@login_required
def download_summarized_content_pdf(request, id):
    """Generate and download the summarized content as a PDF."""
    summarized_content = get_object_or_404(SummarizedContent, id=id, user=request.user)
    summarized_content_html = summarized_content.content_html

    if not summarized_content_html:
        messages.error(request, "No summarized content available to download.")
        return redirect('ai_core:teacher_summarization_form')

    # Generate PDF from HTML content
    pdf = pdfkit.from_string(summarized_content_html, False, options={"enable-local-file-access": None})

    # Return the PDF as an HTTP response to trigger the download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="summarized_content_{summarized_content.id}.pdf"'
    return response


class SummarizedContentListView(LoginRequiredMixin, ListView):
    model = SummarizedContent
    template_name = 'ai_core/summarized_content_list.html'  # The template for displaying the list
    context_object_name = 'summarized_contents'

    def get_queryset(self):
        # Only return summarized content created by the current user
        return SummarizedContent.objects.filter(user=self.request.user).order_by('-created_at')

