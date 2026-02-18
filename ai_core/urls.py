from django.urls import path

from ai_core.views.class_notes import StudyFromNotesView
from ai_core.views.content_summerization import SummarizationView, \
    download_summarized_content_pdf, SummarizedContentListView
from ai_core.views.content_creation import LessonPlanGeneratorView, download_lesson_plan, \
    LessonPlanListView
from ai_core.views.creative_writings import CreativeWritingAssistantView, download_writing_prompt_pdf, \
    CreativeWritingPromptListView
from ai_core.views.exam_simulator import ExamSimulatorView, submit_exam, exam_results, exam_history
from ai_core.views.flashcards import FlashcardGeneratorView
from ai_core.views.quiz_mode import QuizModeView, save_quiz_score

app_name = 'ai_core'

urlpatterns = [
    path('lesson-plan-generator/', LessonPlanGeneratorView.as_view(), name='lesson_plan_generator'),
    path('download-lesson-plan/<int:id>/', download_lesson_plan, name='download_lesson_plan'),
    path('list_lesson_plan/', LessonPlanListView.as_view(), name='lesson_plan_list'),

    path('summarize_form/', SummarizationView.as_view(), name='teacher_summarization_form'),
    path('download_summarized_content/<int:id>/', download_summarized_content_pdf,
         name='download_summarized_content_pdf'),
    path('summarized-content/', SummarizedContentListView.as_view(), name='summarized_content_list'),

    path('creative_writing/', CreativeWritingAssistantView.as_view(), name='creative_writing'),
    path('download-writing/<int:id>/', download_writing_prompt_pdf, name='download_writing_prompt_pdf'),
    path('creative-writing-prompts/', CreativeWritingPromptListView.as_view(), name='creative_writing_prompt_list'),

    path('study-from-notes/', StudyFromNotesView.as_view(), name='study_from_notes'),

    path('quiz/', QuizModeView.as_view(), name='quiz_mode'),
    path('quiz-save/', save_quiz_score, name='quiz_save'),
    path('flashcards/', FlashcardGeneratorView.as_view(), name='flashcard_generator'),

    path('exam/', ExamSimulatorView.as_view(), name='exam_simulator'),
    path('exam/submit/', submit_exam, name='exam_submit'),
    path('exam/results/<int:session_id>/', exam_results, name='exam_results'),
    path('exam/history/', exam_history, name='exam_history'),
]
