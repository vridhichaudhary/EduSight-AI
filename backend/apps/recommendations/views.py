"""
EduSight AI — Recommendations & RAG API Views

Endpoints:
    GET  /api/rag/search/           → Search resources
    GET  /api/rag/status/           → Index statistics
    POST /api/rag/rebuild/          → Rebuild FAISS index
    GET  /api/rag/resources/        → List all resources
    GET  /api/rag/subject/{name}/   → Resources by subject
"""

import logging
from rest_framework.views import APIView
from apps.students.utils import APIResponse

logger = logging.getLogger('apps.recommendations')


class RAGSearchView(APIView):
    """
    Search educational resources using semantic search.

    GET /api/rag/search/?query=algebra+equations&k=5&subject=Mathematics
    """

    def get(self, request):
        try:
            query   = request.query_params.get('query', '').strip()
            k       = int(request.query_params.get('k', 5))
            subject = request.query_params.get('subject', None)

            if not query:
                return APIResponse.error(
                    message='query parameter is required',
                    errors={'query': 'Provide a search query'}
                )

            k = min(max(1, k), 15)

            from .rag_system import ResourceRetriever
            retriever = ResourceRetriever()

            results = retriever.search(query=query, k=k, subject=subject)

            return APIResponse.success(
                data={
                    'query':        query,
                    'subject':      subject,
                    'results':      results,
                    'count':        len(results),
                },
                message=f'Found {len(results)} resources'
            )

        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return APIResponse.error(
                message='Search failed',
                errors={'detail': str(e)}
            )


class RAGStatusView(APIView):
    """
    Get FAISS vectorstore status and statistics.

    GET /api/rag/status/
    """

    def get(self, request):
        try:
            from .rag_system import FAISSVectorStore
            store = FAISSVectorStore()
            stats = store.get_stats()

            from .resource_loader import (
                get_all_resources, get_subjects_list
            )
            all_resources = get_all_resources()

            return APIResponse.success(
                data={
                    'index_exists':    stats.get('exists', False),
                    'index_stats':     stats,
                    'total_resources': len(all_resources),
                    'subjects':        get_subjects_list(),
                },
                message='RAG system status'
            )

        except Exception as e:
            logger.error(f"RAG status error: {e}")
            return APIResponse.error(message='Failed to get status')


class RAGRebuildView(APIView):
    """
    Rebuild FAISS vectorstore index.

    POST /api/rag/rebuild/
    Body: { "force": true }
    """

    def post(self, request):
        try:
            force = request.data.get('force', False)

            from .rag_system import FAISSVectorStore
            store   = FAISSVectorStore()
            success = store.build(force_rebuild=bool(force))

            if success:
                stats = store.get_stats()
                return APIResponse.success(
                    data={
                        'rebuilt':     True,
                        'num_vectors': stats.get('num_vectors'),
                        'dimension':   stats.get('dimension'),
                        'index_path':  stats.get('index_path'),
                    },
                    message='FAISS index rebuilt successfully'
                )
            else:
                return APIResponse.error(
                    message='Failed to rebuild index'
                )

        except Exception as e:
            logger.error(f"RAG rebuild error: {e}")
            return APIResponse.error(
                message='Rebuild failed',
                errors={'detail': str(e)}
            )


class RAGResourceListView(APIView):
    """
    List all educational resources in database.

    GET /api/rag/resources/
    GET /api/rag/resources/?subject=Mathematics
    """

    def get(self, request):
        try:
            subject = request.query_params.get('subject', None)

            from .resource_loader import (
                get_all_resources,
                get_resources_by_subject,
                get_subjects_list,
            )

            if subject:
                resources = get_resources_by_subject(subject)
            else:
                resources = get_all_resources()

            return APIResponse.success(
                data={
                    'resources':       resources,
                    'count':           len(resources),
                    'subjects':        get_subjects_list(),
                    'filtered_by':     subject,
                },
                message=f'{len(resources)} resources found'
            )

        except Exception as e:
            logger.error(f"Resource list error: {e}")
            return APIResponse.error(message='Failed to list resources')


class RAGContextView(APIView):
    """
    Get RAG context for a specific weak area.
    Used for testing and debugging the RAG pipeline.

    GET /api/rag/context/?subject=Mathematics&percentage=65&severity=moderate
    """

    def get(self, request):
        try:
            subject    = request.query_params.get('subject', 'Mathematics')
            percentage = float(request.query_params.get('percentage', 70))
            severity   = request.query_params.get('severity', 'moderate')
            k          = int(request.query_params.get('k', 4))

            from .rag_system import RAGPipeline
            pipeline = RAGPipeline()
            context  = pipeline.get_context_for_weak_area(
                subject    = subject,
                percentage = percentage,
                severity   = severity,
                k          = k,
            )

            return APIResponse.success(
                data={
                    'subject':         subject,
                    'percentage':      percentage,
                    'severity':        severity,
                    'resource_count':  context['resource_count'],
                    'resources':       context['resources'],
                    'context_string':  context['context_string'],
                    'query_used':      context['query_used'],
                },
                message=f"Retrieved {context['resource_count']} resources"
            )

        except Exception as e:
            logger.error(f"RAG context error: {e}")
            return APIResponse.error(message='Failed to get context')
