import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import qrcode
from django.db import transaction

from account.models import School


class Category(models.Model):
    """Model for storing categories for blogs and news articles."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Model for tagging blog posts and articles."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    """Model for storing blog posts."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blogs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='blogs')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='blogs', null=True, blank=True)
    image = models.ImageField(upload_to='blogs/images/', blank=True, null=True)

    def __str__(self):
        return self.title


class NewsArticle(models.Model):
    """Model for storing news articles."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_articles')
    published_date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='news_articles', null=True,
                                 blank=True)
    image = models.ImageField(upload_to='news/images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Model for storing comments on blog posts, news articles, and forum posts."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic foreign key for commenting on multiple types
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Comment by {self.user.first_name} on {self.content_object}"


class Review(models.Model):
    """Model for storing reviews for teachers and courses."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()  # For example, 1 to 5 stars
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.first_name} for {self.teacher.user.first_name}"


class TeacherProfile(models.Model):
    """Model for storing teacher profiles."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_teacher_profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='teachers/profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name}'s Profile"


class CommunityForum(models.Model):
    """Model for storing community forum posts by teachers."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forums')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ForumComment(models.Model):
    """Model for storing comments on community forum posts."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    forum = models.ForeignKey(CommunityForum, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.first_name} on {self.forum.title}"


class LessonPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    level = models.CharField(max_length=50)  # Junior Primary, Senior Primary, etc.
    area = models.CharField(max_length=50)  # Rural or Urban
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    follow_up_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.topic} ({self.level}, {self.area})"


class SummarizedContent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    original_content = models.TextField()
    summarized_content = models.TextField()
    content_html = models.TextField(null=True, blank=True)  # For rendering HTML version
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summarized content by {self.user.first_name} - {self.created_at}"


class CreativeWritingPrompt(models.Model):
    # User-related field
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Creative writing details
    GENRE_CHOICES = [
        ('adventure', 'Adventure'),
        ('mystery', 'Mystery'),
        ('historical', 'Historical Fiction'),
        ('fantasy', 'Fantasy'),
        ('realism', 'Realism'),
        ('comedy', 'Comedy'),
    ]

    TONE_CHOICES = [
        ('inspirational', 'Inspirational'),
        ('playful', 'Playful'),
        ('serious', 'Serious'),
        ('sad', 'Sad'),
        ('hopeful', 'Hopeful'),
    ]

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    LOCATION_CHOICES = [
        ('freetown', 'Freetown'),
        ('kenema', 'Kenema'),
        ('bo', 'Bo'),
        ('makeni', 'Makeni'),
        ('portloko', 'Port Loko'),
        ('kailahun', 'Kailahun'),
        ('other', 'Other'),
    ]

    # Updated fields with null and blank options
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, blank=True, null=True)
    tone = models.CharField(max_length=50, choices=TONE_CHOICES, blank=True, null=True)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, blank=True, null=True)
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='freetown', blank=True, null=True)

    # New fields
    theme = models.CharField(max_length=100, blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    idea = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)

    prompt = models.TextField(blank=False)  # Store the prompt as HTML (mandatory)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt for {self.genre or 'Unknown genre'} ({self.level or 'Unknown level'}) in {self.location or 'Unknown location'}"


class Media(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('youtube', 'YouTube Video'),
        ('document', 'Document'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=255)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image')
    file = models.FileField(upload_to='media/', blank=True, null=True)  # For images, videos, documents
    youtube_url = models.URLField(blank=True, null=True)  # For YouTube URLs
    description = models.TextField(blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='media')

    def __str__(self):
        return self.title

    @property
    def get_media_url(self):
        if self.media_type == 'youtube' and self.youtube_url:
            return self.youtube_url
        elif self.file:
            return self.file.url
        return None

    @property
    def get_embed_code(self):
        if self.media_type == 'youtube' and self.youtube_url:
            video_id = self.youtube_url.split("=")[1]
            return f'<iframe width="100%" height="500" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
        return None


class Facility(models.Model):
    """Model for school facilities"""

    FACILITY_TYPES = [
        ('library', 'Library'),
        ('science_lab', 'Science Lab'),
        ('computer_lab', 'Computer Lab'),
        ('sports_complex', 'Sports Complex'),
        ('auditorium', 'Auditorium'),
        ('cafeteria', 'Cafeteria'),
        ('clinic', 'Clinic'),
        ('playground', 'Playground'),
        ('art_room', 'Art Room'),
        ('music_room', 'Music Room'),
        ('other', 'Other'),  # Always include an 'Other' option
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='facilities')
    facility_type = models.CharField(max_length=50, choices=FACILITY_TYPES, default='other')
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class (e.g., fas fa-book-reader)")
    image = models.ImageField(upload_to='facility_images/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name



from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid

def validate_file_type(value):
    """Ensure only PDF or PNG files are uploaded."""
    allowed_types = ['application/pdf', 'image/png']
    if value.file.content_type not in allowed_types:
        raise ValidationError("Only PDF and PNG files are allowed.")

class ClassLevel(models.TextChoices):
    NURSERY_1 = 'Nursery 1', 'Nursery 1'
    NURSERY_2 = 'Nursery 2', 'Nursery 2'
    NURSERY_3 = 'Nursery 3', 'Nursery 3'
    CLASS_1 = 'Class 1', 'Class 1'
    CLASS_2 = 'Class 2', 'Class 2'
    CLASS_3 = 'Class 3', 'Class 3'
    CLASS_4 = 'Class 4', 'Class 4'
    CLASS_5 = 'Class 5', 'Class 5'
    CLASS_6 = 'Class 6', 'Class 6'
    JSS_1 = 'JSS 1', 'JSS 1'
    JSS_2 = 'JSS 2', 'JSS 2'
    JSS_3 = 'JSS 3', 'JSS 3'
    SS_1 = 'SS 1', 'SS 1'
    SS_2 = 'SS 2', 'SS 2'
    SS_3 = 'SS 3', 'SS 3'


class ApplicationStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    ACCEPTED = 'Accepted', 'Accepted'
    REJECTED = 'Rejected', 'Rejected'


import qrcode
from io import BytesIO
from django.core.files import File
from django.utils.crypto import get_random_string
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.template.defaultfilters import slugify

class Application(models.Model):
    SCHOOL_LEVELS = [
        ('nursery', 'Nursery'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    school_level = models.CharField(max_length=20, choices=SCHOOL_LEVELS)
    class_level = models.CharField(max_length=20, choices=ClassLevel.choices)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_contact = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(max_length=200, null=True, blank=True)
    previous_school = models.CharField(max_length=200, null=True, blank=True)
    previous_result = models.FileField(upload_to='previous_results/', null=True, blank=True)
    applicant_image = models.ImageField(upload_to='applicant_images/', null=True, blank=True)
    application_status = models.CharField(max_length=20, choices=ApplicationStatus.choices,
                                          default=ApplicationStatus.PENDING)
    application_code = models.CharField(max_length=10, unique=True, editable=False)
    application_date = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='application_qr_codes/', blank=True, null=True)


    # def save(self, *args, **kwargs):
    #     if not self.application_code:
    #         self.application_code = self.generate_unique_application_code()
    #         print(f"Generated application_code: {self.application_code}")
    #     if not self.qr_code:
    #         qr_code_file = self.generate_qr_code()
    #         qr_code_file.seek(0)
    #         self.qr_code.save(f'{self.application_code}_qr_code.png', qr_code_file)
    #         print(f"Generated QR Code for {self.application_code}")
    #
    #     super().save(*args, **kwargs)
    #
    # def generate_unique_application_code(self):
    #     """Generate a unique 10-character alphanumeric application code."""
    #     while True:
    #         code = get_random_string(length=10, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    #         if not Application.objects.filter(application_code=code).exists():
    #             return code
    #
    # def generate_qr_code(self):
    #     """Generate a QR code for the application."""
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(self.get_application_url())
    #     qr.make(fit=True)
    #     img = qr.make_image(fill='black', back_color='white')
    #     buffer = BytesIO()
    #     img.save(buffer, 'PNG')
    #     buffer.seek(0)
    #     # Debugging
    #     print(f"Generated QR Code for {self.application_code}")
    #     return File(buffer, name=f'{self.application_code}_qr_code.png')
    #
    # def get_application_url(self):
    #     """Generate a URL for the application page."""
    #     return f'https://yourwebsite.com/application/{self.application_code}/'
    #
    # def __str__(self):
    #     return f"{self.first_name} {self.last_name} - {self.school} ({self.get_class_level_display()})"
    def generate_unique_application_code(self):
        """Generate a unique 10-character alphanumeric application code."""
        while True:
            code = get_random_string(length=10, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            if not Application.objects.filter(application_code=code).exists():
                return code

    def generate_qr_code(self):
        """Generate a QR code for the application."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        return File(buffer, name=f'{self.application_code}_qr_code.png')

    def save(self, *args, **kwargs):
        # Generate application_code if it's not set
        if not self.application_code:
            self.application_code = self.generate_unique_application_code()

        # Generate QR code if not set
        if not self.qr_code:
            qr_code_file = self.generate_qr_code()
            self.qr_code.save(f'{self.application_code}_qr_code.png', qr_code_file, save=False)

        # Save the object (including the qr_code field, if it's been set)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.school} ({self.get_class_level_display()})"