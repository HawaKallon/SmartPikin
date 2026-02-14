from django.views.generic import TemplateView
from django.db.models import Q, Avg


class HomePage(TemplateView):
    template_name = 'base/index.html'

    # Override the `get_context_data` method to add context to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all schools
        schools = School.objects.all()
        context['schools'] = schools

        # Total school counts
        context['total_schools'] = schools.count()

        # Categorize schools by type
        context['primary_schools'] = schools.filter(school_type='Primary')
        context['secondary_schools'] = schools.filter(school_type='Secondary')[:3]
        context['vocational_schools'] = schools.filter(school_type='Vocational')

        # Categorize schools by ownership type
        context['private_schools'] = schools.filter(ownership_type='Private')
        context['government_schools'] = schools.filter(ownership_type='Government')

        # Fetch top schools by total enrollment
        context['top_schools_by_enrollment'] = schools.order_by('-total_enrollment')[:5]

        # Additional context for messaging
        context['page_title'] = "Welcome to Our Schools Portal"
        context['header_message'] = "Explore Schools and Their Statistics"

        return context


from django.views.generic.list import ListView
from account.models import TeacherProfile, School


class TeacherListView(ListView):
    model = TeacherProfile
    template_name = 'teachers/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 10

    def get_queryset(self):
        """
        Get filtered, sorted, and searched queryset based on user input.
        """
        queryset = TeacherProfile.objects.select_related('user', 'school')

        # Extract filters and search parameters
        search_query = self.request.GET.get('search', '')
        teacher_status = self.request.GET.get('status', '')
        school_filter = self.request.GET.get('school', '')
        specialization_filter = self.request.GET.get('specialization', '')
        certification_filter = self.request.GET.get('certification', '')
        sort_by = self.request.GET.get('sort_by', 'user__first_name')  # Default sorting by first name

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(favorite_subjects__icontains=search_query)
            )

        specialization_filter = self.request.GET.get('specialization', '')
        certification_filter = self.request.GET.get('certification', '')

        # Apply specialization filter
        if specialization_filter:
            queryset = queryset.filter(specialization=specialization_filter)

        # Apply certification filter
        if certification_filter:
            queryset = queryset.filter(certifications=certification_filter)

        # Apply sorting
        queryset = queryset.order_by(sort_by)
        # Debugging SQL query

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schools'] = School.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['selected_school'] = self.request.GET.get('school', '')
        context['sort_by'] = self.request.GET.get('sort_by', '')
        context['specializations'] = TeacherProfile.SPECIALIZATION_CHOICES
        context['certifications'] = TeacherProfile.CERTIFICATION_CHOICES
        context['selected_specialization'] = self.request.GET.get('specialization', '')
        context['selected_certification'] = self.request.GET.get('certification', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Handle AJAX and standard HTTP responses.
        """
        # If the request is an AJAX request, return partial HTML for dynamic updates
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('teachers/teacher_list_partial.html', context)
            return JsonResponse({'html': html})

        # Default behavior for standard HTTP requests
        return super().render_to_response(context, **response_kwargs)


from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from account.models import TeacherProfile, Subject, School


class TeacherProfileDetailView(DetailView):
    model = TeacherProfile
    template_name = "teachers/teacher_profile_detail.html"  # Customize this path to your template
    context_object_name = "teacher_profile"

    def get_object(self):
        """Override to fetch teacher profile based on primary key or slug."""
        return get_object_or_404(TeacherProfile, pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        """Add additional context for a more informative page."""
        context = super().get_context_data(**kwargs)
        teacher_profile = self.object

        # Related teachers from the same school
        context["related_teachers"] = (
            TeacherProfile.objects.filter(school=teacher_profile.school)
            .exclude(pk=teacher_profile.pk)
            .select_related("school")
            .prefetch_related("subjects")[:5]
        )

        # Subjects taught by the teacher
        context["teacher_subjects"] = teacher_profile.subjects.all()

        # Information about the teacher's school
        context["school"] = teacher_profile.school

        # Example of QR code generation (if necessary to display dynamically)
        context["teacher_qr_code"] = teacher_profile.generate_qr_code()

        return context


from django.views.generic import ListView
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from account.models import School

from account.models import District  # Ensure the District model is imported

from django.core.cache import cache


class SchoolListView(ListView):
    model = School
    template_name = 'schools/school_list.html'
    context_object_name = 'schools'
    paginate_by = 6

    def get_queryset(self):
        """Fetch the filtered and sorted schools."""
        queryset = School.objects.select_related('district').prefetch_related('subjects')

        # Extract filters and search parameters
        search_query = self.request.GET.get('search', '')
        school_type = self.request.GET.get('school_type', '')
        ownership_type = self.request.GET.get('ownership_type', '')
        district_id = self.request.GET.get('district', '')
        min_enrollment = self.request.GET.get('min_enrollment', None)
        max_enrollment = self.request.GET.get('max_enrollment', None)
        teacher_ratio = self.request.GET.get('teacher_ratio', None)
        sort_by = self.request.GET.get('sort_by', 'name')

        # Apply filters
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(facilities_summary__icontains=search_query) |
                Q(extra_curricular_activities__icontains=search_query)
            )
        if school_type:
            queryset = queryset.filter(school_type=school_type)
        if ownership_type:
            queryset = queryset.filter(ownership_type=ownership_type)
        if district_id:
            queryset = queryset.filter(district__id=district_id)
        if min_enrollment:
            queryset = queryset.filter(total_enrollment__gte=min_enrollment)
        if max_enrollment:
            queryset = queryset.filter(total_enrollment__lte=max_enrollment)
        if teacher_ratio:
            queryset = queryset.filter(teacher_to_student_ratio__gte=teacher_ratio)

        # Apply sorting
        if sort_by in ['name', 'total_enrollment', 'teacher_to_student_ratio']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        """Add extra context to the view."""
        context = super().get_context_data(**kwargs)

        # Cache district options to avoid repeated queries
        districts = cache.get('district_options')
        if not districts:
            districts = District.objects.all()
            cache.set('district_options', districts, timeout=3600)

        context.update({
            'school_types': School.SCHOOL_TYPE_CHOICES,
            'ownership_types': School.OWNERSHIP_CHOICES,
            'districts': districts,
            'search_query': self.request.GET.get('search', ''),
            'selected_school_type': self.request.GET.get('school_type', ''),
            'selected_ownership_type': self.request.GET.get('ownership_type', ''),
            'selected_district': self.request.GET.get('district', ''),
            'min_enrollment': self.request.GET.get('min_enrollment', ''),
            'max_enrollment': self.request.GET.get('max_enrollment', ''),
            'teacher_ratio': self.request.GET.get('teacher_ratio', ''),
            'sort_by': self.request.GET.get('sort_by', 'name'),
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        """Support AJAX pagination for seamless user experience."""
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('schools/school_list_partial.html', context)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)


class SchoolDetailView(DetailView):
    model = School
    template_name = 'schools/school_detail.html'
    context_object_name = 'school'

    def get_context_data(self, **kwargs):
        """Add detailed context for the school."""
        context = super().get_context_data(**kwargs)
        school = self.object

        # Prefetch related data for efficiency
        school_teachers = school.teachers.select_related('user').prefetch_related('subjects')
        school_subjects = school.subjects.all()
        media = school.media.all()
        facilities = school.facilities.all()

        # Calculate analytics
        average_teacher_experience = school_teachers.aggregate(
            avg_experience=Avg('years_of_experience')
        )['avg_experience']
        enrollment_trends = self.get_enrollment_data(school)

        # Context additions
        context.update({
            'district': school.district,
            'teachers': school_teachers,
            'average_teacher_experience': average_teacher_experience,
            'performance_metrics': school.performance_metrics,
            'certificates': school.school_certificates.split(',') if school.school_certificates else [],
            'subjects': school_subjects,
            'extra_curricular_activities': school.extra_curricular_activities.split(
                ',') if school.extra_curricular_activities else [],
            'total_teachers': school_teachers.count(),
            'total_students': school.total_enrollment,
            'enrollment_over_years': enrollment_trends,
            'teacher_student_ratio': school.teacher_to_student_ratio,
            'media': media,
            'facilities': facilities,
            'exam_statuses': [
                ('WASSCE', school.take_wassce),
                ('BECE', school.take_bece),
                ('NPSE', school.take_npse),
            ],
            'gallery_images': media.filter(media_type='image'),
            'youtube_videos': media.filter(media_type='youtube'),
        })
        return context

    def get_enrollment_data(self, school):
        """Mock or real enrollment trend data."""
        return [
            {'year': '2018', 'enrollment': 300},
            {'year': '2019', 'enrollment': 320},
            {'year': '2020', 'enrollment': 350},
            {'year': '2021', 'enrollment': 400},
            {'year': '2022', 'enrollment': 450},
        ]
