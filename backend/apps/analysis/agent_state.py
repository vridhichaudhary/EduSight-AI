"""
EduSight AI — LangGraph Agent State

The AgentState TypedDict is the shared data structure
that flows through all agents in the LangGraph workflow.

Each agent:
1. Receives the full state
2. Reads relevant fields
3. Writes its output to designated fields
4. Returns the updated state

Fields are populated progressively as agents execute:
    supervisor    → sets routing decisions
    pattern_agent → populates pattern_findings
    predictor     → populates prediction_insights
    weak_area     → populates weak_area_insights
    recommender   → populates recommendations
    synthesis     → populates final_report
"""

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """
    Shared state flowing through all agents.
    All fields Optional because they populate progressively.
    """

    # ── Input ──────────────────────────────────────
    student_id:   int
    student_name: str
    grade_level:  int

    # ── Raw Data (loaded once, shared across agents) ──
    marks_summary:    Optional[Dict[str, Any]]
    # {
    #   subjects: [str],
    #   total_exams: int,
    #   overall_avg: float,
    #   subject_averages: {subject: avg},
    #   recent_trend: str,
    # }

    ml_predictions:   Optional[List[Dict[str, Any]]]
    # [{ subject, predicted_marks, confidence, is_at_risk }]

    weak_areas_data:  Optional[List[Dict[str, Any]]]
    # [{ subject, current_percentage, severity, reason }]

    pattern_data:     Optional[Dict[str, Any]]
    # { overall_trend, subject_trends, correlations, outliers }

    # ── Agent Outputs ───────────────────────────────
    pattern_findings:    Optional[str]
    # Natural language summary of patterns

    prediction_insights: Optional[str]
    # Natural language explanation of predictions

    weak_area_insights:  Optional[str]
    # Prioritized weak areas with reasoning

    recommendations:     Optional[List[Dict[str, Any]]]
    # [{ subject, title, description, resources, hours_per_week }]

    final_report:        Optional[str]
    # Comprehensive natural language report

    # ── Control Flow ────────────────────────────────
    current_agent:   Optional[str]
    errors:          Optional[List[str]]
    completed_steps: Optional[List[str]]

    # ── Metadata ────────────────────────────────────
    agent_run_id:    Optional[str]
    tokens_used:     Optional[int]
