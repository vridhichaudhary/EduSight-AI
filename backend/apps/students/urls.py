"""
URL patterns for the students app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    SubjectViewSet,
    MarksViewSet,
    PredictionViewSet,
    WeakAreaViewSet,
    RecommendationViewSet,
    DashboardView,
    TriggerAnalysisView,
    ChatView,
    BulkMarksCreateView,
    ComparisonView,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'marks', MarksViewSet, basename='marks')
router.register(r'predictions', PredictionViewSet, basename='prediction')
router.register(r'weak-areas', WeakAreaViewSet, basename='weakarea')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('dashboard/<int:student_id>/', DashboardView.as_view(), name='dashboard'),
    path('chat/query/', ChatView.as_view(), name='chat-query'),
    path('marks/bulk/', BulkMarksCreateView.as_view(), name='marks-bulk-create'),
    path('compare/', ComparisonView.as_view(), name='compare-students'),
    path('', include(router.urls)),
]
