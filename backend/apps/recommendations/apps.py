"""
EduSight AI — Recommendations App Config

Auto-builds FAISS index on Django startup if not present.
"""

import logging
from django.apps import AppConfig

logger = logging.getLogger('apps.recommendations')


class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'apps.recommendations'

    def ready(self):
        """
        Called when Django app is fully loaded.
        Auto-builds FAISS index if not present.
        Runs in background to not block startup.
        """
        import threading
        import os

        # Prevent double-running in dev reloader
        if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in os.sys.argv:
            return

        def build_if_needed():
            try:
                from apps.recommendations.rag_system import FAISSVectorStore
                store = FAISSVectorStore()

                if not store.index_exists():
                    logger.info(
                        "FAISS index not found. Building automatically..."
                    )
                    success = store.build()
                    if success:
                        logger.info("FAISS index built successfully on startup")
                    else:
                        logger.warning("FAISS auto-build failed")
                else:
                    logger.info("FAISS index exists. Skipping auto-build.")

            except Exception as e:
                logger.warning(f"FAISS auto-build error: {e}")

        # Run in background thread so Django startup is not delayed
        thread = threading.Thread(target=build_if_needed, daemon=True)
        thread.start()
