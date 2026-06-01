"""
EduSight AI — Pattern Analyzer

Detects performance patterns:
    - Overall trend (improving/declining/stable/volatile)
    - Per-subject trend
    - Subject correlations
    - Seasonal patterns (performance by month)
    - Outlier exams (unusually high/low scores)
    - Study gap analysis
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime

logger = logging.getLogger('apps.analysis')


class PatternAnalyzer:
    """
    Analyzes performance patterns in student marks data.

    Returns structured findings used by:
    - Dashboard trend line chart
    - AI agent context (TASK 8)
    - Chat interface context (TASK 10)
    """

    def __init__(self, student_id: int):
        self.student_id = student_id
        self.df         = None

    def _load_data(self):
        """Load marks from database."""
        from apps.students.models import Marks, Student

        student  = Student.objects.get(pk=self.student_id)
        marks_qs = Marks.objects.filter(
            student=student
        ).select_related('subject').order_by('exam_date')

        records = [
            {
                'subject':    m.subject.name,
                'percentage': float(m.percentage),
                'exam_type':  m.exam_type,
                'exam_date':  pd.to_datetime(m.exam_date),
            }
            for m in marks_qs
        ]
        self.df = pd.DataFrame(records)
        return self.df

    def detect_overall_trend(self) -> dict:
        """
        Detect if student is improving, declining, or stable.

        Returns:
            direction : improving | declining | stable | volatile
            slope     : rate of change per exam
            confidence: how clear the trend is (0-1)
        """
        if self.df is None:
            self._load_data()

        if len(self.df) < 3:
            return {
                'direction':  'stable',
                'slope':       0.0,
                'confidence':  0.0,
                'description': 'Not enough data to detect trend.',
            }

        percentages = self.df['percentage'].values
        x           = np.arange(len(percentages))

        # Fit linear trend
        coeffs = np.polyfit(x, percentages, 1)
        slope  = float(coeffs[0])

        # R² to measure trend clarity
        trend_line  = np.polyval(coeffs, x)
        ss_res      = np.sum((percentages - trend_line) ** 2)
        ss_tot      = np.sum((percentages - percentages.mean()) ** 2)
        r_squared   = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        confidence  = round(abs(r_squared), 3)

        # Volatility check
        std_dev = float(np.std(percentages))
        mean    = float(np.mean(percentages))
        cv      = std_dev / mean if mean != 0 else 0

        if cv > 0.25:
            direction   = 'volatile'
            description = (
                f"High variability in scores (std: {std_dev:.1f}%). "
                f"Performance is inconsistent."
            )
        elif slope > 1.0:
            direction   = 'improving'
            description = (
                f"Clear upward trend (+{slope:.2f}% per exam). "
                f"Keep it up!"
            )
        elif slope < -1.0:
            direction   = 'declining'
            description = (
                f"Downward trend ({slope:.2f}% per exam). "
                f"Intervention recommended."
            )
        else:
            direction   = 'stable'
            description = (
                f"Performance is steady around {mean:.1f}%. "
                f"Aim to push higher."
            )

        return {
            'direction':   direction,
            'slope':       round(slope, 4),
            'confidence':  confidence,
            'std_dev':     round(std_dev, 2),
            'mean':        round(mean, 2),
            'description': description,
        }

    def detect_subject_trends(self) -> list:
        """
        Detect trend per subject.
        Returns list of subject trend objects.
        """
        if self.df is None:
            self._load_data()

        subject_trends = []
        for subject in self.df['subject'].unique():
            sub_df = self.df[self.df['subject'] == subject].copy()

            if len(sub_df) < 2:
                subject_trends.append({
                    'subject':      subject,
                    'direction':    'stable',
                    'slope':         0.0,
                    'avg':          round(float(sub_df['percentage'].mean()), 2),
                    'latest':       round(float(sub_df['percentage'].iloc[-1]), 2),
                    'exam_count':   len(sub_df),
                })
                continue

            scores = sub_df['percentage'].values
            x      = np.arange(len(scores))
            slope  = float(np.polyfit(x, scores, 1)[0])

            if slope > 1:
                direction = 'improving'
            elif slope < -1:
                direction = 'declining'
            else:
                direction = 'stable'

            subject_trends.append({
                'subject':    subject,
                'direction':  direction,
                'slope':      round(slope, 4),
                'avg':        round(float(scores.mean()), 2),
                'latest':     round(float(scores[-1]), 2),
                'exam_count': len(sub_df),
            })

        # Sort by slope (most declining first)
        subject_trends.sort(key=lambda x: x['slope'])
        return subject_trends

    def find_correlations(self) -> list:
        """
        Find which subjects correlate with each other.
        High correlation means improving one helps the other.
        """
        if self.df is None:
            self._load_data()

        # Pivot to subject columns
        pivot = self.df.pivot_table(
            index='exam_date',
            columns='subject',
            values='percentage',
            aggfunc='mean',
        )

        if pivot.shape[1] < 2:
            return []

        corr_matrix = pivot.corr()
        correlations = []

        subjects = corr_matrix.columns.tolist()
        for i in range(len(subjects)):
            for j in range(i + 1, len(subjects)):
                corr_val = float(corr_matrix.iloc[i, j])
                if abs(corr_val) >= 0.5:
                    correlations.append({
                        'subject_a':   subjects[i],
                        'subject_b':   subjects[j],
                        'correlation': round(corr_val, 3),
                        'type':        'positive' if corr_val > 0 else 'negative',
                        'insight': (
                            f"Strong connection between {subjects[i]} "
                            f"and {subjects[j]}. "
                            f"Improving one may help the other."
                            if corr_val > 0
                            else
                            f"{subjects[i]} and {subjects[j]} "
                            f"show inverse performance."
                        ),
                    })

        return sorted(
            correlations,
            key=lambda x: abs(x['correlation']),
            reverse=True
        )

    def detect_outliers(self) -> list:
        """
        Find unusually high or low exam scores.
        Uses Z-score method.
        """
        if self.df is None:
            self._load_data()

        if len(self.df) < 4:
            return []

        mean   = self.df['percentage'].mean()
        std    = self.df['percentage'].std()
        if std == 0:
            return []

        outliers = []
        for _, row in self.df.iterrows():
            z_score = (row['percentage'] - mean) / std
            if abs(z_score) >= 2.0:
                outliers.append({
                    'subject':    row['subject'],
                    'percentage': round(float(row['percentage']), 2),
                    'exam_date':  str(row['exam_date'].date()),
                    'z_score':    round(float(z_score), 3),
                    'type':       'high' if z_score > 0 else 'low',
                    'description': (
                        f"Unusually {'high' if z_score > 0 else 'low'} "
                        f"score in {row['subject']} on "
                        f"{row['exam_date'].strftime('%b %d, %Y')}."
                    ),
                })

        return outliers

    def get_monthly_trend(self) -> list:
        """
        Aggregate performance by month for trend line chart.
        Returns list of {month, percentage} for frontend.
        """
        if self.df is None:
            self._load_data()

        if self.df.empty:
            return []

        self.df['month_year'] = self.df['exam_date'].dt.to_period('M')
        monthly = self.df.groupby('month_year')['percentage'].mean().reset_index()
        monthly['month_year'] = monthly['month_year'].astype(str)

        return [
            {
                'month':      row['month_year'],
                'percentage': round(float(row['percentage']), 2),
            }
            for _, row in monthly.iterrows()
        ]

    def run_full_analysis(self) -> dict:
        """
        Run all pattern analyses and return combined result.
        Called by Celery task.
        """
        logger.info(
            f"Running pattern analysis for student {self.student_id}"
        )

        try:
            self._load_data()

            return {
                'success':           True,
                'student_id':        self.student_id,
                'overall_trend':     self.detect_overall_trend(),
                'subject_trends':    self.detect_subject_trends(),
                'correlations':      self.find_correlations(),
                'outliers':          self.detect_outliers(),
                'monthly_trend':     self.get_monthly_trend(),
            }
        except Exception as e:
            logger.error(f"Pattern analysis failed: {str(e)}")
            return {'success': False, 'error': str(e)}
