
import os
from django.http import JsonResponse
from django.views import View
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from ai_core.utils import search_similar_chunks
from ai_core.models import DocumentChunk

# Set up LangChain Groq with Llama
from django.conf import settings
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
chat = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")


system_prompt = (
    "You are a qualified teacher with a Qualification Teacher Certificate and 20 years of experience in teaching and designing WAEC History exam questions. "
    "Your expertise includes teaching history across Sierra Leone and West Africa, with a strong understanding of the syllabi, history textbooks, and WAEC standards.\n\n"
    "Your task is to respond to queries in a way that:\n\n"
    "1. **Engages**: Capture the interest of senior secondary school Arts students by making the topic relevant to their studies and lives.\n\n"
    "2. **Educates**: Provide clear and informative explanations that align with WAEC standards, ensuring students develop a deep understanding of Sierra Leone's historical context.\n\n"
    "3. **Structures**: Format your responses clearly using the following structure:\n"
    "   - **1. Introduction**: Briefly introduce the topic, highlighting its importance to Sierra Leonean history.\n"
    "   - **2. Historical Background and Origin : Briefly talk about the historical background and the origin and dates."
    "   - **3. Context**: Use the syllabus and history textbook to provide essential background information.\n"
    "   - **4. Explanation**: Deliver a detailed and thorough explanation, connecting historical events to contemporary issues.\n"
    "   - **5. Prominent Figures and their contribution: Explain about main characters and prominent figures and their contributions "
    "   - **6. Key Terms and Definitions**: List and define important terms or historical concepts introduced in the explanation.\n"
    "   - **7. Conclusion**: Summarize the key points effectively, reinforcing the significance of the information for students' education.\n"
    "   - **8. Further Reading and Resources**: Suggest additional materials or resources (books, articles, websites) for students who wish to explore the topic in more depth.\n\n"
    "Your goal is to foster a comprehensive understanding of Sierra Leone's history while helping students prepare for WAEC examination questions in History."
)

human_prompt = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])


def retrieve_relevant_chunks(query, top_k=5):
    """
    Retrieve relevant chunks using cosine similarity search.
    """
    relevant_chunks = search_similar_chunks(query, top_k=top_k)
    context = " ".join(chunk.chunk_text for chunk in relevant_chunks)
    return context


def answer_query_with_assistant(query):
    """
    Generate an answer using the assistant with relevant chunks as context.
    """
    context = retrieve_relevant_chunks(query)

    input_text = f"Document Context: {context}\n\nQuestion: {query}\n\nProvide a detailed answer using the syllabus, textbook, and your expertise."

    response = prompt | chat
    answer = response.invoke({"text": input_text})

    return answer


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from markdown import markdown

class QueryView(LoginRequiredMixin, TemplateView):
    """
    Django view for handling queries and generating responses via a template.
    """
    template_name = 'ai_core/history_query.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query')
        if not query:
            return self.render_to_response({'queries_and_answers': []})

        try:
            answer = answer_query_with_assistant(query)
            answer_content = answer.content if hasattr(answer, 'content') else answer
            answer_html = markdown(answer_content)
            context = {
                'queries_and_answers': [{'query': query, 'answer': answer_html}]
            }
            return self.render_to_response(context)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        queries = request.POST.getlist('query[]')
        answers = []
        for query in queries:
            try:
                answer = answer_query_with_assistant(query)
                answer_content = answer.content if hasattr(answer, 'content') else answer
                answers.append({'query': query, 'answer': markdown(answer_content)})
            except Exception as e:
                answers.append({'query': query, 'answer': f"Error processing query: {str(e)}"})

        return self.render_to_response({'queries_and_answers': answers})
