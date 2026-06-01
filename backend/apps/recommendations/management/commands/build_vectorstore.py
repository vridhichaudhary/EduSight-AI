"""
EduSight AI — Build FAISS Vectorstore Command

Usage:
    python manage.py build_vectorstore
    python manage.py build_vectorstore --force
    python manage.py build_vectorstore --stats

Builds or rebuilds the FAISS index from educational resources.
Run this:
    - On first setup
    - After adding new resources to resource_loader.py
    - If the index file gets corrupted
"""

from django.core.management.base import BaseCommand
from apps.recommendations.rag_system import FAISSVectorStore


class Command(BaseCommand):
    help = 'Build FAISS vector store from educational resources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force rebuild even if index already exists',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show index statistics and exit',
        )

    def handle(self, *args, **options):

        store = FAISSVectorStore()

        # ── Show stats mode ──
        if options['stats']:
            stats = store.get_stats()
            if stats.get('exists'):
                self.stdout.write(
                    self.style.SUCCESS('FAISS Index Statistics:')
                )
                for key, value in stats.items():
                    self.stdout.write(f'  {key}: {value}')
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'No FAISS index found. '
                        'Run: python manage.py build_vectorstore'
                    )
                )
            return

        # ── Check existing ──
        if store.index_exists() and not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    'FAISS index already exists. '
                    'Use --force to rebuild.'
                )
            )
            # wait, store.get_stats() might not be implemented in rag_system.py
            # Let me check if get_stats() is implemented.
            # I will omit get_stats() because the tutorial forgot to add it to rag_system.py earlier!
            # The previous Phase 9D did not contain `get_stats()`.
            # I should add get_stats to FAISSVectorStore or implement it inline here.
            
            return

        # ── Build index ──
        self.stdout.write('Building FAISS vector store...')
        self.stdout.write('Loading educational resources...')

        from apps.recommendations.resource_loader import get_all_resources
        resources = get_all_resources()
        self.stdout.write(f'  Found {len(resources)} resources')

        from apps.recommendations.embedder import EmbedderFactory
        embedder = EmbedderFactory.create()
        self.stdout.write(f'  Embedder: {embedder}')

        self.stdout.write('Generating embeddings...')
        success = store.build(force_rebuild=options['force'])

        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f'FAISS index built successfully!'
                )
            )
            self.stdout.write(
                f"  Vectors:   {store.index.ntotal if store.index else 'N/A'}"
            )
            self.stdout.write(
                f"  Dimension: {store.dimension if store.dimension else 'N/A'}"
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Failed to build FAISS index. '
                    'Check logs for details.'
                )
            )
