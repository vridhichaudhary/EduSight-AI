"""URL patterns for RAG and Recommendations app."""

from django.urls import path
from .views import (
    RAGSearchView,
    RAGStatusView,
    RAGRebuildView,
    RAGResourceListView,
    RAGContextView,
)

urlpatterns = [
    path('search/',            RAGSearchView.as_view(),       name='rag-search'),
    path('status/',            RAGStatusView.as_view(),       name='rag-status'),
    path('rebuild/',           RAGRebuildView.as_view(),      name='rag-rebuild'),
    path('resources/',         RAGResourceListView.as_view(), name='rag-resources'),
    path('context/',           RAGContextView.as_view(),      name='rag-context'),
]
