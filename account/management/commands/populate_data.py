import random  
from django.core.management.base import BaseCommand  
from django.contrib.auth.hashers import make_password  
from account.models import *

class Command(BaseCommand):  
    help = 'Populate the database with data'  

    def handle(self, *args, **options):  
        self.populate_schools()  
        self.populate_users()  
        self.populate_teacher_profiles()  
        self.populate_guardian_profiles()  
        self.populate_student_profiles()  
        self.populate_tutor_profiles()  

    def populate_schools(self):  
        schools = [  
            {'name': 'Sahid Kanu Memorial School', 'school_type': 'Secondary'},  
            {'name': 'Makeni Secondary School', 'school_type': 'Secondary'},  
            {'name': 'Ahmed Kanu Memorial School', 'school_type': 'Primary'},  
        ]  

        for school in schools:  
            School.objects.create(**school)  

        self.stdout.write(self.style.SUCCESS('Successfully populated schools'))  

    def populate_users(self):  
        users = [  
            {'email': 'teacher1@example.com', 'first_name': 'John', 'last_name': 'Doe', 'role': 'teacher'},  
            {'email': 'teacher2@example.com', 'first_name': 'Jane', 'last_name': 'Doe', 'role': 'teacher'},  
            {'email': 'student1@example.com', 'first_name': 'Bob', 'last_name': 'Smith', 'role': 'student'},  
            {'email': 'student2@example.com', 'first_name': 'Alice', 'last_name': 'Johnson', 'role': 'student'},  
            {'email': 'guardian1@example.com', 'first_name': 'Mike', 'last_name': 'Williams', 'role': 'guardian'},  
            {'email': 'tutor1@example.com', 'first_name': 'Emma', 'last_name': 'Taylor', 'role': 'tutor'},  
        ]  

        for user in users:  
            CustomUser.objects.create(  
                email=user['email'],  
                first_name=user['first_name'],  
                last_name=user['last_name'],  
                role=user['role'],  
                password=make_password('password123'),  
            )  

        self.stdout.write(self.style.SUCCESS('Successfully populated users'))  

    def populate_teacher_profiles(self):  
        teachers = [  
            {'user': CustomUser.objects.get(email='teacher1@example.com'), 'school': School.objects.first()},  
            {'user': CustomUser.objects.get(email='teacher2@example.com'), 'school': School.objects.last()},  
        ]  

        for teacher in teachers:  
            teacher['subjects_taught'] = random.choice(['Mathematics', 'Science', 'English'])  
            teacher['bio'] = f"{teacher['user'].first_name} {teacher['user'].last_name} is a highly experienced teacher."  
            TeacherProfile.objects.create(**teacher)  

        self.stdout.write(self.style.SUCCESS('Successfully populated teacher profiles'))  

    def populate_guardian_profiles(self):  
        guardians = [  
            {'user': CustomUser.objects.get(email='guardian1@example.com'), 'relationship_to_student': 'Parent'},  
        ]  

        for guardian in guardians:  
            guardian['phone_number'] = f'{random.randint(1000000000, 9999999999)}'  
            GuardianProfile.objects.create(**guardian)  

        self.stdout.write(self.style.SUCCESS('Successfully populated guardian profiles'))  

    def populate_student_profiles(self):  
        students = [  
            {'user': CustomUser.objects.get(email='student1@example.com'), 'school': School.objects.first(), 'grade': 'JSS1'},  
            {'user': CustomUser.objects.get(email='student2@example.com'), 'school': School.objects.last(), 'grade': 'SSS1'},  
        ]  

        for student in students:  
            student['date_of_birth'] = f'{random.randint(1995, 2005)}-01-01'  
            student['guardian'] = GuardianProfile.objects.first()  
            StudentProfile.objects.create(**student)  

        self.stdout.write(self.style.SUCCESS('Successfully populated student profiles'))  

    def populate_tutor_profiles(self):  
        tutors = [  
            {'user': CustomUser.objects.get(email='tutor1@example.com')},  
        ]  

        for tutor in tutors:  
            tutor['subjects_expert_in'] = random.choice(['Mathematics', 'Science', 'English'])  
            tutor['experience_years'] = random.randint(1, 10)  
            tutor['hourly_rate'] = random.randint(10, 50)  
            tutor['bio'] = f"{tutor['user'].first_name} {tutor['user'].last_name} is a highly experienced tutor."  
            TutorProfile.objects.create(**tutor)  

        self.stdout.write(self.style.SUCCESS('Successfully populated tutor profiles'))