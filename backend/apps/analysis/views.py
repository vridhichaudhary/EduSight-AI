"""
EduSight AI — Analysis API Views

Endpoints:
    POST /api/analysis/trigger/         → Start analysis task
    GET  /api/analysis/status/{task_id}/ → Check task status
    GET  /api/analysis/logs/{student_id}/ → Get analysis logs
    GET  /api/analysis/summary/{student_id}/ → Get latest results
"""

import logging
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.views import APIView
from celery.result import AsyncResult
from apps.students.models import Student, AnalysisLog, Prediction, WeakArea
from apps.students.serializers import (
    AnalysisLogSerializer,
    PredictionSerializer,
    WeakAreaSerializer,
)
from apps.students.utils import APIResponse
from .tasks import run_ml_analysis

logger = logging.getLogger('apps.analysis')


class TriggerAnalysisView(APIView):
    """
    Trigger full ML analysis for a student.
    Queues Celery background task.

    POST /api/analysis/trigger/
    Body: { "student_id": 1, "retrain": false }
    """

    def post(self, request):
        try:
            student_id = request.data.get('student_id')
            retrain    = request.data.get('retrain', False)

            # ── Validate inputs ──
            if not student_id:
                return APIResponse.error(
                    message='student_id is required',
                    errors={'student_id': 'This field is required'}
                )

            student = get_object_or_404(Student, pk=student_id)

            # ── Check minimum data requirement ──
            from apps.students.models import Marks
            marks_count = Marks.objects.filter(student=student).count()

            if marks_count < 3:
                return APIResponse.error(
                    message='Insufficient data for analysis',
                    errors={
                        'marks_count':       marks_count,
                        'minimum_required':  3,
                        'hint': (
                            'Upload a CSV with at least 3 mark entries '
                            'before running analysis.'
                        ),
                    }
                )

            # ── Queue Celery task ──
            task = run_ml_analysis.delay(
                student_id = int(student_id),
                retrain    = bool(retrain),
            )

            logger.info(
                f"Analysis queued: student={student_id}, task={task.id}"
            )

            return APIResponse.success(
                data={
                    'task_id':      task.id,
                    'student_id':   student_id,
                    'student_name': student.name,
                    'status':       'queued',
                    'marks_count':  marks_count,
                    'message': (
                        'Analysis queued. Poll /api/analysis/status/'
                        f'{task.id}/ for updates.'
                    ),
                },
                message=f'Analysis queued for {student.name}'
            )

        except Exception as e:
            logger.error(f"Trigger analysis error: {str(e)}")
            return APIResponse.error(
                message='Failed to trigger analysis',
                errors={'detail': str(e)}
            )


class AnalysisStatusView(APIView):
    """
    Check status of a running Celery task.

    GET /api/analysis/status/{task_id}/
    Returns: pending | started | success | failure + result
    """

    def get(self, request, task_id):
        try:
            result = AsyncResult(task_id)
            state  = result.state

            if state == 'PENDING':
                return APIResponse.success(
                    data={
                        'task_id': task_id,
                        'status':  'pending',
                        'message': 'Task is queued, waiting to start.',
                    }
                )

            elif state == 'STARTED':
                return APIResponse.success(
                    data={
                        'task_id': task_id,
                        'status':  'running',
                        'message': 'Analysis is running...',
                    }
                )

            elif state == 'SUCCESS':
                task_result = result.result or {}
                return APIResponse.success(
                    data={
                        'task_id':        task_id,
                        'status':         'success',
                        'message':        'Analysis complete.',
                        'result_summary': {
                            'predictions_created': (
                                task_result.get('results', {})
                                .get('predictions', {})
                                .get('predictions_created', 0)
                            ),
                            'weak_areas_found': (
                                task_result.get('results', {})
                                .get('weak_areas', {})
                                .get('weak_areas_found', 0)
                            ),
                            'execution_time': task_result.get(
                                'execution_time', 0
                            ),
                        },
                    },
                    message='Analysis completed successfully'
                )

            elif state == 'FAILURE':
                return APIResponse.error(
                    message='Analysis failed',
                    errors={
                        'task_id': task_id,
                        'detail':  str(result.result),
                    },
                    status_code=500
                )

            else:
                return APIResponse.success(
                    data={'task_id': task_id, 'status': state.lower()}
                )

        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return APIResponse.error(message='Failed to check status')


class AnalysisLogsView(APIView):
    """
    Get analysis execution logs for a student.

    GET /api/analysis/logs/{student_id}/
    """

    def get(self, request, student_id):
        try:
            student = get_object_or_404(Student, pk=student_id)
            logs    = AnalysisLog.objects.filter(
                student=student
            ).order_by('-started_at')[:20]

            serializer = AnalysisLogSerializer(logs, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f'{len(serializer.data)} log entries'
            )
        except Exception as e:
            return APIResponse.error(message='Failed to fetch logs')


class AnalysisSummaryView(APIView):
    """
    Get latest analysis summary for a student.
    Returns predictions + weak areas from DB.

    GET /api/analysis/summary/{student_id}/
    """

    def get(self, request, student_id):
        try:
            student = get_object_or_404(Student, pk=student_id)

            predictions = Prediction.objects.filter(
                student=student
            ).select_related('subject').order_by('-created_at')

            weak_areas = WeakArea.objects.filter(
                student=student
            ).select_related('subject').order_by('priority_rank')

            # Get latest supervisor log with final AI report
            latest_log = AnalysisLog.objects.filter(
                student    = student,
                agent_name = 'supervisor',
                status     = 'completed',
            ).order_by('-completed_at').first()

            final_report     = None
            pattern_findings = None
            weak_insights    = None
            recommendations  = []

            if latest_log and latest_log.output_data:
                output = latest_log.output_data
                # Output is nested under 'agents' key when coming from full pipeline
                agents_output = output.get('agents', output)
                final_report     = agents_output.get('final_report') or output.get('final_report')
                pattern_findings = agents_output.get('pattern_findings') or output.get('pattern_findings')
                weak_insights    = agents_output.get('weak_area_insights') or output.get('weak_area_insights')
                recommendations  = agents_output.get('recommendations', []) or output.get('recommendations', [])

            return APIResponse.success(
                data={
                    'predictions':            PredictionSerializer(
                        predictions, many=True
                    ).data,
                    'weak_areas':             WeakAreaSerializer(
                        weak_areas, many=True
                    ).data,
                    'final_report':           final_report,
                    'pattern_findings':       pattern_findings,
                    'weak_insights':          weak_insights,
                    'recommendations_count':  len(recommendations),
                    'last_analyzed':          (
                        latest_log.completed_at.isoformat()
                        if latest_log else None
                    ),
                    'analysis_count':         AnalysisLog.objects.filter(
                        student=student, status='completed'
                    ).count(),
                },
                message='Analysis summary retrieved'
            )

        except Exception as e:
            logger.error(f"Summary error: {str(e)}")
            return APIResponse.error(message='Failed to fetch summary')


class DownloadReportView(APIView):
    """
    Generate and download PDF performance report.

    GET /api/analysis/report/{student_id}/

    Returns:
        PDF file as binary response (application/pdf)
        Browser automatically triggers download
    """

    def get(self, request, student_id):
        try:
            from apps.students.models import Student
            student = get_object_or_404(Student, pk=student_id)

            # ── Check data exists ──
            from apps.students.models import Marks
            marks_count = Marks.objects.filter(student=student).count()

            if marks_count == 0:
                return APIResponse.error(
                    message='No marks data found for report',
                    errors={
                        'hint': (
                            'Upload marks data and run analysis first.'
                        )
                    }
                )

            # ── Generate PDF ──
            from apps.analysis.pdf_generator import (
                generate_student_report
            )

            logger.info(
                f"Generating PDF report: student {student_id}"
            )

            pdf_bytes = generate_student_report(student_id)

            if not pdf_bytes:
                return APIResponse.error(
                    message='PDF generation failed',
                    errors={
                        'hint': (
                            'Make sure ReportLab is installed '
                            'and analysis has been run.'
                        )
                    },
                    status_code=500
                )

            # ── Return PDF response ──
            filename = (
                f"EduSight_Report_"
                f"{student.name.replace(' ', '_')}_"
                f"{student_id}.pdf"
            )

            response = HttpResponse(
                pdf_bytes,
                content_type='application/pdf'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{filename}"'
            )
            response['Content-Length'] = len(pdf_bytes)

            logger.info(
                f"PDF report downloaded: student {student_id}, "
                f"{len(pdf_bytes)} bytes"
            )

            return response

        except Exception as e:
            logger.error(f"PDF download error: {e}")
            return APIResponse.error(
                message='Failed to generate report',
                errors={'detail': str(e)},
                status_code=500
            )
