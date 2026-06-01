"""
EduSight AI — Weak Area Detector

Analyzes student performance per subject and identifies
areas that need improvement. Ranks by priority and
saves to WeakArea model.

Severity classification:
    critical : < 40%
    severe   : 40-50%
    moderate : 50-60%
    mild     : 60-70%
    warning  : 70-80% (close to class average)
"""

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger('apps.analysis')


class WeakAreaDetector:
    """
    Identifies and ranks student weak areas.

    Algorithm:
    1. Calculate per-subject average percentage
    2. Calculate student overall average
    3. Compute gap = overall_avg - subject_avg
    4. Classify severity by absolute percentage
    5. Rank by gap (largest gap = highest priority)
    6. Save to WeakArea model
    """

    SEVERITY_THRESHOLDS = {
        'critical': (0,  40),
        'severe':   (40, 50),
        'moderate': (50, 60),
        'mild':     (60, 70),
        'warning':  (70, 80),
    }

    def __init__(self, student_id: int):
        self.student_id = student_id

    def _classify_severity(self, percentage: float) -> str:
        """Classify severity based on percentage score."""
        for severity, (low, high) in self.SEVERITY_THRESHOLDS.items():
            if low <= percentage < high:
                return severity
        return 'default'  # >= 80%, no weak area

    def _get_color(self, severity: str) -> str:
        """Return hex color for severity level."""
        colors = {
            'critical': '#ef4444',
            'severe':   '#f97316',
            'moderate': '#f59e0b',
            'mild':     '#84cc16',
            'warning':  '#22c55e',
            'default':  '#22c55e',
        }
        return colors.get(severity, '#52525b')

    def analyze(self) -> dict:
        """
        Run full weak area analysis for student.
        Returns analysis results dict.
        """
        from apps.students.models import (
            Student, Marks, Subject, WeakArea
        )

        logger.info(
            f"Running weak area analysis for student {self.student_id}"
        )

        try:
            student = Student.objects.get(pk=self.student_id)
        except Student.DoesNotExist:
            return {'success': False, 'error': 'Student not found'}

        marks_qs = Marks.objects.filter(
            student=student
        ).select_related('subject')

        if not marks_qs.exists():
            return {
                'success': False,
                'error': 'No marks found for student'
            }

        # ── Build DataFrame ──
        records = [
            {
                'subject':    m.subject.name,
                'subject_id': m.subject.id,
                'percentage': float(m.percentage),
                'exam_type':  m.exam_type,
                'exam_date':  m.exam_date,
            }
            for m in marks_qs
        ]
        df = pd.DataFrame(records)

        # ── Per-subject statistics ──
        subject_stats = df.groupby('subject').agg(
            avg_percentage = ('percentage', 'mean'),
            exam_count     = ('percentage', 'count'),
            latest_score   = ('percentage', 'last'),
            min_score      = ('percentage', 'min'),
            max_score      = ('percentage', 'max'),
        ).reset_index()

        # ── Overall average ──
        overall_avg = float(df['percentage'].mean())

        # ── Class average simulation ──
        # In production: query other students same grade
        class_avg = min(overall_avg + 5, 85)

        # ── Classify and rank ──
        weak_areas_found = []

        for _, row in subject_stats.iterrows():
            subject_avg = float(row['avg_percentage'])
            severity    = self._classify_severity(subject_avg)

            # Only flag as weak if below 80%
            if severity == 'default':
                continue

            gap_from_overall = max(0, overall_avg - subject_avg)
            gap_from_class   = max(0, class_avg - subject_avg)

            # Improvement potential (how much they can realistically gain)
            improvement_potential = min(
                30,
                max(5, (80 - subject_avg) * 0.5)
            )

            weak_areas_found.append({
                'subject':                row['subject'],
                'current_percentage':     round(subject_avg, 2),
                'class_average':          round(class_avg, 2),
                'gap_from_target':        round(gap_from_class, 2),
                'severity':               severity,
                'improvement_potential':  round(improvement_potential, 2),
                'reason':                 self._generate_reason(
                    row['subject'], subject_avg, severity,
                    float(row['latest_score']), overall_avg
                ),
                'color_code':             self._get_color(severity),
                'exam_count':             int(row['exam_count']),
            })

        # ── Sort by priority (critical first, then by gap) ──
        severity_order = {
            'critical': 0, 'severe': 1, 'moderate': 2,
            'mild': 3, 'warning': 4
        }
        weak_areas_found.sort(
            key=lambda x: (
                severity_order.get(x['severity'], 5),
                -x['gap_from_target']
            )
        )

        # ── Save to database ──
        saved_count = 0
        # Clear old weak areas for this student
        WeakArea.objects.filter(student=student).delete()

        for rank, area in enumerate(weak_areas_found):
            try:
                subject = Subject.objects.get(name=area['subject'])
                WeakArea.objects.create(
                    student              = student,
                    subject              = subject,
                    current_percentage   = area['current_percentage'],
                    class_average        = area['class_average'],
                    gap_from_target      = area['gap_from_target'],
                    severity             = area['severity'],
                    priority_rank        = rank,
                    reason               = area['reason'],
                    improvement_potential = area['improvement_potential'],
                )
                saved_count += 1
            except Exception as e:
                logger.warning(f"Could not save weak area: {e}")

        logger.info(
            f"Weak area analysis done: {saved_count} areas saved"
        )

        return {
            'success':           True,
            'student_id':        self.student_id,
            'overall_average':   round(overall_avg, 2),
            'class_average':     round(class_avg, 2),
            'weak_areas_found':  len(weak_areas_found),
            'weak_areas_saved':  saved_count,
            'weak_areas':        weak_areas_found,
        }

    def _generate_reason(
        self,
        subject: str,
        avg: float,
        severity: str,
        latest: float,
        overall_avg: float,
    ) -> str:
        """Generate human-readable reason for weak area."""
        gap = round(overall_avg - avg, 1)

        reasons = {
            'critical': (
                f"{subject} is critically below target at {avg:.1f}%. "
                f"Immediate focused study is required."
            ),
            'severe': (
                f"{subject} shows severe underperformance at {avg:.1f}%. "
                f"Significant improvement needed."
            ),
            'moderate': (
                f"{subject} performance at {avg:.1f}% is {gap}% below "
                f"your overall average. Structured practice recommended."
            ),
            'mild': (
                f"{subject} at {avg:.1f}% is slightly below overall average. "
                f"Regular revision should improve scores."
            ),
            'warning': (
                f"{subject} at {avg:.1f}% is close to class average "
                f"but has room for improvement."
            ),
        }
        return reasons.get(severity, f"{subject} needs attention.")
