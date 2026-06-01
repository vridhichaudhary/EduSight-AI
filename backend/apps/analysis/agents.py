"""
EduSight AI — LangGraph Agent Definitions

5 Specialized Agents:
    1. pattern_agent     → Analyzes performance trends
    2. predictor_agent   → Interprets ML predictions
    3. weak_area_agent   → Prioritizes improvement areas
    4. recommender_agent → Generates study plans
    5. synthesis_agent   → Creates final comprehensive report

Each agent function:
    - Takes AgentState as input
    - Reads relevant data from state
    - Builds a structured LLM prompt
    - Calls LLM for reasoning
    - Writes output back to state
    - Returns updated state

LangGraph workflow connects these as directed graph nodes.
"""

import logging
import json
from typing import Any
from .agent_state import AgentState
from .llm_factory import LLMFactory

logger = logging.getLogger('apps.analysis')


# ─────────────────────────────────────────────
# AGENT 1: PATTERN DISCOVERY AGENT
# ─────────────────────────────────────────────
def pattern_agent(state: AgentState) -> AgentState:
    """
    Analyzes temporal patterns in student performance.

    Reads:
        state['marks_summary']
        state['pattern_data']

    Writes:
        state['pattern_findings'] → Natural language insights
        state['completed_steps']  → Appends 'pattern'
    """
    logger.info(
        f"Pattern Agent running for student {state['student_id']}"
    )

    try:
        marks     = state.get('marks_summary', {})
        patterns  = state.get('pattern_data', {})
        student   = state.get('student_name', 'the student')

        overall_trend   = patterns.get('overall_trend', {})
        subject_trends  = patterns.get('subject_trends', [])
        correlations    = patterns.get('correlations', [])
        outliers        = patterns.get('outliers', [])

        # ── Format data for prompt ──
        trend_summary = "\n".join([
            f"  - {t['subject']}: {t['direction']} "
            f"(avg: {t['avg']}%, slope: {t['slope']})"
            for t in subject_trends[:6]
        ]) or "  No subject trend data available"

        corr_summary = "\n".join([
            f"  - {c['subject_a']} ↔ {c['subject_b']}: "
            f"{c['correlation']} ({c['type']})"
            for c in correlations[:3]
        ]) or "  No significant correlations found"

        outlier_summary = "\n".join([
            f"  - {o['type'].upper()} score in {o['subject']}: "
            f"{o['percentage']}% on {o['exam_date']}"
            for o in outliers[:3]
        ]) or "  No outliers detected"

        # ── Build prompt ──
        prompt = f"""You are an expert educational data analyst for EduSight AI.

Analyze the performance patterns for student: {student}
Grade Level: {state.get('grade_level', 'Unknown')}
Overall Average: {marks.get('overall_avg', 0)}%
Total Exams: {marks.get('total_exams', 0)}
Subjects: {', '.join(marks.get('subjects', []))}

OVERALL TREND:
  Direction: {overall_trend.get('direction', 'stable')}
  Slope: {overall_trend.get('slope', 0)} per exam
  Description: {overall_trend.get('description', '')}

SUBJECT-WISE TRENDS:
{trend_summary}

SUBJECT CORRELATIONS:
{corr_summary}

OUTLIER PERFORMANCES:
{outlier_summary}

Write a concise 2-3 paragraph analysis of these patterns.
Focus on:
1. What the overall trend means for this student
2. Which subjects show the most significant changes
3. Any important correlations or outliers to highlight

Be specific with numbers. Use professional but accessible language.
Do NOT use bullet points. Write flowing paragraphs.
Keep it under 200 words."""

        # ── Call LLM ──
        llm      = LLMFactory.create()
        response = llm.invoke(prompt)
        findings = response.content.strip()

        # ── Update state ──
        completed = state.get('completed_steps') or []
        completed.append('pattern')

        logger.info("Pattern Agent complete")

        return {
            **state,
            'pattern_findings': findings,
            'current_agent':    'predictor',
            'completed_steps':  completed,
        }

    except Exception as e:
        logger.error(f"Pattern Agent error: {str(e)}")
        errors = state.get('errors') or []
        errors.append(f"pattern_agent: {str(e)}")
        return {
            **state,
            'pattern_findings': (
                "Pattern analysis encountered an error. "
                "Please retry the analysis."
            ),
            'current_agent':   'predictor',
            'errors':          errors,
        }


# ─────────────────────────────────────────────
# AGENT 2: PREDICTIVE ANALYTICS AGENT
# ─────────────────────────────────────────────
def predictor_agent(state: AgentState) -> AgentState:
    """
    Interprets ML predictions and generates forecasts narrative.

    Reads:
        state['ml_predictions']
        state['marks_summary']

    Writes:
        state['prediction_insights'] → Natural language forecast
        state['completed_steps']     → Appends 'predictor'
    """
    logger.info(
        f"Predictor Agent running for student {state['student_id']}"
    )

    try:
        predictions = state.get('ml_predictions', [])
        marks       = state.get('marks_summary', {})
        student     = state.get('student_name', 'the student')

        if not predictions:
            completed = state.get('completed_steps') or []
            completed.append('predictor')
            return {
                **state,
                'prediction_insights': (
                    "No ML predictions available yet. "
                    "Run the ML pipeline first to generate forecasts."
                ),
                'current_agent':   'weak_area',
                'completed_steps': completed,
            }

        # ── Format predictions for prompt ──
        pred_text = "\n".join([
            f"  - {p['subject']}: {p['predicted_marks']}% "
            f"(confidence: {round(p['confidence'] * 100)}%, "
            f"range: {p.get('lower_bound', 'N/A')}-{p.get('upper_bound', 'N/A')}%, "
            f"risk: {'YES' if p['is_at_risk'] else 'NO'})"
            for p in predictions
        ])

        at_risk = [p for p in predictions if p['is_at_risk']]
        strong  = [
            p for p in predictions
            if p['predicted_marks'] >= 80
        ]

        # ── Build prompt ──
        prompt = f"""You are an expert academic counselor for EduSight AI.

Interpret these ML-generated exam score predictions for: {student}
Current Overall Average: {marks.get('overall_avg', 0)}%
Model Used: {predictions[0].get('model_name', 'ML Model') if predictions else 'N/A'}

PREDICTIONS FOR NEXT EXAM:
{pred_text}

AT-RISK SUBJECTS (predicted below 60%): {
    ', '.join([p['subject'] for p in at_risk]) or 'None'
}
STRONG SUBJECTS (predicted above 80%): {
    ', '.join([p['subject'] for p in strong]) or 'None'
}

Write a 2-3 paragraph interpretation of these predictions.
Focus on:
1. What the forecasts suggest about overall academic trajectory
2. Which predictions are concerning and why
3. What these numbers mean practically for the student

Be specific with the percentages. Acknowledge model confidence.
Use encouraging but honest language. Under 200 words.
Do NOT use bullet points. Write flowing paragraphs."""

        # ── Call LLM ──
        llm      = LLMFactory.create()
        response = llm.invoke(prompt)
        insights = response.content.strip()

        # ── Update state ──
        completed = state.get('completed_steps') or []
        completed.append('predictor')

        logger.info("Predictor Agent complete")

        return {
            **state,
            'prediction_insights': insights,
            'current_agent':       'weak_area',
            'completed_steps':     completed,
        }

    except Exception as e:
        logger.error(f"Predictor Agent error: {str(e)}")
        errors = state.get('errors') or []
        errors.append(f"predictor_agent: {str(e)}")
        return {
            **state,
            'prediction_insights': (
                "Prediction interpretation encountered an error."
            ),
            'current_agent':   'weak_area',
            'errors':          errors,
        }


# ─────────────────────────────────────────────
# AGENT 3: WEAK AREA IDENTIFICATION AGENT
# ─────────────────────────────────────────────
def weak_area_agent(state: AgentState) -> AgentState:
    """
    Prioritizes weak areas and explains improvement strategy.

    Reads:
        state['weak_areas_data']
        state['pattern_findings']

    Writes:
        state['weak_area_insights'] → Prioritized analysis
        state['completed_steps']    → Appends 'weak_area'
    """
    logger.info(
        f"Weak Area Agent running for student {state['student_id']}"
    )

    try:
        weak_areas = state.get('weak_areas_data', [])
        student    = state.get('student_name', 'the student')
        marks      = state.get('marks_summary', {})

        if not weak_areas:
            completed = state.get('completed_steps') or []
            completed.append('weak_area')
            return {
                **state,
                'weak_area_insights': (
                    f"No significant weak areas detected for {student}. "
                    f"Overall performance is above threshold in all subjects. "
                    f"Focus on maintaining current performance levels."
                ),
                'current_agent':   'recommender',
                'completed_steps': completed,
            }

        # ── Format weak areas ──
        weak_text = "\n".join([
            f"  {i+1}. {w['subject']} — {w['current_percentage']}% "
            f"(severity: {w['severity']}, "
            f"gap: {w['gap_from_target']}% below target, "
            f"rank: #{w['priority_rank'] + 1})"
            for i, w in enumerate(weak_areas[:6])
        ])

        critical = [
            w for w in weak_areas
            if w['severity'] in ('critical', 'severe')
        ]

        # ── Build prompt ──
        prompt = f"""You are an expert learning specialist for EduSight AI.

Analyze weak areas for student: {student}
Overall Average: {marks.get('overall_avg', 0)}%
Total Subjects: {len(marks.get('subjects', []))}

IDENTIFIED WEAK AREAS (ranked by priority):
{weak_text}

CRITICAL/SEVERE AREAS NEEDING IMMEDIATE ATTENTION:
{', '.join([w['subject'] for w in critical]) or 'None'}

Write a focused 2-3 paragraph analysis covering:
1. The most critical subject(s) and why they need priority attention
2. The root causes of underperformance based on severity patterns
3. A realistic outlook for improvement if targeted study is applied

Be direct and actionable. Use the actual percentages.
Avoid generic advice. Under 180 words.
Do NOT use bullet points. Write flowing paragraphs."""

        # ── Call LLM ──
        llm      = LLMFactory.create()
        response = llm.invoke(prompt)
        insights = response.content.strip()

        # ── Update state ──
        completed = state.get('completed_steps') or []
        completed.append('weak_area')

        logger.info("Weak Area Agent complete")

        return {
            **state,
            'weak_area_insights': insights,
            'current_agent':      'recommender',
            'completed_steps':    completed,
        }

    except Exception as e:
        logger.error(f"Weak Area Agent error: {str(e)}")
        errors = state.get('errors') or []
        errors.append(f"weak_area_agent: {str(e)}")
        return {
            **state,
            'weak_area_insights': (
                "Weak area analysis encountered an error."
            ),
            'current_agent':   'recommender',
            'errors':          errors,
        }


# ─────────────────────────────────────────────
# AGENT 4: RECOMMENDATION ENGINE AGENT
# ─────────────────────────────────────────────
def recommender_agent(state: AgentState) -> AgentState:
    """
    Reads weak areas from state.
    Uses RAG to retrieve real study resources from FAISS.
    Generates structured recommendations grounded in real materials.
    Saves each recommendation to database.
    """
    logger.info(
        f"[Agent 4] Recommender Agent (RAG) "
        f"→ student {state['student_id']}"
    )

    try:
        weak_areas = state.get('weak_areas_data', [])
        student    = state.get('student_name', 'Student')
        student_id = state.get('student_id')
        grade      = state.get('grade_level', 10)
        completed  = list(state.get('completed_steps') or [])

        if not weak_areas:
            completed.append('recommender')
            return {
                **state,
                'recommendations': [],
                'current_agent':   'synthesis',
                'completed_steps': completed,
            }

        # ── Initialize RAG pipeline ──
        try:
            from apps.recommendations.rag_system import RAGPipeline
            rag = RAGPipeline()
            rag_available = True
            logger.info("[Agent 4] RAG pipeline initialized")
        except Exception as e:
            logger.warning(f"[Agent 4] RAG unavailable: {e}")
            rag_available = False
            rag = None

        recommendations = []
        llm = LLMFactory.create_fast()

        for weak in weak_areas[:3]:
            subject    = weak['subject']
            percentage = weak['current_percentage']
            severity   = weak['severity']
            gap        = weak['gap_from_target']

            # ── RAG: Retrieve real resources ──
            rag_context = ""
            retrieved_resources = []

            if rag_available and rag:
                try:
                    rag_result = rag.get_context_for_weak_area(
                        subject    = subject,
                        percentage = percentage,
                        severity   = severity,
                        k          = 4,
                    )
                    rag_context         = rag_result['context_string']
                    retrieved_resources = rag_result['resources']

                    logger.info(
                        f"[Agent 4] RAG retrieved "
                        f"{len(retrieved_resources)} resources "
                        f"for {subject}"
                    )
                except Exception as e:
                    logger.warning(f"[Agent 4] RAG search failed: {e}")
                    rag_context = ""

            # ── Build RAG-grounded prompt ──
            prompt = f"""You are an expert study coach for EduSight AI.

Create a specific study recommendation for:
Student: {student}
Grade: {grade}
Subject: {subject}
Current Score: {percentage}%
Severity: {severity}
Gap from Target: {gap}%

{rag_context}

Return ONLY a JSON object. No text before or after. No markdown.
{{
  "title": "specific actionable title (max 60 chars)",
  "description": "2 sentences: what to do and why (max 150 chars)",
  "study_hours_per_week": <integer 2-8>,
  "study_frequency": "<daily|3x_per_week|2x_per_week>",
  "topics_to_focus": ["specific topic 1", "specific topic 2", "specific topic 3"],
  "resources": [
    {{
      "title": "use exact title from retrieved resources above",
      "type": "<video|article|practice|book|interactive>",
      "url": "use exact URL from retrieved resources above",
      "difficulty": "<beginner|intermediate|advanced>"
    }}
  ]
}}

IMPORTANT: Use the exact titles and URLs from the RETRIEVED STUDY
RESOURCES section above. Do not invent URLs."""

            try:
                response = llm.invoke(prompt)
                content  = response.content.strip()

                # Clean markdown fences
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]

                rec_data = json.loads(content.strip())

                # Inject retrieved resources if LLM didn't use them
                if not rec_data.get('resources') and retrieved_resources:
                    rec_data['resources'] = [
                        {
                            'title':      r['title'],
                            'type':       r['type'],
                            'url':        r['url'],
                            'difficulty': r['difficulty'],
                        }
                        for r in retrieved_resources[:3]
                    ]

                _save_recommendation(
                    student_id = student_id, 
                    subject    = subject, 
                    rec_data   = rec_data
                )

                recommendations.append({
                    'subject':         subject,
                    'title':           rec_data.get('title', ''),
                    'description':     rec_data.get('description', ''),
                    'study_hours':     rec_data.get('study_hours_per_week', 3),
                    'study_frequency': rec_data.get('study_frequency', '3x_per_week'),
                    'topics':          rec_data.get('topics_to_focus', []),
                    'resources':       rec_data.get('resources', []),
                    'rag_resources_used': len(retrieved_resources),
                })

                logger.info(
                    f"[Agent 4] Recommendation saved: {subject} "
                    f"(RAG: {len(retrieved_resources)} resources used)"
                )

            except json.JSONDecodeError:
                logger.warning(f"[Agent 4] JSON parse failed: {subject}")
                fallback = _create_fallback_recommendation(
                    subject, percentage, severity, student_id
                )
                # Inject RAG resources into fallback
                if retrieved_resources:
                    fallback['resources'] = [
                        {
                            'title':      r['title'],
                            'type':       r['type'],
                            'url':        r['url'],
                            'difficulty': r['difficulty'],
                        }
                        for r in retrieved_resources[:2]
                    ]
                recommendations.append(fallback)

            except Exception as e:
                logger.warning(
                    f"[Agent 4] Rec failed for {subject}: {e}"
                )

        completed.append('recommender')

        logger.info(
            f"[Agent 4] Recommender complete (RAG): "
            f"{len(recommendations)} recommendations"
        )

        return {
            **state,
            'recommendations': recommendations,
            'current_agent':   'synthesis',
            'completed_steps': completed,
        }

    except Exception as e:
        logger.error(f"[Agent 4] Error: {e}")
        errors = list(state.get('errors') or [])
        errors.append(f"recommender_agent: {str(e)}")
        completed = list(state.get('completed_steps') or [])
        completed.append('recommender')
        return {
            **state,
            'recommendations': [],
            'current_agent':   'synthesis',
            'errors':          errors,
            'completed_steps': completed,
        }


def _save_recommendation(student_id, subject, rec_data):
    """Save recommendation to database."""
    from apps.students.models import Student, Subject, Recommendation

    try:
        student     = Student.objects.get(pk=student_id)
        subject_obj = Subject.objects.get(name=subject)

        Recommendation.objects.update_or_create(
            student = student,
            subject = subject_obj,
            defaults={
                'title':                rec_data.get('title', f'{subject} Study Plan'),
                'description':          rec_data.get('description', ''),
                'recommendation_type':  'practice',
                'topics_to_study':      rec_data.get('topics_to_focus', []),
                'study_hours_suggested': rec_data.get('study_hours_per_week', 3),
                'study_frequency':      rec_data.get('study_frequency', '3x_per_week'),
                'resources':            rec_data.get('resources', []),
                'generated_by_agent':   'RecommenderAgent',
                'is_active':            True,
            }
        )
    except Exception as e:
        logger.warning(f"Could not save recommendation to DB: {e}")


def _create_fallback_recommendation(
    subject, percentage, severity, student_id
):
    """Create a fallback recommendation when LLM fails."""
    resources_map = {
        'Mathematics': [
            {
                'title':      'Khan Academy Math',
                'type':       'video',
                'url':        'https://www.khanacademy.org/math',
                'difficulty': 'intermediate',
            }
        ],
        'Science': [
            {
                'title':      'Khan Academy Science',
                'type':       'video',
                'url':        'https://www.khanacademy.org/science',
                'difficulty': 'intermediate',
            }
        ],
        'English': [
            {
                'title':      'Grammarly Blog',
                'type':       'article',
                'url':        'https://www.grammarly.com/blog',
                'difficulty': 'intermediate',
            }
        ],
    }

    rec = {
        'subject':         subject,
        'title':           f'Improve {subject} Performance',
        'description':     (
            f'Focused study plan to raise {subject} '
            f'from {percentage}% to target. '
            f'Consistent practice is key.'
        ),
        'study_hours':     4 if severity in ('critical', 'severe') else 3,
        'study_frequency': 'daily' if severity == 'critical' else '3x_per_week',
        'topics_to_focus': ['Core concepts', 'Practice problems', 'Past papers'],
        'resources':       resources_map.get(subject, []),
    }

    _save_recommendation(student_id, subject, {
        'title':                rec['title'],
        'description':          rec['description'],
        'study_hours_per_week': rec['study_hours'],
        'study_frequency':      rec['study_frequency'],
        'topics_to_focus':      rec['topics_to_focus'],
        'resources':            rec['resources'],
    })

    return rec


# ─────────────────────────────────────────────
# AGENT 5: SYNTHESIS AGENT (SUPERVISOR)
# ─────────────────────────────────────────────
def synthesis_agent(state: AgentState) -> AgentState:
    """
    Synthesizes all agent outputs into final report.
    Saves complete report to AnalysisLog.

    Reads:
        All previous agent outputs in state

    Writes:
        state['final_report']    → Comprehensive report
        state['completed_steps'] → Appends 'synthesis'
    """
    logger.info(
        f"Synthesis Agent running for student {state['student_id']}"
    )

    try:
        student    = state.get('student_name', 'Student')
        student_id = state.get('student_id')
        marks      = state.get('marks_summary', {})

        patterns    = state.get('pattern_findings', 'N/A')
        predictions = state.get('prediction_insights', 'N/A')
        weak_areas  = state.get('weak_area_insights', 'N/A')
        rec_count   = len(state.get('recommendations', []))
        errors      = state.get('errors', [])

        # ── Build synthesis prompt ──
        prompt = f"""You are the lead academic advisor for EduSight AI.

Create a comprehensive performance report for: {student}
Grade Level: {state.get('grade_level', 'N/A')}
Overall Average: {marks.get('overall_avg', 0)}%
Total Exams Analyzed: {marks.get('total_exams', 0)}
Subjects: {', '.join(marks.get('subjects', []))}

PATTERN ANALYSIS:
{patterns}

PREDICTION INSIGHTS:
{predictions}

WEAK AREA ANALYSIS:
{weak_areas}

STUDY PLANS GENERATED: {rec_count} personalized recommendations

Write a final comprehensive report with these sections:
1. EXECUTIVE SUMMARY (2 sentences)
2. KEY STRENGTHS (what the student is doing well)
3. PRIORITY IMPROVEMENTS (top 2-3 areas to focus on)
4. ACTION PLAN (specific next steps for the next 30 days)
5. MOTIVATIONAL CLOSE (encouraging, forward-looking)

Keep each section concise. Total under 300 words.
Use clear section headers in CAPS followed by colon.
Be specific with subject names and percentages.
Tone: Professional, supportive, actionable."""

        # ── Call LLM ──
        llm      = LLMFactory.create()
        response = llm.invoke(prompt)
        report   = response.content.strip()

        # ── Save final report to AnalysisLog ──
        try:
            from apps.students.models import Student, AnalysisLog
            student_obj = Student.objects.get(pk=student_id)

            AnalysisLog.objects.create(
                student    = student_obj,
                agent_name = 'supervisor',
                status     = 'completed',
                input_data = {
                    'agent_run_id': state.get('agent_run_id'),
                    'completed_steps': state.get('completed_steps', []),
                },
                output_data = {
                    'final_report':      report,
                    'recommendations':   state.get('recommendations', []),
                    'errors':            errors,
                    'pattern_findings':  state.get('pattern_findings', ''),
                    'weak_area_insights': state.get('weak_area_insights', ''),
                },
                execution_time_seconds = 0,
            )
        except Exception as e:
            logger.warning(f"Could not save synthesis log: {e}")

        # ── Update state ──
        completed = state.get('completed_steps') or []
        completed.append('synthesis')

        logger.info("Synthesis Agent complete")

        return {
            **state,
            'final_report':    report,
            'current_agent':   'done',
            'completed_steps': completed,
        }

    except Exception as e:
        logger.error(f"Synthesis Agent error: {str(e)}")
        errors = state.get('errors') or []
        errors.append(f"synthesis_agent: {str(e)}")

        fallback_report = (
            f"Analysis complete for {state.get('student_name', 'Student')}. "
            f"Performance data has been processed. "
            f"Please review the individual sections for detailed insights."
        )

        return {
            **state,
            'final_report':    fallback_report,
            'current_agent':   'done',
            'errors':          errors,
        }
