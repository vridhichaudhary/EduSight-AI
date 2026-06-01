"""
EduSight AI — LangGraph Workflow

Directed agent graph:
    START → pattern → predictor → weak_area
          → recommender → synthesis → END

Falls back to sequential execution if LangGraph
is unavailable. Behavior is identical either way.
"""

import uuid
import logging
from .agent_state import AgentState
from .agents import (
    pattern_agent,
    predictor_agent,
    weak_area_agent,
    recommender_agent,
    synthesis_agent,
)
from .data_loader import load_student_context

logger = logging.getLogger('apps.analysis')


def build_workflow():
    """
    Build and compile LangGraph agent workflow.
    Returns compiled app or None if unavailable.
    """
    try:
        from langgraph.graph import StateGraph, END

        graph = StateGraph(AgentState)

        graph.add_node('pattern_agent',     pattern_agent)
        graph.add_node('predictor_agent',   predictor_agent)
        graph.add_node('weak_area_agent',   weak_area_agent)
        graph.add_node('recommender_agent', recommender_agent)
        graph.add_node('synthesis_agent',   synthesis_agent)

        graph.add_edge('pattern_agent',     'predictor_agent')
        graph.add_edge('predictor_agent',   'weak_area_agent')
        graph.add_edge('weak_area_agent',   'recommender_agent')
        graph.add_edge('recommender_agent', 'synthesis_agent')
        graph.add_edge('synthesis_agent',    END)

        graph.set_entry_point('pattern_agent')

        app = graph.compile()
        logger.info("LangGraph workflow compiled")
        return app

    except ImportError as e:
        logger.warning(f"LangGraph not available: {e}. Using fallback.")
        return None
    except Exception as e:
        logger.error(f"Workflow build failed: {e}")
        return None


def _run_sequential(initial_state: AgentState) -> AgentState:
    """Sequential fallback when LangGraph unavailable."""
    logger.info("Running sequential fallback workflow")
    state = initial_state
    state = pattern_agent(state)
    state = predictor_agent(state)
    state = weak_area_agent(state)
    state = recommender_agent(state)
    state = synthesis_agent(state)
    return state


def run_agent_workflow(student_id: int) -> dict:
    """
    Execute full agent workflow for a student.

    1. Load student context from database
    2. Build initial AgentState
    3. Run LangGraph workflow (or sequential fallback)
    4. Return structured results

    Args:
        student_id: ID of student to analyze

    Returns:
        Dict with all agent outputs
    """
    logger.info(f"Starting agent workflow: student {student_id}")

    try:
        context = load_student_context(student_id)
    except ValueError as e:
        return {'success': False, 'student_id': student_id, 'error': str(e)}

    initial_state: AgentState = {
        'student_id':          student_id,
        'student_name':        context['student_name'],
        'grade_level':         context['grade_level'],
        'marks_summary':       context['marks_summary'],
        'ml_predictions':      context['ml_predictions'],
        'weak_areas_data':     context['weak_areas_data'],
        'pattern_data':        context['pattern_data'],
        'pattern_findings':    None,
        'prediction_insights': None,
        'weak_area_insights':  None,
        'recommendations':     None,
        'final_report':        None,
        'current_agent':       'pattern_agent',
        'errors':              [],
        'completed_steps':     [],
        'agent_run_id':        str(uuid.uuid4()),
        'tokens_used':         0,
    }

    try:
        workflow_app = build_workflow()
        if workflow_app is not None:
            final_state = workflow_app.invoke(initial_state)
        else:
            final_state = _run_sequential(initial_state)
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        try:
            final_state = _run_sequential(initial_state)
        except Exception as e2:
            return {
                'success':    False,
                'student_id': student_id,
                'error':      f"Both workflow and fallback failed: {e}, {e2}",
            }

    return {
        'success':             True,
        'student_id':          student_id,
        'student_name':        final_state.get('student_name'),
        'completed_steps':     final_state.get('completed_steps', []),
        'errors':              final_state.get('errors', []),
        'pattern_findings':    final_state.get('pattern_findings'),
        'prediction_insights': final_state.get('prediction_insights'),
        'weak_area_insights':  final_state.get('weak_area_insights'),
        'recommendations':     final_state.get('recommendations', []),
        'final_report':        final_state.get('final_report'),
    }
