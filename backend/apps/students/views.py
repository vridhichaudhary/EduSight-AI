"""
API Views for Student Performance Predictor.

Handles all HTTP requests for:
- Students (CRUD)
- Subjects (CRUD)
- Marks (CRUD + CSV upload)
- Dashboard data
- Analysis trigger
- Chat
"""

import logging
import pandas as pd
from io import StringIO

from django.shortcuts import get_object_or_404
from django.db.models import Avg, Max, Min, Count

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView

from .models import (
    Student, Subject, Marks,
    Prediction, WeakArea,
    Recommendation, AnalysisLog, ChatMessage
)
from .serializers import (
    StudentSerializer, SubjectSerializer, MarksSerializer,
    PredictionSerializer, WeakAreaSerializer,
    RecommendationSerializer, AnalysisLogSerializer,
    ChatMessageSerializer
)
from .utils import APIResponse

logger = logging.getLogger('apps.students')


# ─────────────────────────────────────────────
# STUDENT VIEWSET
# ─────────────────────────────────────────────
class StudentViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Students.

    GET    /api/students/              → List all students
    POST   /api/students/              → Create student
    GET    /api/students/{id}/         → Get student
    PUT    /api/students/{id}/         → Update student
    PATCH  /api/students/{id}/         → Partial update
    DELETE /api/students/{id}/         → Delete student
    GET    /api/students/{id}/summary/ → Student summary dashboard
    """

    queryset = Student.objects.all().order_by('-created_at')
    serializer_class = StudentSerializer
    search_fields = ['name', 'email', 'roll_number']
    ordering_fields = ['name', 'grade_level', 'created_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            grade = request.query_params.get('grade')
            if grade:
                queryset = queryset.filter(grade_level=grade)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return APIResponse.paginated(
                    data=serializer.data,
                    pagination_info={
                        'count': self.paginator.page.paginator.count,
                        'next': self.paginator.get_next_link(),
                        'previous': self.paginator.get_previous_link(),
                    }
                )

            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f'Found {len(serializer.data)} students'
            )
        except Exception as e:
            logger.error(f"Error listing students: {str(e)}")
            return APIResponse.error(message='Failed to fetch students', errors={'detail': str(e)})

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return APIResponse.validation_error(errors=serializer.errors, message='Student data is invalid')
            serializer.save()
            logger.info(f"Created student: {serializer.data['name']}")
            return APIResponse.created(
                data=serializer.data,
                message=f"Student '{serializer.data['name']}' created successfully"
            )
        except Exception as e:
            logger.error(f"Error creating student: {str(e)}")
            return APIResponse.error(message='Failed to create student', errors={'detail': str(e)})

    def retrieve(self, request, pk=None):
        try:
            student = get_object_or_404(Student, pk=pk)
            serializer = self.get_serializer(student)
            return APIResponse.success(data=serializer.data, message='Student retrieved successfully')
        except Exception:
            return APIResponse.not_found(message=f'Student with ID {pk} not found')

    def update(self, request, pk=None, *args, **kwargs):
        try:
            student = get_object_or_404(Student, pk=pk)
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(student, data=request.data, partial=partial)
            if not serializer.is_valid():
                return APIResponse.validation_error(errors=serializer.errors)
            serializer.save()
            return APIResponse.success(data=serializer.data, message='Student updated successfully')
        except Exception as e:
            logger.error(f"Error updating student {pk}: {str(e)}")
            return APIResponse.error(message='Failed to update student')

    def destroy(self, request, pk=None):
        try:
            student = get_object_or_404(Student, pk=pk)
            name = student.name
            student.delete()
            logger.info(f"Deleted student: {name}")
            return APIResponse.success(message=f"Student '{name}' deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting student {pk}: {str(e)}")
            return APIResponse.error(message='Failed to delete student')

    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self, request, pk=None):
        """
        GET /api/students/{id}/summary/
        Returns overall performance stats for the dashboard header.
        """
        try:
            student = get_object_or_404(Student, pk=pk)
            marks = Marks.objects.filter(student=student)

            if not marks.exists():
                return APIResponse.success(
                    data={
                        'student': StudentSerializer(student).data,
                        'total_exams': 0,
                        'average_percentage': 0,
                        'highest_score': 0,
                        'lowest_score': 0,
                        'subjects_count': 0,
                        'weak_areas_count': 0,
                    },
                    message='No marks data found for this student'
                )

            stats = marks.aggregate(
                avg_percentage=Avg('percentage'),
                highest=Max('percentage'),
                lowest=Min('percentage'),
                total=Count('id')
            )
            weak_count = WeakArea.objects.filter(student=student).count()
            subjects_count = marks.values('subject').distinct().count()

            return APIResponse.success(
                data={
                    'student': StudentSerializer(student).data,
                    'total_exams': stats['total'],
                    'average_percentage': round(float(stats['avg_percentage'] or 0), 2),
                    'highest_score': round(float(stats['highest'] or 0), 2),
                    'lowest_score': round(float(stats['lowest'] or 0), 2),
                    'subjects_count': subjects_count,
                    'weak_areas_count': weak_count,
                },
                message='Student summary retrieved successfully'
            )
        except Exception as e:
            logger.error(f"Error getting student summary {pk}: {str(e)}")
            return APIResponse.error(message='Failed to get student summary')


# ─────────────────────────────────────────────
# SUBJECT VIEWSET
# ─────────────────────────────────────────────
class SubjectViewSet(viewsets.ModelViewSet):
    """
    CRUD for Subjects.
    GET/POST /api/subjects/
    GET/PUT/DELETE /api/subjects/{id}/
    """
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']


# ─────────────────────────────────────────────
# MARKS VIEWSET
# ─────────────────────────────────────────────
class MarksViewSet(viewsets.ModelViewSet):
    """
    CRUD for Marks + CSV upload.

    GET/POST  /api/marks/
    GET/PUT/DELETE /api/marks/{id}/
    POST      /api/marks/upload-csv/
    """
    queryset = Marks.objects.all().select_related('student', 'subject').order_by('-exam_date')
    serializer_class = MarksSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    search_fields = ['student__name', 'subject__name']
    ordering_fields = ['exam_date', 'percentage', 'subject__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        subject_id = self.request.query_params.get('subject_id')
        exam_type = self.request.query_params.get('exam_type')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if exam_type:
            queryset = queryset.filter(exam_type=exam_type)
        return queryset

    @action(
        detail=False,
        methods=['post'],
        url_path='upload-csv',
        parser_classes=[MultiPartParser, FormParser]
    )
    def upload_csv(self, request):
        """
        POST /api/marks/upload-csv/
        Upload a CSV with columns: student_name, subject, marks_obtained,
        max_marks, exam_type, exam_date
        """
        try:
            if 'file' not in request.FILES:
                return APIResponse.error(
                    message='No file uploaded',
                    errors={'file': 'Please upload a CSV file'}
                )

            uploaded_file = request.FILES['file']
            if not uploaded_file.name.endswith('.csv'):
                return APIResponse.error(
                    message='Invalid file type',
                    errors={'file': 'Only CSV files are accepted'}
                )

            file_content = uploaded_file.read().decode('utf-8')
            df = pd.read_csv(StringIO(file_content))
            df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')

            required_columns = ['student_name', 'subject', 'marks_obtained', 'max_marks', 'exam_type', 'exam_date']
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                return APIResponse.error(
                    message='Missing required columns in CSV',
                    errors={'missing_columns': missing, 'required_columns': required_columns}
                )

            created_marks = []
            errors = []

            for index, row in df.iterrows():
                try:
                    student, _ = Student.objects.get_or_create(
                        name=str(row['student_name']).strip(),
                        defaults={
                            'email': f"{str(row['student_name']).lower().replace(' ', '.')}@student.com",
                            'grade_level': int(row.get('grade_level', 10)),
                        }
                    )
                    subject, _ = Subject.objects.get_or_create(
                        name=str(row['subject']).strip(),
                        defaults={'code': str(row['subject'])[:3].upper() + '101'}
                    )
                    exam_date = pd.to_datetime(row['exam_date']).date()
                    mark, created = Marks.objects.get_or_create(
                        student=student,
                        subject=subject,
                        exam_type=str(row['exam_type']).lower().strip(),
                        exam_date=exam_date,
                        defaults={
                            'marks_obtained': float(row['marks_obtained']),
                            'max_marks': float(row['max_marks']),
                        }
                    )
                    if created:
                        created_marks.append({
                            'student': student.name,
                            'subject': subject.name,
                            'percentage': float(mark.percentage)
                        })
                except Exception as row_error:
                    errors.append({'row': index + 2, 'error': str(row_error)})

            if not created_marks and errors:
                return APIResponse.error(
                    message='CSV upload failed — no records created',
                    errors={'row_errors': errors}
                )

            return APIResponse.created(
                data={
                    'records_created': len(created_marks),
                    'records_failed': len(errors),
                    'created_marks': created_marks[:5],
                    'errors': errors[:5] if errors else [],
                },
                message=f'Successfully uploaded {len(created_marks)} mark records'
            )

        except pd.errors.ParserError:
            return APIResponse.error(message='Invalid CSV format', errors={'file': 'File could not be parsed as CSV'})
        except Exception as e:
            logger.error(f"CSV upload error: {str(e)}")
            return APIResponse.error(message='CSV upload failed', errors={'detail': str(e)})


# ─────────────────────────────────────────────
# PREDICTION VIEWSET (Read-only)
# ─────────────────────────────────────────────
class PredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/predictions/
    GET /api/predictions/{id}/
    GET /api/predictions/?student_id={id}
    """
    queryset = Prediction.objects.all().select_related('student', 'subject').order_by('-created_at')
    serializer_class = PredictionSerializer
    search_fields = ['student__name', 'subject__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        subject_id = self.request.query_params.get('subject_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        return queryset


# ─────────────────────────────────────────────
# WEAK AREA VIEWSET (Read-only)
# ─────────────────────────────────────────────
class WeakAreaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/weak-areas/
    GET /api/weak-areas/{id}/
    GET /api/weak-areas/?student_id={id}
    """
    queryset = WeakArea.objects.all().select_related('student', 'subject').order_by('priority_rank')
    serializer_class = WeakAreaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        severity = self.request.query_params.get('severity')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if severity:
            queryset = queryset.filter(severity=severity)
        return queryset


# ─────────────────────────────────────────────
# RECOMMENDATION VIEWSET (Read-only)
# ─────────────────────────────────────────────
class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/recommendations/
    GET /api/recommendations/{id}/
    GET /api/recommendations/?student_id={id}
    """
    queryset = Recommendation.objects.filter(is_active=True).select_related('student', 'subject').order_by('-created_at')
    serializer_class = RecommendationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        subject_id = self.request.query_params.get('subject_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        return queryset


# ─────────────────────────────────────────────
# DASHBOARD VIEW
# ─────────────────────────────────────────────
class DashboardView(APIView):
    """
    Single endpoint that returns all data needed for the dashboard.
    GET /api/dashboard/{student_id}/
    """

    def get(self, request, student_id):
        try:
            student = get_object_or_404(Student, pk=student_id)
            marks = Marks.objects.filter(student=student).select_related('subject').order_by('exam_date')

            radar_data = self._get_radar_data(marks)
            trend_data = self._get_trend_data(marks)

            weak_areas = WeakArea.objects.filter(student=student).select_related('subject').order_by('priority_rank')
            predictions = Prediction.objects.filter(student=student).select_related('subject').order_by('prediction_for_date')
            recommendations = Recommendation.objects.filter(student=student, is_active=True).select_related('subject')[:5]

            marks_stats = marks.aggregate(
                avg=Avg('percentage'),
                highest=Max('percentage'),
                lowest=Min('percentage'),
                total=Count('id')
            )

            return APIResponse.success(
                data={
                    'student': StudentSerializer(student).data,
                    'summary': {
                        'total_exams': marks_stats['total'],
                        'average_percentage': round(float(marks_stats['avg'] or 0), 2),
                        'highest_score': round(float(marks_stats['highest'] or 0), 2),
                        'lowest_score': round(float(marks_stats['lowest'] or 0), 2),
                        'weak_areas_count': weak_areas.count(),
                        'subjects_count': marks.values('subject').distinct().count(),
                    },
                    'radar_chart': radar_data,
                    'trend_line': trend_data,
                    'weak_areas': WeakAreaSerializer(weak_areas, many=True).data,
                    'predictions': PredictionSerializer(predictions, many=True).data,
                    'recommendations': RecommendationSerializer(recommendations, many=True).data,
                },
                message='Dashboard data retrieved successfully'
            )
        except Exception as e:
            logger.error(f"Dashboard error for student {student_id}: {str(e)}")
            return APIResponse.error(message='Failed to load dashboard data', errors={'detail': str(e)})

    def _get_radar_data(self, marks):
        """Format data for radar chart visualization"""
        subject_averages = marks.values('subject__name', 'subject__color').annotate(
            avg_percentage=Avg('percentage')
        ).order_by('subject__name')
        return [
            {
                'subject': item['subject__name'],
                'score': round(float(item['avg_percentage']), 2),
                'color': item['subject__color'],
                'fullMark': 100,
            }
            for item in subject_averages
        ]

    def _get_trend_data(self, marks):
        """Format monthly trend data for line chart"""
        monthly = marks.extra(
            select={'month': "DATE_TRUNC('month', exam_date)"}
        ).values('month').annotate(
            avg_percentage=Avg('percentage')
        ).order_by('month')
        return [
            {
                'month': item['month'].strftime('%b %Y') if item['month'] else '',
                'percentage': round(float(item['avg_percentage']), 2),
            }
            for item in monthly
        ]


# ─────────────────────────────────────────────
# ANALYSIS TRIGGER VIEW
# ─────────────────────────────────────────────
class TriggerAnalysisView(APIView):
    """
    POST /api/analysis/trigger/
    Body: { "student_id": 1 }
    Triggers the AI agent pipeline for a student (Celery task in Task 6).
    """

    def post(self, request):
        try:
            student_id = request.data.get('student_id')
            if not student_id:
                return APIResponse.error(
                    message='student_id is required',
                    errors={'student_id': 'This field is required'}
                )

            student = get_object_or_404(Student, pk=student_id)
            marks_count = Marks.objects.filter(student=student).count()

            if marks_count < 3:
                return APIResponse.error(
                    message='Not enough data for analysis',
                    errors={
                        'marks_count': marks_count,
                        'minimum_required': 3,
                        'hint': 'Add at least 3 mark entries before running analysis'
                    }
                )

            # Celery task will be wired here in Task 6
            return APIResponse.success(
                data={
                    'student_id': student_id,
                    'student_name': student.name,
                    'status': 'queued',
                },
                message=f'Analysis queued for {student.name}'
            )

        except Exception as e:
            logger.error(f"Error triggering analysis: {str(e)}")
            return APIResponse.error(message='Failed to trigger analysis', errors={'detail': str(e)})


# ─────────────────────────────────────────────
# CHAT VIEW
# ─────────────────────────────────────────────
class ChatView(APIView):
    """
    LangChain-powered chat interface.

    POST /api/chat/query/
    Body: { "student_id": 1, "message": "Which subject needs most work?" }

    GET /api/chat/query/?student_id=1
    Returns conversation history.
    """

    def post(self, request):
        try:
            student_id   = request.data.get('student_id')
            user_message = request.data.get('message', '').strip()

            if not student_id or not user_message:
                return APIResponse.error(
                    message='student_id and message are required',
                    errors={
                        'student_id': 'Required',
                        'message':    'Required',
                    }
                )

            if len(user_message) > 1000:
                return APIResponse.error(
                    message='Message too long',
                    errors={'message': 'Maximum 1000 characters'}
                )

            student = get_object_or_404(Student, pk=student_id)

            # Save user message
            ChatMessage.objects.create(
                student = student,
                role    = 'user',
                content = user_message,
            )

            # Generate AI response via LangChain ChatEngine
            try:
                from apps.chat.chat_engine import ChatEngine
                engine   = ChatEngine(student_id=int(student_id))
                ai_reply = engine.generate_response(user_message)
            except Exception as e:
                logger.error(f"ChatEngine error: {e}")
                ai_reply = (
                    "I'm having trouble accessing your performance data. "
                    "Please ensure analysis has been run for your profile "
                    "by clicking Run Analysis on the dashboard."
                )

            # Save AI response
            ai_message = ChatMessage.objects.create(
                student = student,
                role    = 'assistant',
                content = ai_reply,
            )

            logger.info(
                f"Chat: student={student_id}, "
                f"response_len={len(ai_reply)}"
            )

            return APIResponse.success(
                data={
                    'message_id':   ai_message.id,
                    'student_id':   student_id,
                    'user_message': user_message,
                    'ai_response':  ai_reply,
                    'timestamp':    ai_message.created_at.isoformat(),
                },
                message='Message processed'
            )

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return APIResponse.error(
                message='Failed to process message',
                errors={'detail': str(e)}
            )

    def get(self, request):
        """Get conversation history for a student."""
        try:
            student_id = request.query_params.get('student_id')
            if not student_id:
                return APIResponse.error(message='student_id is required')

            student  = get_object_or_404(Student, pk=student_id)
            messages = ChatMessage.objects.filter(
                student=student
            ).order_by('created_at')

            serializer = ChatMessageSerializer(messages, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f'{len(serializer.data)} messages'
            )
        except Exception as e:
            return APIResponse.error(message='Failed to get chat history')
