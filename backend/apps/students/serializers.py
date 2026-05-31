from rest_framework import serializers
from .models import Student, Subject, Marks, Prediction, WeakArea, Recommendation, AnalysisLog, ChatMessage


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'icon', 'color']


class StudentSerializer(serializers.ModelSerializer):
    average_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'name', 'email', 'roll_number', 'phone',
            'grade_level', 'school', 'learning_style',
            'profile_image', 'average_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'average_percentage']
    
    def get_average_percentage(self, obj):
        return obj.get_average_percentage()


class MarksSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Marks
        fields = [
            'id', 'student', 'subject', 'subject_name',
            'marks_obtained', 'max_marks', 'percentage', 'grade',
            'exam_type', 'exam_date', 'topic', 'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'percentage', 'created_at']
    
    def get_grade(self, obj):
        return obj.get_grade()


class PredictionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    is_at_risk = serializers.SerializerMethodField()
    
    class Meta:
        model = Prediction
        fields = [
            'id', 'student', 'subject', 'subject_name',
            'predicted_marks', 'confidence_score',
            'lower_bound', 'upper_bound',
            'prediction_for_date', 'prediction_reason',
            'model_name', 'is_at_risk',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_is_at_risk(self, obj):
        return obj.is_at_risk()


class WeakAreaSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    color_code = serializers.SerializerMethodField()
    
    class Meta:
        model = WeakArea
        fields = [
            'id', 'student', 'subject', 'subject_name',
            'current_percentage', 'class_average', 'gap_from_target',
            'severity', 'priority_rank', 'reason',
            'improvement_potential', 'color_code',
            'identified_at'
        ]
        read_only_fields = ['id', 'identified_at']
    
    def get_color_code(self, obj):
        return obj.get_color_code()


class RecommendationSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    resource_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'student', 'subject', 'subject_name',
            'title', 'description', 'recommendation_type',
            'topics_to_study', 'study_hours_suggested',
            'study_frequency', 'resources', 'resource_count',
            'generated_by_agent', 'is_active',
            'completion_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'resource_count']
    
    def get_resource_count(self, obj):
        return obj.get_resource_count()


class AnalysisLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisLog
        fields = [
            'id', 'student', 'agent_name', 'status',
            'input_data', 'output_data', 'error_message',
            'execution_time_seconds', 'tokens_used',
            'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'input_data', 'output_data',
            'started_at', 'completed_at'
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'student', 'role', 'content',
            'context_data', 'sources', 'is_helpful',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
