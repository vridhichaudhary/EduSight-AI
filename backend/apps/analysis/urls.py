"""
URL patterns for Analysis app.
"""

from django.urls import path
from .views import (
    TriggerAnalysisView,
    AnalysisStatusView,
    AnalysisLogsView,
    AnalysisSummaryView,
)

urlpatterns = [
    path(
        'trigger/',
        TriggerAnalysisView.as_view(),
        name='analysis-trigger'
    ),
    path(
        'status/<str:task_id>/',
        AnalysisStatusView.as_view(),
        name='analysis-status'
    ),
    path(
        'logs/<int:student_id>/',
        AnalysisLogsView.as_view(),
        name='analysis-logs'
    ),
    path(
        'summary/<int:student_id>/',
        AnalysisSummaryView.as_view(),
        name='analysis-summary'
    ),
]
