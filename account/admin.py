from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, School, TeacherProfile, StudentProfile, GuardianProfile, TutorProfile, TutorRequest, \
    ContentCreationRequest, Subject, District


# Register the CustomUser model with a custom UserAdmin class.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'role']
    list_filter = ['role']
    # Remove ordering by username
    ordering = ['email']  # You can order by email or any other field you have in your CustomUser model
    fieldsets = [
        ['Personal info', {'fields': ['email', 'first_name', 'last_name']}],
        ['Permissions', {'fields': ['is_staff', 'is_superuser', 'role']}],
    ]
    add_fieldsets = [
        [None, {'classes': ['wide'], 'fields': ['email', 'password1', 'password2', 'first_name', 'last_name', 'role']}]
    ]
    search_fields = ['email', 'first_name', 'last_name']


admin.site.register(CustomUser, CustomUserAdmin)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_type']
    list_filter = ['school_type']


admin.site.register(School, SchoolAdmin)


class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'teacher_status']
    list_filter = ['school', 'teacher_status']


admin.site.register(TeacherProfile, TeacherProfileAdmin)


class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'grade']
    list_filter = ['school', 'grade']


admin.site.register(StudentProfile, StudentProfileAdmin)


class GuardianProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'relationship_to_student']
    list_filter = ['relationship_to_student']


admin.site.register(GuardianProfile, GuardianProfileAdmin)


class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ['user',  'hourly_rate']



admin.site.register(TutorProfile, TutorProfileAdmin)


class TutorRequestAdmin(admin.ModelAdmin):
    list_display = [ 'requested_tutor', 'request_date']
    list_filter = ['request_date']


admin.site.register(TutorRequest, TutorRequestAdmin)


class ContentCreationRequestAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'content_type', 'request_date']
    list_filter = ['content_type', 'request_date']


admin.site.register(ContentCreationRequest, ContentCreationRequestAdmin)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Fields to display in the admin list view
    search_fields = ('name',)  # Fields to add search functionality
    ordering = ('name',)  # Order the subjects by name


# Register the Subject model with the admin site
admin.site.register(Subject, SubjectAdmin)


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'region', 'population')

admin.site.register(District, DistrictAdmin)
