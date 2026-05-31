from django.contrib import admin
from .models import Student, Subject, Marks, Prediction, WeakArea, Recommendation, AnalysisLog, ChatMessage


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'grade_level', 'school', 'created_at']
    list_filter = ['grade_level', 'learning_style', 'created_at']
    search_fields = ['name', 'email', 'roll_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'roll_number', 'phone')
        }),
        ('Academic Information', {
            'fields': ('grade_level', 'school')
        }),
        ('Profile', {
            'fields': ('profile_image', 'learning_style')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'color']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'marks_obtained', 'max_marks', 'percentage', 'exam_date']
    list_filter = ['exam_type', 'exam_date', 'subject']
    search_fields = ['student__name', 'subject__name']
    readonly_fields = ['percentage', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Student & Subject', {
            'fields': ('student', 'subject')
        }),
        ('Marks', {
            'fields': ('marks_obtained', 'max_marks', 'percentage')
        }),
        ('Exam Details', {
            'fields': ('exam_type', 'exam_date', 'topic', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'predicted_marks', 'confidence_score', 'prediction_for_date']
    list_filter = ['prediction_reason', 'prediction_for_date', 'model_name']
    search_fields = ['student__name', 'subject__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WeakArea)
class WeakAreaAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'current_percentage', 'severity', 'priority_rank']
    list_filter = ['severity', 'identified_at']
    search_fields = ['student__name', 'subject__name']
    readonly_fields = ['identified_at', 'updated_at']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'title', 'recommendation_type', 'is_active', 'completion_percentage']
    list_filter = ['recommendation_type', 'is_active', 'created_at']
    search_fields = ['student__name', 'subject__name', 'title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AnalysisLog)
class AnalysisLogAdmin(admin.ModelAdmin):
    list_display = ['student', 'agent_name', 'status', 'execution_time_seconds', 'started_at']
    list_filter = ['status', 'agent_name', 'started_at']
    search_fields = ['student__name']
    readonly_fields = [
        'input_data', 'output_data', 'started_at',
        'completed_at', 'error_message'
    ]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['student', 'role', 'created_at']
    list_filter = ['role', 'created_at', 'is_helpful']
    search_fields = ['student__name', 'content']
    readonly_fields = ['created_at']
