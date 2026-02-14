import uuid
from io import BytesIO
import qrcode
from django.core.files import File
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings
import qrcode


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('guardian', 'Guardian'),
    ]
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    objects = CustomUserManager()


class District(models.Model):
    REGION_CHOICES = [
        ('Eastern', 'Eastern'),
        ('Northern', 'Northern'),
        ('Southern', 'Southern'),
        ('Western', 'Western'),
    ]

    name = models.CharField(max_length=200, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True, help_text="Brief description of the district.")
    region = models.CharField(max_length=20, choices=REGION_CHOICES, db_index=True)
    population = models.IntegerField(null=True, blank=True, help_text="Population of the district.")
    literacy_rate = models.FloatField(null=True, blank=True, help_text="Literacy rate in percentage.")
    land_area_km2 = models.FloatField(null=True, blank=True, help_text="Total land area in square kilometers.")
    contact_number = models.CharField(max_length=15, blank=True, null=True, help_text="District office contact number.")
    official_email = models.EmailField(blank=True, null=True, help_text="Official email of the district office.")
    website = models.URLField(blank=True, null=True, help_text="Official district website.")

    def __str__(self):
        return f"{self.name} ({self.region})"
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class School(models.Model):
    SCHOOL_TYPE_CHOICES = [
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
        ('Vocational', 'Vocational'),
    ]
    OWNERSHIP_CHOICES = [
        ('Private', 'Private'),
        ('Government', 'Government'),
    ]

    # Existing fields
    name = models.CharField(max_length=200, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    total_enrollment = models.IntegerField(null=True, blank=True, db_index=True)
    teacher_to_student_ratio = models.FloatField(null=True, blank=True, db_index=True)
    number_of_classrooms = models.IntegerField(null=True, blank=True, db_index=True)
    number_of_teachers = models.IntegerField(null=True, blank=True)
    average_years_of_experience = models.FloatField(null=True, blank=True)
    percentage_of_qualified_teachers = models.FloatField(null=True, blank=True)
    school_admin = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account_school',
        null=True, blank=True
    )
    number_of_subjects_offered = models.IntegerField(null=True, blank=True)
    school_type = models.CharField(max_length=50, choices=SCHOOL_TYPE_CHOICES, db_index=True)
    facilities_summary = models.TextField(
        blank=True, help_text="Summary of key facilities (e.g., library, labs, sports fields)."
    )
    subjects = models.ManyToManyField(
        Subject, related_name='subjects', blank=True, help_text="Subjects the teacher is proficient in."
    )
    total_facilities = models.IntegerField(null=True, blank=True)
    extra_curricular_activities = models.TextField(
        blank=True, help_text="Details of extracurricular activities offered by the school."
    )
    performance_metrics = models.JSONField(
        default=dict, blank=True, help_text="Key performance indicators (e.g., exam pass rates).", db_index=True
    )
    community_engagement = models.TextField(
        blank=True, help_text="Details about community involvement and initiatives."
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    established_year = models.DateField(null=True, blank=True, db_index=True)
    contact_number = models.CharField(
        max_length=15, blank=True, null=True, help_text="Contact number for the school."
    )
    email_address = models.EmailField(
        blank=True, null=True, help_text="Official email address of the school."
    )
    website = models.URLField(
        blank=True, null=True, help_text="School's official website."
    )
    school_motto = models.CharField(
        max_length=255, blank=True, null=True, help_text="The motto or mission statement of the school."
    )
    qr_code = models.ImageField(upload_to='school_qrcodes/', blank=True, null=True)
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_CHOICES, null=True, blank=True, db_index=True)

    # New fields
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='schools')
    school_certificates = models.TextField(
        blank=True, null=True, help_text="Certificates offered (e.g., WASSCE, BECE, NPSE)."
    )
    is_governmental_approved = models.BooleanField(default=False, help_text="Is the school approved by the government?")
    take_wassce = models.BooleanField(default=False, help_text="Does the school participate in WASSCE exams?")
    take_bece = models.BooleanField(default=False, help_text="Does the school participate in BECE exams?")
    take_npse = models.BooleanField(default=False, help_text="Does the school participate in NPSE exams?")

    def __str__(self):
        return self.name

    def generate_qr_code(self):
        """Generate a QR code dynamically with school information."""
        qr_data = (
            f"School: {self.name}, "
            f"Type: {self.get_school_type_display()}, "
            f"District: {self.district.name if self.district else 'N/A'}, "
            f"Contact: {self.contact_number or 'N/A'}, "
            f"Email: {self.email_address or 'N/A'}, "
            f"Website: {self.website or 'N/A'}, "
            f"Established: {self.established_year or 'N/A'}"
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        filename = f"{self.name.replace(' ', '_')}_qr_code.png"
        self.qr_code.save(filename, File(buffer), save=False)

    def save(self, *args, **kwargs):
        """Override save to ensure QR code is generated."""
        self.generate_qr_code()
        super().save(*args, **kwargs)




class TeacherProfile(models.Model):
    TEACHER_STATUS_CHOICES = [
        ('private', 'Private'),
        ('government', 'Government'),
    ]

    CERTIFICATION_CHOICES = [
        ('GR', 'Graduate Teacher'),
        ('HTC', 'Higher Teacher’s Certificate'),
        ('PTC', 'Primary Teacher’s Certificate'),
        ('STC', 'Secondary Teacher’s Certificate'),
    ]

    SPECIALIZATION_CHOICES = [
        ('STEM', 'Science/STEM'),
        ('Arts', 'Arts'),
        ('Business', 'Business/Commercial'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account_teacher_profile'
    )
    school = models.ForeignKey(
        School, on_delete=models.SET_NULL, null=True, related_name='teachers'
    )
    subjects = models.ManyToManyField(
        Subject, related_name='teachers', blank=True, help_text="Subjects the teacher is proficient in."
    )
    favorite_subjects = models.CharField(
        max_length=255, blank=True, null=True, help_text="Comma-separated list of favorite subjects."
    )
    years_of_experience = models.IntegerField(blank=True, null=True)
    certifications = models.CharField(
        max_length=20, choices=CERTIFICATION_CHOICES, blank=True, null=True, help_text="Highest certification obtained."
    )
    specialization = models.CharField(
        max_length=20, choices=SPECIALIZATION_CHOICES, blank=True, null=True, help_text="Teacher's specialization area."
    )
    bio = models.TextField(blank=True, null=True)
    teacher_status = models.CharField(
        max_length=20, choices=TEACHER_STATUS_CHOICES, default='private'
    )
    government_pin_code = models.CharField(max_length=10, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    awards_and_recognitions = models.TextField(
        blank=True, null=True, help_text="Details of awards or recognitions received."
    )
    contact_number = models.CharField(
        max_length=15, blank=True, null=True, help_text="Teacher’s contact number."
    )
    additional_languages = models.CharField(
        max_length=255, blank=True, null=True, help_text="Languages spoken other than English."
    )
    teaching_philosophy = models.TextField(
        blank=True, null=True, help_text="Brief description of the teacher's philosophy or approach."
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def generate_qr_code(self):
        """Generate a QR code dynamically with teacher information."""
        # Fetch all associated subjects
        subjects_list = ", ".join(subject.name for subject in self.subjects.all())
        qr_data = (
            f"Teacher: {self.user.first_name} {self.user.last_name}, "
            f"Email: {self.user.email}, "
            f"School: {self.school.name if self.school else 'N/A'}, "
            f"Subjects: {subjects_list if subjects_list else 'None'}, "
            f"Favorite Subjects: {self.favorite_subjects or 'None'}, "
            f"Certification: {self.get_certifications_display() if self.certifications else 'None'}, "
            f"Specialization: {self.get_specialization_display() if self.specialization else 'None'}, "
            f"Years of Experience: {self.years_of_experience or 'N/A'}"
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)

        return File(buffer, name=f'{self.user.email}_qr_code.png')


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, related_name='students')
    grade = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    guardian = models.ForeignKey('GuardianProfile', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='students')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def generate_qr_code(self):
        """Generate a QR code for the student."""
        qr_data = f"Student: {self.user.first_name} {self.user.last_name}, Email: {self.user.email}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)

        return File(buffer, name=f'{self.user.email}_qr_code.png')


class GuardianProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    relationship_to_student = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class TutorProfile(models.Model):
    SPECIALIZATION_CHOICES = [
        ('STEM', 'Science/STEM'),
        ('Arts', 'Arts'),
        ('Business', 'Business/Commercial'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subjects_expert_in = models.ManyToManyField(Subject, blank=True, related_name='tutors')
    experience_years = models.IntegerField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)  # Rating out of 5

    # Education Fields
    highest_education = models.CharField(max_length=255, blank=True, null=True)
    institution_name = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    degree_type = models.CharField(max_length=255, blank=True, null=True)
    specialization = models.CharField(
        max_length=20, choices=SPECIALIZATION_CHOICES, blank=True, null=True, help_text="Teacher's specialization area."
    )

    # Certificates Fields
    certifications = models.TextField(blank=True, null=True)  # A text field for listing certifications

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def update_rating(self):
        # Assuming ratings are stored in a related Review model
        reviews = self.reviews.all()
        if reviews:
            self.rating = sum([review.rating for review in reviews]) / len(reviews)
            self.save()


class TutorRequest(models.Model):
    PENDING = 'P'
    ACCEPTED = 'A'
    COMPLETED = 'C'
    CANCELLED = 'X'
    REQUEST_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='tutor_requests')
    requested_tutor = models.ForeignKey(TutorProfile, on_delete=models.SET_NULL, null=True,
                                        related_name='tutor_requests')
    request_date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=REQUEST_STATUS_CHOICES, default=PENDING)
    preferred_time = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # E.g., Online, in-person
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True,
                                related_name='tutor_requests')  # Linking to Subject
    deadline = models.DateTimeField(blank=True, null=True)  # When the request should be completed by
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True,
                                 null=True)  # Rating for the tutor once the request is completed

    def __str__(self):
        return f"Request by {self.student.user.first_name} for tutor {self.requested_tutor.user.first_name}"




class ContentCreationRequest(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='content_requests')
    content_type = models.CharField(max_length=100, choices=[
        ('lesson_plan', 'Lesson Plan'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ])
    description = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    ai_generated_content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Content request by {self.teacher.user.first_name} for {self.content_type}"
