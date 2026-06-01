"""
EduSight AI — Chat Engine

LangChain-powered conversational interface.
Answers questions about student performance
using real database context + conversation memory.
"""

import logging
from apps.analysis.llm_factory import LLMFactory
from apps.analysis.data_loader import load_student_context

logger = logging.getLogger('apps.chat')


def build_system_prompt(context: dict) -> str:
    """Build data-grounded system prompt for chat."""
    marks    = context.get('marks_summary', {})
    preds    = context.get('ml_predictions', [])
    weak     = context.get('weak_areas_data', [])
    patterns = context.get('pattern_data', {})
    trend    = patterns.get('overall_trend', {})

    subject_lines = "\n".join([
        f"  {subj}: {avg}%"
        for subj, avg in marks.get('subject_averages', {}).items()
    ]) or "  No subject data yet"

    pred_lines = "\n".join([
        f"  {p['subject']}: {p['predicted_marks']}% "
        f"(confidence {round(p['confidence']*100)}%)"
        for p in preds[:5]
    ]) or "  No predictions yet"

    weak_lines = "\n".join([
        f"  {w['subject']}: {w['current_percentage']}% "
        f"({w['severity']})"
        for w in weak[:4]
    ]) or "  No weak areas identified"

    return f"""You are EduSight AI, an intelligent academic performance assistant.

You are talking with: {context.get('student_name', 'Student')}
Grade Level: {context.get('grade_level', 'Unknown')}

PERFORMANCE DATA:
Overall Average: {marks.get('overall_avg', 0)}%
Total Exams: {marks.get('total_exams', 0)}
Subjects: {', '.join(marks.get('subjects', []))}

SUBJECT AVERAGES:
{subject_lines}

PREDICTED NEXT SCORES:
{pred_lines}

WEAK AREAS:
{weak_lines}

PERFORMANCE TREND:
  Direction: {trend.get('direction', 'stable')}
  Description: {trend.get('description', 'Performance is steady')}

RULES:
1. Answer ONLY from the data above. Never invent numbers.
2. If data is unavailable, say so clearly.
3. Be specific with subject names and percentages from above.
4. Keep answers to 2-4 sentences unless more detail is needed.
5. Be encouraging but honest. Professional but warm.
6. Suggest concrete actions when asked for advice."""


class ChatEngine:
    """Handles student chat with LangChain + conversation memory."""

    def __init__(self, student_id: int):
        self.student_id = student_id
        self.llm        = LLMFactory.create(temperature=0.6)
        self.context    = None

    def _load_context(self) -> dict:
        """Load and cache student context from database."""
        if self.context is None:
            try:
                self.context = load_student_context(self.student_id)
            except Exception as e:
                logger.error(f"Context load failed for student {self.student_id}: {e}")
                self.context = {
                    'student_name':  'Student',
                    'grade_level':   10,
                    'marks_summary': {
                        'overall_avg':      0,
                        'total_exams':      0,
                        'subjects':         [],
                        'subject_averages': {},
                    },
                    'ml_predictions':  [],
                    'weak_areas_data': [],
                    'pattern_data':    {},
                }
        return self.context

    def _get_history(self, limit: int = 6) -> str:
        """Load recent conversation history from database."""
        from apps.students.models import ChatMessage
        try:
            msgs = ChatMessage.objects.filter(
                student_id=self.student_id
            ).order_by('-created_at')[:limit]

            lines = []
            for msg in reversed(list(msgs)):
                role = "Human" if msg.role == 'user' else "Assistant"
                lines.append(f"{role}: {msg.content}")
            return "\n".join(lines)
        except Exception:
            return ""

    def generate_response(self, user_message: str) -> str:
        """Generate AI response grounded in real student data."""
        logger.info(
            f"Chat: student={self.student_id}, "
            f"msg='{user_message[:60]}'"
        )

        context = self._load_context()
        system  = build_system_prompt(context)
        history = self._get_history()

        if history:
            full_prompt = (
                f"{system}\n\n"
                f"CONVERSATION HISTORY:\n{history}\n\n"
                f"Human: {user_message}\n\n"
                f"Assistant:"
            )
        else:
            full_prompt = (
                f"{system}\n\n"
                f"Human: {user_message}\n\n"
                f"Assistant:"
            )

        try:
            response = self.llm.invoke(full_prompt)
            answer   = response.content.strip()

            # Remove "Assistant:" prefix if LLM echoes it back
            if answer.lower().startswith('assistant:'):
                answer = answer[10:].strip()

            return answer

        except Exception as e:
            logger.error(f"Chat generation failed: {e}")
            return (
                "I encountered an issue generating a response. "
                "Please try again, or ensure that analysis has been "
                "run for your profile by clicking Run Analysis on the dashboard."
            )
