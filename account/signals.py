from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, TeacherProfile, StudentProfile, GuardianProfile, TutorProfile


@receiver(post_save, sender=CustomUser)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:  # Only create profiles when the user is created
        if instance.role == 'teacher':
            TeacherProfile.objects.get_or_create(user=instance)
        elif instance.role == 'student':
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.role == 'guardian':
            GuardianProfile.objects.get_or_create(user=instance)
        elif instance.role == 'tutor':
            TutorProfile.objects.get_or_create(user=instance)

    # Save the profile after ensuring it exists
    try:
        if instance.role == 'teacher':
            instance.teacherprofile.save()
        elif instance.role == 'student':
            instance.studentprofile.save()
        elif instance.role == 'guardian':
            instance.guardianprofile.save()
        elif instance.role == 'tutor':
            instance.tutorprofile.save()
    except (
    TeacherProfile.DoesNotExist, StudentProfile.DoesNotExist, GuardianProfile.DoesNotExist, TutorProfile.DoesNotExist):
        # Handle case where profile does not exist
        pass
