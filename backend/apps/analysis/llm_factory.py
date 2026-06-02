"""
EduSight AI — LLM Factory

Creates LLM instances for agents.
Supports:
    - Gemini 1.5 Pro (production)
    - Gemini 1.5 Flash (cheaper option for simple tasks)
    - MockLLM (development without API key)

Usage:
    llm = LLMFactory.create()
    response = llm.invoke("Your prompt here")
    print(response.content)
"""

import os
import logging
from typing import Any

logger = logging.getLogger('apps.analysis')


class MockLLMResponse:
    """
    Mimics LangChain AIMessage response.
    Used when no API key is configured.
    """

    def __init__(self, content: str):
        self.content         = content
        self.response_metadata = {'model': 'mock', 'tokens': 0}


class MockLLM:
    """
    Mock LLM for development without API key.
    Returns realistic structured responses for each prompt type.
    """

    MOCK_RESPONSES = {
        'pattern': (
            "Performance analysis shows a generally positive trajectory. "
            "The student demonstrates consistent improvement in core subjects "
            "over the past assessment period. Mathematics shows the strongest "
            "upward trend (+3.2% per exam), while Science exhibits some "
            "volatility that warrants attention. Subject correlations suggest "
            "that performance in Mathematics positively influences Physics "
            "outcomes. No significant seasonal performance dips detected. "
            "Overall learning momentum is building positively."
        ),
        'prediction': (
            "Based on current performance trajectory and historical patterns, "
            "the student is projected to maintain or improve scores in most "
            "subjects. Mathematics forecast of 87% reflects consistent "
            "practice and conceptual understanding. English prediction of 91% "
            "indicates strong writing skills development. Science at 76% "
            "suggests moderate improvement potential if foundational concepts "
            "are reinforced. Students performing at this level typically "
            "respond well to targeted practice in identified weak areas. "
            "Confidence intervals are moderate, reflecting sufficient "
            "historical data for reliable forecasting."
        ),
        'weak_area': (
            "Analysis identifies two primary areas requiring immediate focus. "
            "Science (72%) represents the highest priority intervention area "
            "with a 13% gap from target performance. The root cause appears "
            "to be inconsistent scores in lab-based assessments, suggesting "
            "practical application skills need development alongside theory. "
            "History (68%) is the secondary concern, with performance "
            "declining steadily over the last three assessments. Memorization "
            "and analytical essay skills appear to be the limiting factors. "
            "Addressing these two subjects first will have the greatest "
            "positive impact on overall GPA."
        ),
        'recommend': (
            '{"title": "Focused Science Review", "description": "Dedicate 4 hours weekly to conceptual review using Khan Academy.", "study_hours_per_week": 4, "study_frequency": "3x_per_week", "topics_to_focus": ["Cellular biology", "Chemical reactions"], "resources": [{"title": "Khan Academy Biology", "type": "video", "url": "https://khanacademy.org/biology", "difficulty": "intermediate"}]}'
        ),
        'synthesis': (
            "PERFORMANCE REPORT — EduSight AI Analysis\n\n"
            "OVERALL STATUS: On Track with Improvement Areas\n\n"
            "This student demonstrates solid academic performance with "
            "clear strengths in Mathematics (88%) and English (91%). "
            "The upward performance trend over the past quarter is "
            "encouraging and reflects consistent study habits.\n\n"
            "KEY FINDINGS:\n"
            "• Strong: Mathematics, English show excellent performance\n"
            "• Improving: Computer Science trending upward\n"
            "• Needs Attention: Science and History require focused effort\n\n"
            "PRIORITY ACTIONS:\n"
            "1. Science — 4hrs/week focused on practical concepts\n"
            "2. History — 3hrs/week analytical essay practice\n"
            "3. Maintain current Mathematics study schedule\n\n"
            "PREDICTED OUTCOME: With targeted intervention in weak areas, "
            "overall GPA is projected to improve by 4-6% next semester.\n\n"
            "Continue current momentum. Small consistent improvements "
            "compound significantly over time."
        ),
        'default': (
            "Analysis complete. The student shows overall satisfactory "
            "performance with specific areas identified for improvement. "
            "Structured study plans have been generated based on "
            "individual performance patterns and learning objectives."
        ),
    }

    def invoke(self, prompt: Any) -> MockLLMResponse:
        """Return appropriate mock response based on prompt content."""
        prompt_text = (
            prompt if isinstance(prompt, str)
            else str(prompt)
        ).lower()

        if 'pattern' in prompt_text or 'trend' in prompt_text:
            content = self.MOCK_RESPONSES['pattern']
        elif 'predict' in prompt_text or 'forecast' in prompt_text:
            content = self.MOCK_RESPONSES['prediction']
        elif 'weak' in prompt_text or 'improve' in prompt_text:
            content = self.MOCK_RESPONSES['weak_area']
        elif 'recommend' in prompt_text or 'study coach' in prompt_text:
            content = self.MOCK_RESPONSES['recommend']
        elif 'synthesis' in prompt_text or 'report' in prompt_text:
            content = self.MOCK_RESPONSES['synthesis']
        else:
            content = self.MOCK_RESPONSES['default']

        logger.debug("MockLLM response generated")
        return MockLLMResponse(content)

    def __call__(self, prompt: Any) -> MockLLMResponse:
        return self.invoke(prompt)


class LLMFactory:
    """
    Factory for creating LLM instances.

    Priority:
    1. Gemini (if GOOGLE_API_KEY set)
    2. MockLLM (no API key)
    """

    @staticmethod
    def create(
        model:       str   = 'gemini-2.5-flash',
        temperature: float = 0.7,
        max_tokens:  int   = 1000,
    ):
        """
        Create and return appropriate LLM instance.
        """
        api_key = os.getenv('GOOGLE_API_KEY', '')

        if not api_key or api_key == 'your_actual_gemini_key_here':
            logger.warning(
                "GOOGLE_API_KEY not set. "
                "Using MockLLM for development. "
                "Set real API key in backend/.env for production."
            )
            return MockLLM()

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                max_output_tokens=max_tokens,
                google_api_key=api_key,
                timeout=30,
            )

            logger.info(f"LLM created: {model}")
            return llm

        except ImportError:
            logger.error(
                "langchain-google-genai not installed. "
                "Run: pip install langchain-google-genai"
            )
            return MockLLM()

        except Exception as e:
            logger.error(f"LLM creation failed: {e}. Using MockLLM.")
            return MockLLM()

    @staticmethod
    def create_fast():
        """
        Create faster, cheaper LLM for simple tasks.
        Uses gemini-2.5-flash.
        """
        return LLMFactory.create(
            model='gemini-2.5-flash',
            temperature=0.5,
            max_tokens=600,
        )
