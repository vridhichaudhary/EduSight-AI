from django.core.management.base import BaseCommand
from apps.students.models import Student, Subject, Marks
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Seeds the database with a robust Demo Student with realistic marks data.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Demo Student...')
        
        # 1. Create or get Demo Student
        student, created = Student.objects.get_or_create(
            name="Demo Student",
            defaults={
                'email': "demo.student@edusight.ai",
                'grade_level': 10
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created student: {student.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Student {student.name} already exists. Appending data...'))

        # 2. Create standard subjects
        subjects = {
            'Mathematics': 'MAT101',
            'Physics': 'PHY101',
            'Chemistry': 'CHE101',
            'English': 'ENG101',
            'History': 'HIS101'
        }
        
        subject_objs = {}
        for name, code in subjects.items():
            subj, _ = Subject.objects.get_or_create(name=name, defaults={'code': code})
            subject_objs[name] = subj

        # 3. Generate realistic data
        # Let's say exams happen every month for the last 6 months
        # Base scores: Math (struggling but improving), Physics (steady), English (strong), History (weak)
        
        base_scores = {
            'Mathematics': 55, # starts low, goes up
            'Physics': 75,     # steady
            'Chemistry': 65,   # fluctuates
            'English': 88,     # strong
            'History': 45      # weak
        }
        
        exam_types = ['quiz', 'assignment', 'midterm', 'practical', 'final']
        
        marks_created = 0
        today = timezone.now().date()
        
        for month_offset in range(6, -1, -1):
            exam_date = today - timedelta(days=30 * month_offset)
            
            for subject_name, base_score in base_scores.items():
                # Add some random noise to the score
                noise = random.randint(-8, 8)
                
                # Apply trend
                if subject_name == 'Mathematics':
                    trend = (6 - month_offset) * 4  # Improves by 4 points every month
                elif subject_name == 'History':
                    trend = (6 - month_offset) * -2 # Declines slightly
                else:
                    trend = 0
                
                final_score = min(100, max(0, base_score + noise + trend))
                
                # Pick a random exam type
                e_type = random.choice(exam_types)
                if month_offset == 3: e_type = 'midterm'
                if month_offset == 0: e_type = 'final'
                
                Marks.objects.create(
                    student=student,
                    subject=subject_objs[subject_name],
                    marks_obtained=final_score,
                    max_marks=100,
                    exam_type=e_type,
                    exam_date=exam_date
                )
                marks_created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {marks_created} marks for {student.name}!'))
        self.stdout.write(self.style.SUCCESS('You can now view this student in the dashboard and run the ML Analysis.'))
