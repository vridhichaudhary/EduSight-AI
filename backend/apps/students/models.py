from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Student(models.Model):
    """
    Represents a student in the system.
    Stores basic student information.
    """
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        help_text="Full name of the student"
    )
    email = models.EmailField(
        unique=True,
        help_text="Student email address (must be unique)"
    )
    roll_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Student roll number or ID"
    )
    phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="Contact number"
    )
    
    # Academic Information
    grade_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Grade/Class level (1-12)"
    )
    school = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="School/Institution name"
    )
    
    # Profile Information
    profile_image = models.ImageField(
        upload_to='student_profiles/',
        null=True,
        blank=True,
        help_text="Student profile picture"
    )
    learning_style = models.CharField(
        max_length=50,
        choices=[
            ('visual', 'Visual Learner'),
            ('auditory', 'Auditory Learner'),
            ('kinesthetic', 'Kinesthetic Learner'),
            ('reading_writing', 'Reading/Writing Learner'),
            ('mixed', 'Mixed Learning Style'),
        ],
        default='mixed',
        help_text="Preferred learning style"
    )
    
    # Time Tracking
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When student was added to system"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When student info was last updated"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['roll_number']),
            models.Index(fields=['grade_level']),
        ]
        verbose_name = "Student"
        verbose_name_plural = "Students"
    
    def __str__(self):
        return f"{self.name} (Grade {self.grade_level})"
    
    def get_latest_marks(self):
        """Get the 5 most recent mark entries"""
        return self.marks_set.all()[:5]
    
    def get_average_percentage(self):
        """Calculate overall average percentage across all marks"""
        marks = self.marks_set.all()
        if not marks:
            return 0
        total_percentage = sum([m.percentage for m in marks])
        return total_percentage / len(marks)
    
    def get_weak_subjects(self):
        """Get list of subjects below class average"""
        return self.weakarea_set.all()[:5]

class Subject(models.Model):
    """
    Represents an academic subject.
    Used to categorize marks and recommendations.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Subject name (e.g., Mathematics, Physics)"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Subject code (e.g., MATH101)"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Description of the subject"
    )
    icon = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Icon name for UI display"
    )
    color = models.CharField(
        max_length=7,
        default='#0ea5e9',
        help_text="Hex color code for visualizations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Marks(models.Model):
    """
    Represents a student's marks/scores in an exam or assessment.
    This is the raw data that gets analyzed by AI agents.
    """
    
    EXAM_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('midterm', 'Midterm'),
        ('final', 'Final Exam'),
        ('assignment', 'Assignment'),
        ('practical', 'Practical'),
        ('project', 'Project'),
    ]
    
    # Relationships
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='marks_set',
        help_text="Student who took the exam"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='marks',
        help_text="Subject of the exam"
    )
    
    # Mark Information
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Marks obtained by student"
    )
    max_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total marks for the exam"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        editable=False,
        help_text="Percentage (auto-calculated)"
    )
    
    # Exam Details
    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES,
        default='quiz',
        help_text="Type of assessment"
    )
    exam_date = models.DateField(
        help_text="Date when exam was conducted"
    )
    
    # Additional Info
    topic = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Specific topic/chapter for this exam"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Teacher comments or notes"
    )
    
    # Time Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-exam_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['exam_date']),
            models.Index(fields=['exam_type']),
        ]
        verbose_name = "Mark Entry"
        verbose_name_plural = "Mark Entries"
        unique_together = [['student', 'subject', 'exam_type', 'exam_date']]
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.name}: {self.percentage}% ({self.exam_date})"
    
    def save(self, *args, **kwargs):
        """Calculate percentage before saving"""
        if self.max_marks > 0:
            self.percentage = (self.marks_obtained / self.max_marks) * 100
        super().save(*args, **kwargs)
    
    def is_weak(self, class_average=70):
        """Check if mark is below expected level"""
        return self.percentage < class_average
    
    def get_grade(self):
        """Return letter grade based on percentage"""
        percentage = float(self.percentage)
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

class Prediction(models.Model):
    """
    Stores AI-generated predictions for student performance.
    Created by ML models in the analysis pipeline.
    """
    
    # Relationships
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text="Student for whom prediction is made"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text="Subject being predicted"
    )
    
    # Prediction Data
    predicted_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Predicted percentage for next exam"
    )
    predicted_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Predicted actual score (if max_marks known)"
    )
    
    # Confidence Metrics
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        default=0.85,
        help_text="Model confidence (0-1, where 1 is 100% confident)"
    )
    lower_bound = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Lower confidence interval bound"
    )
    upper_bound = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Upper confidence interval bound"
    )
    
    # Prediction Timing
    prediction_for_date = models.DateField(
        help_text="Date for which prediction is made"
    )
    prediction_reason = models.CharField(
        max_length=50,
        choices=[
            ('semester', 'Semester Prediction'),
            ('next_exam', 'Next Exam Prediction'),
            ('annual', 'Annual Prediction'),
            ('custom', 'Custom Prediction'),
        ],
        default='next_exam',
        help_text="Type of prediction"
    )
    
    # Model Info
    model_name = models.CharField(
        max_length=100,
        default='XGBoost',
        help_text="Which ML model made this prediction"
    )
    model_version = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Version of the model"
    )
    features_used = models.JSONField(
        null=True,
        blank=True,
        help_text="Features used for prediction"
    )
    
    # Time Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-prediction_for_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['prediction_for_date']),
        ]
        verbose_name = "Prediction"
        verbose_name_plural = "Predictions"
    
    def __str__(self):
        return f"Prediction: {self.student.name} - {self.subject.name}: {self.predicted_marks}%"
    
    def get_prediction_interval(self):
        """Return confidence interval as tuple"""
        return (self.lower_bound, self.upper_bound)
    
    def is_at_risk(self, threshold=60):
        """Check if predicted score is below passing threshold"""
        return self.predicted_marks < threshold

class WeakArea(models.Model):
    """
    Identifies subjects/areas where student is weak.
    Created by analysis agents to highlight improvement opportunities.
    """
    
    SEVERITY_CHOICES = [
        ('critical', 'Critical - Below 40%'),
        ('severe', 'Severe - 40-50%'),
        ('moderate', 'Moderate - 50-60%'),
        ('mild', 'Mild - 60-70%'),
        ('warning', 'Warning - Close attention needed'),
    ]
    
    # Relationships
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='weakarea_set',
        help_text="Student with weak area"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='weakareas',
        help_text="Subject identified as weak"
    )
    
    # Analysis Data
    current_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Current average percentage in this subject"
    )
    class_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Class average for comparison"
    )
    gap_from_target = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="How many points below target performance"
    )
    
    # Severity & Priority
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='moderate',
        help_text="How critical this weak area is"
    )
    priority_rank = models.IntegerField(
        default=0,
        help_text="Ranking among student's weak areas (lower = higher priority)"
    )
    
    # Reason & Analysis
    reason = models.TextField(
        null=True,
        blank=True,
        help_text="Why this area is weak (from AI analysis)"
    )
    improvement_potential = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        help_text="Estimated percentage improvement possible"
    )
    
    # Tracking
    identified_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority_rank', '-identified_at']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['severity']),
        ]
        verbose_name = "Weak Area"
        verbose_name_plural = "Weak Areas"
        unique_together = [['student', 'subject']]
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.name}: {self.severity}"
    
    def get_color_code(self):
        """Return color for UI visualization"""
        colors = {
            'critical': '#ef4444',      # Red
            'severe': '#f97316',        # Orange
            'moderate': '#eab308',      # Yellow
            'mild': '#22c55e',          # Green
            'warning': '#f59e0b',       # Amber
        }
        return colors.get(self.severity, '#gray')

class Recommendation(models.Model):
    """
    Stores personalized study recommendations and resources.
    Generated by RAG system based on weak areas.
    """
    
    RESOURCE_TYPE_CHOICES = [
        ('video', 'Video Tutorial'),
        ('article', 'Article/Blog'),
        ('practice', 'Practice Problems'),
        ('book', 'Book Chapter'),
        ('interactive', 'Interactive Tool'),
        ('quiz', 'Practice Quiz'),
        ('podcast', 'Podcast'),
    ]
    
    # Relationships
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='recommendations',
        help_text="Student receiving recommendation"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='recommendations',
        help_text="Subject for this recommendation"
    )
    weak_area = models.ForeignKey(
        WeakArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommendations',
        help_text="Related weak area (if applicable)"
    )
    
    # Recommendation Content
    title = models.CharField(
        max_length=300,
        help_text="Title of recommendation"
    )
    description = models.TextField(
        help_text="Detailed description of recommendation"
    )
    recommendation_type = models.CharField(
        max_length=50,
        choices=RESOURCE_TYPE_CHOICES,
        default='practice',
        help_text="Type of study resource"
    )
    
    # Study Plan
    topics_to_study = models.JSONField(
        default=list,
        help_text="List of topics to focus on: ['Topic 1', 'Topic 2']"
    )
    study_hours_suggested = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Suggested hours per week"
    )
    study_frequency = models.CharField(
        max_length=50,
        choices=[
            ('daily', 'Daily'),
            ('3x_per_week', '3 times per week'),
            ('2x_per_week', '2 times per week'),
            ('weekly', 'Weekly'),
        ],
        default='3x_per_week',
        help_text="How often to study this"
    )
    
    # Resources
    resources = models.JSONField(
        default=list,
        help_text="""
        List of resources: 
        [
            {
                'title': 'Khan Academy: Linear Equations',
                'type': 'video',
                'url': 'https://...',
                'difficulty': 'beginner'
            }
        ]
        """
    )
    
    # AI Generation Info
    generated_by_agent = models.CharField(
        max_length=100,
        default='RecommendationEngine',
        help_text="Which AI agent generated this"
    )
    rag_query = models.TextField(
        null=True,
        blank=True,
        help_text="RAG query used to retrieve resources"
    )
    
    # Status Tracking
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this recommendation is currently active"
    )
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How much of recommendation student has completed"
    )
    
    # Time Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = "Recommendation"
        verbose_name_plural = "Recommendations"
    
    def __str__(self):
        return f"Recommendation: {self.student.name} - {self.title}"
    
    def mark_completed(self):
        """Mark recommendation as completed"""
        self.completion_percentage = 100
        self.save()
    
    def get_resource_count(self):
        """Count number of resources in this recommendation"""
        return len(self.resources)

class AnalysisLog(models.Model):
    """
    Logs AI agent execution for debugging and auditing.
    Tracks what each agent does with student data.
    """
    
    AGENT_CHOICES = [
        ('pattern_discovery', 'Pattern Discovery Agent'),
        ('predictor', 'Predictive Analytics Agent'),
        ('weak_area', 'Weak Area Identification Agent'),
        ('recommender', 'Recommendation Engine Agent'),
        ('supervisor', 'Supervisor Agent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Relationships
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='analysis_logs',
        help_text="Student being analyzed"
    )
    
    # Agent Info
    agent_name = models.CharField(
        max_length=50,
        choices=AGENT_CHOICES,
        help_text="Which agent ran this analysis"
    )
    
    # Execution Details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of analysis"
    )
    input_data = models.JSONField(
        help_text="Input data provided to agent"
    )
    output_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Output produced by agent"
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if execution failed"
    )
    
    # Performance Metrics
    execution_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="How long agent took to run"
    )
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="LLM tokens used (for cost tracking)"
    )
    
    # Time Tracking
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When agent finished execution"
    )
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['student', 'agent_name']),
            models.Index(fields=['status']),
        ]
        verbose_name = "Analysis Log"
        verbose_name_plural = "Analysis Logs"
    
    def __str__(self):
        return f"{self.agent_name} - {self.student.name}: {self.status}"
    
    def mark_completed(self, output_data, execution_time):
        """Mark analysis as completed"""
        self.status = 'completed'
        self.output_data = output_data
        self.execution_time_seconds = execution_time
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """Mark analysis as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()

class ChatMessage(models.Model):
    """
    Stores chat messages for conversational AI interface.
    Allows students to ask questions about their performance.
    """
    
    ROLE_CHOICES = [
        ('user', 'User Question'),
        ('assistant', 'AI Response'),
        ('system', 'System Message'),
    ]
    
    # Relationships
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        help_text="Student in conversation"
    )
    
    # Message Content
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text="Who sent this message"
    )
    content = models.TextField(
        help_text="Message text"
    )
    
    # Context
    context_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Reference data used to answer (marks, predictions, etc.)"
    )
    sources = models.JSONField(
        default=list,
        help_text="Sources used for this response"
    )
    
    # Metadata
    is_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="User feedback on response quality"
    )
    
    # Time Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['student', 'created_at']),
        ]
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
    
    def __str__(self):
        return f"{self.student.name} - {self.role}: {self.content[:50]}"
    
    def get_conversation_context(self, limit=10):
        """Get last N messages for conversation context"""
        return self.student.chat_messages.order_by('-created_at')[:limit]
