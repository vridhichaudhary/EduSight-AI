"""
EduSight AI — Agent Data Loader

Loads all student performance data from PostgreSQL
into a structured dict for the AgentState.

Called once at the start of the agent workflow.
All agents read from this pre-loaded data rather
than hitting the database repeatedly.
"""

import logging
from django.db.models import Avg, Max, Min, Count

logger = logging.getLogger('apps.analysis')


def load_student_context(student_id: int) -> dict:
    """
    Load complete student context for agent workflow.

    Returns dict containing:
        student_info    : Basic student details
        marks_summary   : Aggregated marks statistics
        ml_predictions  : Latest ML predictions from DB
        weak_areas_data : Latest weak areas from DB
        pattern_data    : Latest pattern analysis results
    """
    from apps.students.models import (
        Student, Marks, Prediction, WeakArea, AnalysisLog
    )
    from apps.analysis.pattern_analysis import PatternAnalyzer

    logger.info(f"Loading context for student {student_id}")

    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        raise ValueError(f"Student {student_id} not found")

    # ── Marks Summary ──
    marks_qs = Marks.objects.filter(
        student=student
    ).select_related('subject')

    marks_stats = marks_qs.aggregate(
        overall_avg = Avg('percentage'),
        highest     = Max('percentage'),
        lowest      = Min('percentage'),
        total       = Count('id'),
    )

    # Per-subject averages
    subject_avgs = {}
    for item in marks_qs.values('subject__name').annotate(
        avg=Avg('percentage')
    ):
        subject_avgs[item['subject__name']] = round(
            float(item['avg']), 2
        )

    marks_summary = {
        'subjects':         list(subject_avgs.keys()),
        'total_exams':      marks_stats['total'] or 0,
        'overall_avg':      round(float(marks_stats['overall_avg'] or 0), 2),
        'highest_score':    round(float(marks_stats['highest'] or 0), 2),
        'lowest_score':     round(float(marks_stats['lowest'] or 0), 2),
        'subject_averages': subject_avgs,
    }

    # ── ML Predictions ──
    predictions_qs = Prediction.objects.filter(
        student=student
    ).select_related('subject').order_by('-created_at')

    ml_predictions = [
        {
            'subject':          p.subject.name,
            'predicted_marks':  float(p.predicted_marks),
            'confidence':       float(p.confidence_score),
            'lower_bound':      float(p.lower_bound) if p.lower_bound else None,
            'upper_bound':      float(p.upper_bound) if p.upper_bound else None,
            'is_at_risk':       p.is_at_risk(),
            'model_name':       p.model_name,
        }
        for p in predictions_qs
    ]

    # ── Weak Areas ──
    weak_qs = WeakArea.objects.filter(
        student=student
    ).select_related('subject').order_by('priority_rank')

    weak_areas_data = [
        {
            'subject':             w.subject.name,
            'current_percentage':  float(w.current_percentage),
            'class_average':       float(w.class_average) if w.class_average else 75,
            'gap_from_target':     float(w.gap_from_target),
            'severity':            w.severity,
            'priority_rank':       w.priority_rank,
            'reason':              w.reason or '',
            'improvement_potential': float(w.improvement_potential),
            'color_code':          w.get_color_code(),
        }
        for w in weak_qs
    ]

    # ── Pattern Data ──
    try:
        analyzer     = PatternAnalyzer(student_id)
        pattern_data = analyzer.run_full_analysis()
    except Exception as e:
        logger.warning(f"Pattern analysis failed in loader: {e}")
        pattern_data = {
            'success':        False,
            'overall_trend':  {'direction': 'stable', 'slope': 0},
            'subject_trends': [],
            'correlations':   [],
            'outliers':       [],
            'monthly_trend':  [],
        }

    context = {
        'student_id':    student_id,
        'student_name':  student.name,
        'grade_level':   student.grade_level,
        'marks_summary': marks_summary,
        'ml_predictions': ml_predictions,
        'weak_areas_data': weak_areas_data,
        'pattern_data':    pattern_data,
    }

    logger.info(
        f"Context loaded: {len(marks_summary['subjects'])} subjects, "
        f"{len(ml_predictions)} predictions, "
        f"{len(weak_areas_data)} weak areas"
    )

    return context
