from django.urls import path

from ai_core.views.ai_report_card import ReportCardWizardView
from ai_core.views.aihistory import QueryView
from ai_core.views.class_notes import QuestionBankGeneratorView
from ai_core.views.content_summerization import SummarizationView, \
    download_summarized_content_pdf, SummarizedContentListView
from ai_core.views.content_creation import LessonPlanGeneratorView, download_lesson_plan, \
    LessonPlanListView
from ai_core.views.creative_writings import CreativeWritingAssistantView, download_writing_prompt_pdf, \
    CreativeWritingPromptListView
from ai_core.views.image_card import ReportCardUploadView
from ai_core.views.maths_assistant import MathLessonNoteGeneratorView, download_math_lesson, MathLessonNoteListView

app_name = 'ai_core'

urlpatterns = [
    path('lesson-plan-generator/', LessonPlanGeneratorView.as_view(), name='lesson_plan_generator'),
    path('download-lesson-plan/<int:id>/', download_lesson_plan, name='download_lesson_plan'),
    path('summarize_form/', SummarizationView.as_view(), name='teacher_summarization_form'),
    path('download_summarized_content/<int:id>/', download_summarized_content_pdf,
         name='download_summarized_content_pdf'),
    path('list_lesson_plan/', LessonPlanListView.as_view(), name='lesson_plan_list'),

    path('creative_writing/', CreativeWritingAssistantView.as_view(), name='creative_writing'),
    path('download-writing/<int:id>/', download_writing_prompt_pdf, name='download_writing_prompt_pdf'),
    path('summarized-content/', SummarizedContentListView.as_view(), name='summarized_content_list'),
    path('creative-writing-prompts/', CreativeWritingPromptListView.as_view(), name='creative_writing_prompt_list'),

    path('math-lesson-generator/', MathLessonNoteGeneratorView.as_view(), name='math_lesson_note_generator'),
    path('math-lesson-list/', MathLessonNoteListView.as_view(), name='math_lesson_note_list'),
    path('math-lesson-download/<int:id>/', download_math_lesson, name='download_math_lesson'),
    path('query/', QueryView.as_view(), name='query'),
    path('report-card/', ReportCardWizardView.as_view(), name='report_card_wizard'),
    path('upload/', ReportCardUploadView.as_view(), name='upload_image'),
    path('generate-questions/', QuestionBankGeneratorView.as_view(), name='question_generator'),

]
