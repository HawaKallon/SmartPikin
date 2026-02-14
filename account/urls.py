from django.urls import path
from .views import (
    TeacherRegisterView,
    StudentRegisterView,
    GuardianRegisterView,
    CustomLoginView,
    CustomLogoutView
)
from .views import (
    TeacherProfileUpdateView,
    StudentProfileUpdateView,
    GuardianProfileUpdateView,
    TutorProfileUpdateView
)

app_name = 'account'

urlpatterns = [
    path('register/teacher/', TeacherRegisterView.as_view(), name='teacher_register'),
    path('register/student/', StudentRegisterView.as_view(), name='student_register'),
    path('register/guardian/', GuardianRegisterView.as_view(), name='guardian_register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('teacher/update/', TeacherProfileUpdateView.as_view(), name='teacher_profile_update'),
    path('student/update/', StudentProfileUpdateView.as_view(), name='student_profile_update'),
    path('guardian/update/', GuardianProfileUpdateView.as_view(), name='guardian_profile_update'),
    path('tutor/update/', TutorProfileUpdateView.as_view(), name='tutor_profile_update'),

]