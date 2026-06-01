"""
EduSight AI — Celery Tasks

All heavy ML and AI operations run as background tasks.
This prevents API timeouts and keeps the server responsive.

Tasks:
    run_ml_analysis      → Full ML pipeline for a student
    run_pattern_analysis → Pattern detection only
    run_weak_area_analysis → Weak area detection only

Usage (from views.py):
    task = run_ml_analysis.delay(student_id=1)
    task_id = task.id   # Use to check status
"""

import logging
import time
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('apps.analysis')


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='analysis.run_ml_analysis',
)
def run_ml_analysis(self, student_id: int, retrain: bool = False) -> dict:
    """
    Full ML + AI analysis pipeline for a student.

    Steps:
    1. Pattern analysis
    2. Weak area detection
    3. ML predictions
    4. AI Agent Workflow (LangGraph)

    Args:
        student_id : ID of student to analyze
        retrain    : Force model retraining even if saved model exists

    Returns:
        dict with success status and results summary
    """
    from apps.students.models import AnalysisLog, Student
    from .ml_pipeline import PredictionGenerator
    from .weak_area import WeakAreaDetector
    from .pattern_analysis import PatternAnalyzer
    from .workflow import run_agent_workflow

    start_time = time.time()
    log_entry  = None

    try:
        student = Student.objects.get(pk=student_id)

        log_entry = AnalysisLog.objects.create(
            student    = student,
            agent_name = 'supervisor',
            status     = 'running',
            input_data = {
                'student_id': student_id,
                'retrain':    retrain,
                'timestamp':  timezone.now().isoformat(),
            },
        )

        logger.info(f"[Task] Step 0/4 Analysis started: student {student_id}")

        results = {}

        # ── Step 1: Pattern Analysis ──
        logger.info(f"[Task] Step 1/4 Pattern Analysis: student {student_id}")
        pattern_log = AnalysisLog.objects.create(
            student=student, agent_name='pattern_discovery',
            status='running', input_data={'student_id': student_id}
        )
        try:
            pattern_results = PatternAnalyzer(student_id).run_full_analysis()
            results['patterns'] = pattern_results
            pattern_log.mark_completed(pattern_results, time.time() - start_time)
        except Exception as e:
            pattern_log.mark_failed(str(e))
            results['patterns'] = {'success': False, 'error': str(e)}

        # ── Step 2: Weak Area Detection ──
        logger.info(f"[Task] Step 2/4 Weak Areas: student {student_id}")
        weak_log = AnalysisLog.objects.create(
            student=student, agent_name='weak_area',
            status='running', input_data={'student_id': student_id}
        )
        try:
            weak_results = WeakAreaDetector(student_id).analyze()
            results['weak_areas'] = weak_results
            weak_log.mark_completed(weak_results, time.time() - start_time)
        except Exception as e:
            weak_log.mark_failed(str(e))
            results['weak_areas'] = {'success': False, 'error': str(e)}

        # ── Step 3: ML Predictions ──
        logger.info(f"[Task] Step 3/4 ML Predictions: student {student_id}")
        pred_log = AnalysisLog.objects.create(
            student=student, agent_name='predictor',
            status='running',
            input_data={'student_id': student_id, 'retrain': retrain}
        )
        try:
            pred_results = PredictionGenerator(student_id).run(retrain=retrain)
            results['predictions'] = pred_results
            pred_log.mark_completed(pred_results, time.time() - start_time)
        except Exception as e:
            pred_log.mark_failed(str(e))
            results['predictions'] = {'success': False, 'error': str(e)}

        # ── Step 4: AI Agent Workflow ──
        logger.info(f"[Task] Step 4/4 AI Agents: student {student_id}")
        agent_log = AnalysisLog.objects.create(
            student=student, agent_name='supervisor',
            status='running',
            input_data={
                'student_id': student_id,
                'trigger': 'post_ml_pipeline',
            }
        )
        try:
            agent_results = run_agent_workflow(student_id)
            results['agents'] = agent_results
            agent_log.mark_completed(
                {
                    'completed_steps': agent_results.get('completed_steps', []),
                    'has_report':      bool(agent_results.get('final_report')),
                    'recommendations': len(
                        agent_results.get('recommendations', [])
                    ),
                },
                time.time() - start_time,
            )
        except Exception as e:
            agent_log.mark_failed(str(e))
            results['agents'] = {'success': False, 'error': str(e)}
            logger.warning(f"[Task] AI agents failed (non-fatal): {e}")

        # ── Finalize ──
        execution_time = time.time() - start_time
        log_entry.mark_completed(results, execution_time)

        logger.info(
            f"[Task] Analysis complete: student {student_id} "
            f"in {execution_time:.2f}s"
        )

        return {
            'success':        True,
            'student_id':     student_id,
            'execution_time': round(execution_time, 2),
            'results':        results,
        }

    except Exception as exc:
        execution_time = time.time() - start_time
        error_msg = str(exc)
        logger.error(
            f"ML analysis failed for student {student_id}: {error_msg}"
        )

        if log_entry:
            log_entry.mark_failed(error_msg)

        try:
            raise self.retry(exc=exc, countdown=30)
        except self.MaxRetriesExceededError:
            return {
                'success':    False,
                'student_id': student_id,
                'error':      error_msg,
            }


@shared_task(name='analysis.run_pattern_analysis')
def run_pattern_analysis(student_id: int) -> dict:
    """Run only pattern analysis (faster, used for refresh)."""
    from .pattern_analysis import PatternAnalyzer
    analyzer = PatternAnalyzer(student_id)
    return analyzer.run_full_analysis()


@shared_task(name='analysis.run_weak_area_analysis')
def run_weak_area_analysis(student_id: int) -> dict:
    """Run only weak area detection."""
    from .weak_area import WeakAreaDetector
    detector = WeakAreaDetector(student_id)
    return detector.analyze()
