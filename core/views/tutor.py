from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.generic import ListView
from account.models import TutorProfile, Subject  # Import models


class TutorListView(ListView):
    model = TutorProfile
    template_name = 'tutors/tutor_list.html'  # Update with your template path
    context_object_name = 'tutors'
    paginate_by = 10  # Number of tutors per page

    def get_queryset(self):
        """
        Get filtered, sorted, and searched queryset based on user input.
        """
        queryset = TutorProfile.objects.select_related('user')  # Select related fields to avoid N+1 queries

        # Extract filters and search parameters from the GET request
        search_query = self.request.GET.get('search', '')
        subjects_filter = self.request.GET.get('subjects', '')
        experience_filter = self.request.GET.get('experience_years', '')
        hourly_rate_filter = self.request.GET.get('hourly_rate', '')
        sort_by = self.request.GET.get('sort_by', 'user__first_name')  # Default sorting by first name

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(bio__icontains=search_query)
            )

        # Apply subject filter
        if subjects_filter:
            queryset = queryset.filter(subjects_expert_in__id=subjects_filter)

        # Apply experience filter
        if experience_filter:
            queryset = queryset.filter(experience_years__gte=experience_filter)  # Example for filtering by experience

        # Apply hourly rate filter
        if hourly_rate_filter:
            queryset = queryset.filter(hourly_rate__lte=hourly_rate_filter)  # Example for filtering by rate

        # Apply sorting
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pass subjects, filter values, and sorting options to context
        context['subjects'] = Subject.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_subject'] = self.request.GET.get('subjects', '')
        context['selected_experience'] = self.request.GET.get('experience_years', '')
        context['selected_hourly_rate'] = self.request.GET.get('hourly_rate', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'user__first_name')

        # Example subject choices for filtering (if you have predefined choices)
        context['experience_choices'] = range(1, 21)  # Example: Filter for 1 to 20 years of experience
        context['hourly_rate_choices'] = [50, 100, 150, 200]  # Example rate choices

        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Handle AJAX and standard HTTP responses.
        """
        # Check if the request is an AJAX request (e.g., the request is sent with 'XMLHttpRequest' header)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Render the partial template for AJAX response
            html = render_to_string('tutors/tutor_list_partial.html', context)
            return JsonResponse({'html': html})

        # Default behavior for standard HTTP requests (full page load)
        return super().render_to_response(context, **response_kwargs)
