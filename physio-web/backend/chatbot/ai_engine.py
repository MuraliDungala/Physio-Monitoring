"""
AI Physiotherapy Assistant Chatbot Engine
Comprehensive NLP-based chatbot with context awareness, exercise guidance,
posture correction, rehabilitation support, and system data integration.

Supports optional OpenAI / LLM integration. Falls back to rule-based
pattern matching when no API key is configured.
"""

import re
import os
import random
import logging
from typing import Dict, List, Optional, Tuple

from chatbot.knowledge_base import knowledge_base, PhysioKnowledgeBase

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# OPTIONAL: OpenAI / LLM integration
# ─────────────────────────────────────────────
_openai_client = None

def _init_openai():
    """Try to initialise OpenAI client from env var OPENAI_API_KEY."""
    global _openai_client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return
    try:
        import openai
        _openai_client = openai.OpenAI(api_key=api_key)
        logger.info("✅ OpenAI client initialised for chatbot")
    except ImportError:
        logger.info("openai package not installed – using rule-based chatbot")
    except Exception as exc:
        logger.warning(f"OpenAI init failed: {exc} – falling back to rule-based chatbot")

_init_openai()

# System prompt for LLM mode
SYSTEM_PROMPT = """You are an AI Physiotherapy Assistant embedded in a rehabilitation monitoring application.
Your role is to help users perform exercises correctly, explain posture corrections, provide rehabilitation guidance, and answer physiotherapy-related questions.

Guidelines:
- Be supportive, clear, educational, and safety-focused.
- NEVER provide medical diagnoses.
- Always recommend consulting a healthcare professional for persistent pain or complex conditions.
- When exercise context is provided (current exercise, rep count, quality score, joint angle), incorporate that information into your responses.
- Keep responses concise (2-4 sentences) unless the user explicitly asks for detailed instructions.
- Use plain language; avoid jargon unless explaining a term.
- If you don't know something, say so honestly and suggest consulting a physiotherapist.
"""


class AIChatbotEngine:
    """Main chatbot engine with pattern matching + optional LLM."""

    def __init__(self):
        self.kb: PhysioKnowledgeBase = knowledge_base
        self.conversation_history: Dict[str, List[dict]] = {}  # user_id -> messages
        self._intent_patterns = self._build_intent_patterns()

    # ══════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════
    def get_response(
        self,
        user_message: str,
        exercise: Optional[str] = None,
        rep_count: Optional[int] = None,
        quality_score: Optional[float] = None,
        joint_angle: Optional[float] = None,
        posture_feedback: Optional[str] = None,
        user_id: str = "default",
    ) -> str:
        """Generate chatbot response. Tries LLM first, falls back to rule engine."""

        # Record the user message for history
        self._record_message(user_id, "user", user_message)

        context = {
            "exercise": exercise,
            "rep_count": rep_count,
            "quality_score": quality_score,
            "joint_angle": joint_angle,
            "posture_feedback": posture_feedback,
        }

        # Try LLM if available
        if _openai_client:
            try:
                response = self._llm_response(user_message, context, user_id)
                self._record_message(user_id, "assistant", response)
                return response
            except Exception as exc:
                logger.warning(f"LLM error, falling back to rules: {exc}")

        # Rule-based fallback
        response = self._rule_based_response(user_message, context)
        self._record_message(user_id, "assistant", response)
        return response

    def get_session_coaching(
        self,
        exercise: str,
        rep_count: int,
        quality_score: float,
        joint_angle: float,
        posture_feedback: str = "",
    ) -> str:
        """Generate in-session coaching message."""
        messages = []

        # Rep milestone
        if rep_count > 0 and rep_count % 5 == 0:
            messages.append(f"Great work — {rep_count} reps completed!")

        # Quality feedback
        if quality_score >= 90:
            messages.append("Excellent form! Keep it up.")
        elif quality_score >= 70:
            messages.append("Good form. Try to keep your movements smooth and controlled.")
        elif quality_score >= 50:
            messages.append("Your form could improve. Focus on slow, controlled movements and proper alignment.")
        else:
            messages.append("Focus on your form. Slow down and pay attention to your body alignment.")

        # Posture-specific
        if posture_feedback and "incorrect" in posture_feedback.lower():
            messages.append("Watch your posture — follow the correction tips on screen.")

        # Exercise-specific tips
        ex_data = self.kb.get_exercise(exercise)
        if ex_data and quality_score < 70:
            tips = ex_data.get("tips", "")
            if tips:
                messages.append(f"Tip: {tips}")

        return " ".join(messages) if messages else "Keep going, you're doing well!"

    # ══════════════════════════════════════════════
    # LLM PATH
    # ══════════════════════════════════════════════
    def _llm_response(self, user_message: str, context: dict, user_id: str) -> str:
        """Get response from OpenAI-compatible LLM."""
        system_msg = SYSTEM_PROMPT
        if any(v is not None for v in context.values()):
            ctx_parts = []
            if context["exercise"]:
                ctx_parts.append(f"Current exercise: {context['exercise']}")
            if context["rep_count"] is not None:
                ctx_parts.append(f"Rep count: {context['rep_count']}")
            if context["quality_score"] is not None:
                ctx_parts.append(f"Quality score: {context['quality_score']}%")
            if context["joint_angle"] is not None:
                ctx_parts.append(f"Joint angle: {context['joint_angle']}°")
            if context["posture_feedback"]:
                ctx_parts.append(f"Posture feedback: {context['posture_feedback']}")
            system_msg += "\n\nCurrent session context:\n" + "\n".join(ctx_parts)

        # Build messages list (keep last 10 turns for context)
        messages = [{"role": "system", "content": system_msg}]
        history = self.conversation_history.get(user_id, [])[-20:]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        completion = _openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return completion.choices[0].message.content.strip()

    # ══════════════════════════════════════════════
    # RULE-BASED PATH
    # ══════════════════════════════════════════════
    def _rule_based_response(self, user_message: str, context: dict) -> str:
        """Pattern-matching based response generation."""
        msg = user_message.lower().strip()

        # 1. Detect intent
        intent, match_data = self._detect_intent(msg)

        # 2. Route to handler
        handler_map = {
            "greeting": self._handle_greeting,
            "farewell": self._handle_farewell,
            "exercise_how": self._handle_exercise_how,
            "exercise_info": self._handle_exercise_info,
            "exercise_list": self._handle_exercise_list,
            "posture_question": self._handle_posture,
            "quality_score_question": self._handle_quality_score,
            "rep_question": self._handle_reps,
            "pain_concern": self._handle_pain,
            "tightness": self._handle_tightness,
            "safety_question": self._handle_safety,
            "warm_up": self._handle_warm_up,
            "cool_down": self._handle_cool_down,
            "frequency": self._handle_frequency,
            "motivation": self._handle_motivation,
            "rehab_stage": self._handle_rehab_stage,
            "rom_question": self._handle_rom,
            "dashboard_help": self._handle_dashboard,
            "session_data_question": self._handle_session_data,
            "ice_heat": self._handle_ice_heat,
            "soreness": self._handle_soreness,
            "thank_you": self._handle_thanks,
            "help": self._handle_help,
        }

        handler = handler_map.get(intent)
        if handler:
            return handler(msg, context, match_data)

        # Check for exercise name anywhere in message
        exercise_match = self._find_exercise_in_message(msg)
        if exercise_match:
            return self._handle_exercise_info(msg, context, exercise_match)

        # Default
        return self._handle_default(msg, context)

    # ──────────────────────────────────────────────
    # INTENT PATTERNS
    # ──────────────────────────────────────────────
    def _build_intent_patterns(self) -> List[Tuple[str, re.Pattern]]:
        """Build regex patterns for intent detection, ordered by priority."""
        patterns = [
            ("greeting", re.compile(r"^(hi|hello|hey|greetings|good\s*(morning|afternoon|evening)|howdy)\b")),
            ("farewell", re.compile(r"\b(bye|goodbye|see\s*you|exit|quit|farewell|take\s*care)\b")),
            ("thank_you", re.compile(r"\b(thank|thanks|thx|appreciate)\b")),
            ("exercise_how", re.compile(r"\b(how\s+(do|to|should)\s+(i|you|we)\s+(do|perform|execute))\b")),
            ("exercise_list", re.compile(r"\b(list|show|what)\s*(of|all|available|the)?\s*(exercises?|workouts?)\b")),
            ("posture_question", re.compile(r"\b(posture|form|alignment|position|body\s*position|why.*(incorrect|wrong|bad))\b")),
            ("quality_score_question", re.compile(r"\b(quality\s*score|score|my\s*score|rating|accuracy|performance\s*score)\b")),
            ("rep_question", re.compile(r"\b(how\s*many\s*reps|repetitions?|sets?|how\s*many\s*should|target\s*reps)\b")),
            ("pain_concern", re.compile(r"\b(pain|hurts?|hurting|ache|aching|sharp\s*pain|discomfort|ouch)\b")),
            ("tightness", re.compile(r"\b(tight|tightness|stiff|stiffness|restricted|limited)\b")),
            ("safety_question", re.compile(r"\b(safe|safety|careful|precaution|risk|dangerous|injury\s*prevent|avoid\s*injury)\b")),
            ("warm_up", re.compile(r"\b(warm\s*up|warming\s*up|before\s*exercise|prepare|preparation)\b")),
            ("cool_down", re.compile(r"\b(cool\s*down|cooling\s*down|after\s*exercise|stretch\s*after|wind\s*down)\b")),
            ("frequency", re.compile(r"\b(how\s*often|frequency|times\s*per\s*week|schedule|routine|daily|weekly)\b")),
            ("motivation", re.compile(r"\b(motivat|encourage|inspire|keep\s*going|give\s*up|struggle|hard)\b")),
            ("rehab_stage", re.compile(r"\b(rehab|rehabilitation|recovery\s*stage|phase|progress\s*stage|what\s*stage)\b")),
            ("rom_question", re.compile(r"\b(range\s*of\s*motion|rom\b|flexibility|how\s*far|joint\s*range)\b")),
            ("dashboard_help", re.compile(r"\b(dashboard|chart|graph|analytics|trend|history|data|report|insight)\b")),
            ("session_data_question", re.compile(r"\b(my\s*session|my\s*data|today.*(session|exercise|workout)|last\s*session)\b")),
            ("ice_heat", re.compile(r"\b(ice|heat|cold\s*pack|hot\s*pack|compress|inflammation|swell)\b")),
            ("soreness", re.compile(r"\b(sore|soreness|doms|muscle\s*ache|stiff\s*after|tender)\b")),
            ("help", re.compile(r"^(help|what\s*can\s*you\s*do|capabilities|features|commands|what\s*do\s*you\s*know)\b")),
        ]
        return patterns

    def _detect_intent(self, msg: str) -> Tuple[str, Optional[str]]:
        """Detect user intent using regex patterns."""
        for intent, pattern in self._intent_patterns:
            m = pattern.search(msg)
            if m:
                return intent, m.group(0)
        return "unknown", None

    def _find_exercise_in_message(self, msg: str) -> Optional[str]:
        """Try to find a known exercise name in the message."""
        for ex_name in self.kb.exercises:
            if ex_name in msg:
                return ex_name
        # Also try partial matches
        body_parts = ["shoulder", "elbow", "knee", "hip", "neck", "wrist", "back", "ankle", "squat"]
        for part in body_parts:
            if part in msg:
                return part
        return None

    # ──────────────────────────────────────────────
    # INTENT HANDLERS
    # ──────────────────────────────────────────────
    def _handle_greeting(self, msg: str, context: dict, match: str) -> str:
        greetings = [
            "Hello! I'm your AI Physiotherapy Assistant. I can help with exercise instructions, posture correction, recovery guidance, and more. What would you like to know?",
            "Hi there! I'm here to help with your physiotherapy exercises. You can ask me about specific exercises, safety tips, or your session data. How can I assist you?",
            "Welcome! I'm your virtual physio assistant. Feel free to ask me anything about exercises, posture, or your recovery progress.",
        ]
        resp = random.choice(greetings)
        if context.get("exercise"):
            resp += f"\n\nI see you're working on **{context['exercise']}**. Would you like guidance for this exercise?"
        return resp

    def _handle_farewell(self, msg: str, context: dict, match: str) -> str:
        farewells = [
            "Take care and keep up with your exercises! Remember — consistency is key to recovery. 💪",
            "Goodbye! Keep exercising safely and listen to your body. See you next time!",
            "Stay healthy! Remember to warm up, cool down, and rest when needed. See you!",
        ]
        return random.choice(farewells)

    def _handle_exercise_how(self, msg: str, context: dict, match: str) -> str:
        """Handle 'how to perform' questions."""
        # Try to find exercise name in the message
        ex_name = self._find_exercise_in_message(msg)
        if not ex_name:
            ex_name = context.get("exercise")

        if ex_name:
            ex_data = self.kb.get_exercise(ex_name)
            if ex_data:
                return self._format_exercise_instructions(ex_name, ex_data)

        return (
            "Could you tell me which exercise you'd like instructions for? "
            "I can guide you through exercises like Shoulder Abduction, Elbow Flexion, Knee Flexion, Squats, and many more."
        )

    def _handle_exercise_info(self, msg: str, context: dict, match: str) -> str:
        """Handle general exercise info requests."""
        ex_name = match if match else self._find_exercise_in_message(msg)
        if not ex_name:
            ex_name = context.get("exercise")

        if ex_name:
            ex_data = self.kb.get_exercise(ex_name)
            if ex_data:
                # Decide what info to return based on what was asked
                if any(w in msg for w in ["how", "perform", "do", "instructions", "guide", "step"]):
                    return self._format_exercise_instructions(ex_name, ex_data)
                elif any(w in msg for w in ["muscle", "work", "target"]):
                    return f"**{ex_name.title()}** targets: {ex_data['muscles']}."
                elif any(w in msg for w in ["error", "mistake", "wrong", "common"]):
                    errors = ex_data.get("common_errors", [])
                    if errors:
                        error_list = "\n".join(f"• {e}" for e in errors)
                        return f"Common mistakes during **{ex_name.title()}**:\n{error_list}\n\n💡 Tip: {ex_data.get('tips', '')}"
                else:
                    return self._format_exercise_summary(ex_name, ex_data)

            # Check if it's a body part category
            category_exercises = self.kb.get_exercises_by_category(ex_name)
            if category_exercises:
                ex_list = "\n".join(f"• {e}" for e in category_exercises)
                return f"**{ex_name.title()} Exercises:**\n{ex_list}\n\nAsk me about any specific exercise for detailed instructions!"

        return (
            "I can provide information about many physiotherapy exercises. "
            "Could you specify which exercise you're interested in?"
        )

    def _handle_exercise_list(self, msg: str, context: dict, match: str) -> str:
        all_exercises = self.kb.get_exercise_names()
        categorized = {}
        for ex_name in all_exercises:
            ex_data = self.kb.exercises.get(ex_name.lower(), {})
            cat = ex_data.get("category", "Other")
            categorized.setdefault(cat, []).append(ex_name)

        parts = ["**Available Exercises:**\n"]
        for cat in sorted(categorized):
            exercises = ", ".join(categorized[cat])
            parts.append(f"**{cat}:** {exercises}")

        parts.append("\nAsk me about any exercise for detailed instructions!")
        return "\n".join(parts)

    def _handle_posture(self, msg: str, context: dict, match: str) -> str:
        if context.get("posture_feedback"):
            feedback = context["posture_feedback"]
            # Try to match a correction
            for key, correction in self.kb.posture_corrections.items():
                if any(word in feedback.lower() for word in key.split("_")):
                    return correction
            return f"Current posture feedback: {feedback}. Focus on maintaining proper alignment and controlled movements."

        if context.get("exercise"):
            ex_data = self.kb.get_exercise(context["exercise"])
            if ex_data:
                errors = ex_data.get("common_errors", [])
                if errors:
                    return (
                        f"For **{context['exercise']}**, watch out for these posture issues:\n"
                        + "\n".join(f"• {e}" for e in errors)
                        + f"\n\n💡 Tip: {ex_data.get('tips', '')}"
                    )

        return (
            "Good posture is crucial for effective rehabilitation. Key principles:\n"
            "• Keep your back straight and core engaged\n"
            "• Relax your shoulders — don't shrug\n"
            "• Move slowly and controlled\n"
            "• Maintain proper joint alignment throughout\n\n"
            "The system provides real-time posture feedback during exercises. "
            "Follow the correction tips shown on screen."
        )

    def _handle_quality_score(self, msg: str, context: dict, match: str) -> str:
        score = context.get("quality_score")
        base = self.kb.dashboard_help["quality_score"]

        if score is not None:
            if score >= 80:
                return f"Your current quality score is **{score}%** — excellent! {base}"
            elif score >= 60:
                return (
                    f"Your current quality score is **{score}%** — good, but there's room for improvement. "
                    "Try to focus on maintaining full range of motion and smooth, controlled movements. " + base
                )
            else:
                advice = "Focus on slowing down your movements, maintaining proper posture, and achieving full range of motion."
                if context.get("exercise"):
                    ex_data = self.kb.get_exercise(context["exercise"])
                    if ex_data and ex_data.get("tips"):
                        advice += f" Tip: {ex_data['tips']}"
                return f"Your current quality score is **{score}%** — needs improvement. {advice}\n\n{base}"

        return base

    def _handle_reps(self, msg: str, context: dict, match: str) -> str:
        if context.get("exercise"):
            ex_data = self.kb.get_exercise(context["exercise"])
            if ex_data:
                current_reps = context.get("rep_count")
                target = ex_data.get("target_reps", "10-15 repetitions per set")
                resp = (
                    f"For **{context['exercise']}**, the recommended target is **{target}** "
                    f"with **{ex_data.get('target_sets', '2-3 sets')}**."
                )
                if current_reps is not None:
                    resp += f"\n\nYou've completed **{current_reps}** reps so far."
                resp += "\n\nStart with fewer reps if you're a beginner and gradually increase as you get stronger."
                return resp

        return self.kb.faq["how_many_reps"]

    def _handle_pain(self, msg: str, context: dict, match: str) -> str:
        return (
            "⚠️ **Important Safety Notice**\n\n"
            "If you are experiencing pain during exercise, **stop immediately**. "
            "Do not try to push through sharp or sudden pain.\n\n"
            + self.kb.faq["pain_during_exercise"]
            + "\n\n"
            "If the pain persists, please consult a qualified physiotherapist or your healthcare provider."
        )

    def _handle_tightness(self, msg: str, context: dict, match: str) -> str:
        resp = self.kb.faq["tight_feeling"]
        if context.get("exercise"):
            resp += f"\n\nSince you're working on **{context['exercise']}**, try some gentle warm-up movements for that area first."
        return resp

    def _handle_safety(self, msg: str, context: dict, match: str) -> str:
        tips = random.sample(self.kb.safety_guidelines, min(5, len(self.kb.safety_guidelines)))
        tip_list = "\n".join(f"• {t}" for t in tips)
        return f"**Safety Guidelines:**\n{tip_list}\n\nDo you want more specific safety advice for a particular exercise?"

    def _handle_warm_up(self, msg: str, context: dict, match: str) -> str:
        return self.kb.faq["warm_up"]

    def _handle_cool_down(self, msg: str, context: dict, match: str) -> str:
        return self.kb.faq["cool_down"]

    def _handle_frequency(self, msg: str, context: dict, match: str) -> str:
        return self.kb.faq["how_often"]

    def _handle_motivation(self, msg: str, context: dict, match: str) -> str:
        resp = self.kb.get_random_motivation()
        if context.get("rep_count") and context["rep_count"] > 0:
            resp += f"\n\nYou've already completed {context['rep_count']} reps — that's real progress!"
        if context.get("quality_score") and context["quality_score"] >= 70:
            resp += f"\n\nYour quality score of {context['quality_score']}% shows you're putting in focused effort."
        return resp

    def _handle_rehab_stage(self, msg: str, context: dict, match: str) -> str:
        stages = self.kb.rehab_stages
        parts = ["**Rehabilitation Stages:**\n"]
        for key, stage in stages.items():
            parts.append(f"**{stage['name']}**\n{stage['description']}\n")
        parts.append(
            "Your stage depends on your specific injury, timeline, and progress. "
            "If you're unsure, consult your physiotherapist for an assessment."
        )
        return "\n".join(parts)

    def _handle_rom(self, msg: str, context: dict, match: str) -> str:
        resp = self.kb.biomechanics["range_of_motion"]
        if context.get("joint_angle") is not None:
            resp += f"\n\nYour current joint angle is **{context['joint_angle']}°**."
            if context.get("exercise"):
                ex_data = self.kb.get_exercise(context["exercise"])
                if ex_data:
                    resp += f" The target ROM for {context['exercise']} is **{ex_data.get('target_rom', 'varies')}**."
        return resp

    def _handle_dashboard(self, msg: str, context: dict, match: str) -> str:
        # Try to match specific dashboard element
        for key, explanation in self.kb.dashboard_help.items():
            key_words = key.replace("_", " ").split()
            if any(w in msg for w in key_words):
                return explanation

        return (
            "**Dashboard Guide:**\n"
            "• **Quality Score** — How accurately you perform exercises (0-100%)\n"
            "• **Rep Count** — Number of completed repetitions\n"
            "• **Joint Angle** — Real-time angle at the tracked joint\n"
            "• **Posture Feedback** — Whether your body alignment is correct\n"
            "• **Session History** — Record of your past exercise sessions\n"
            "• **Progress Trends** — Charts showing improvement over time\n"
            "• **AI Insights** — AI-generated recommendations\n\n"
            "Ask me about any specific metric for more details!"
        )

    def _handle_session_data(self, msg: str, context: dict, match: str) -> str:
        parts = []
        if context.get("exercise"):
            parts.append(f"**Current Exercise:** {context['exercise']}")
        if context.get("rep_count") is not None:
            parts.append(f"**Reps Completed:** {context['rep_count']}")
        if context.get("quality_score") is not None:
            parts.append(f"**Quality Score:** {context['quality_score']}%")
        if context.get("joint_angle") is not None:
            parts.append(f"**Joint Angle:** {context['joint_angle']}°")
        if context.get("posture_feedback"):
            parts.append(f"**Posture:** {context['posture_feedback']}")

        if parts:
            return "**Your Current Session Data:**\n" + "\n".join(parts)
        return "No active session data available. Start an exercise session to see real-time metrics here!"

    def _handle_ice_heat(self, msg: str, context: dict, match: str) -> str:
        return self.kb.faq["ice_or_heat"]

    def _handle_soreness(self, msg: str, context: dict, match: str) -> str:
        return self.kb.faq["soreness_vs_pain"]

    def _handle_thanks(self, msg: str, context: dict, match: str) -> str:
        responses = [
            "You're welcome! Feel free to ask if you need anything else.",
            "Happy to help! Don't hesitate to ask more questions.",
            "Glad I could help! Keep up the great work with your exercises.",
            "Anytime! I'm here to support your recovery journey.",
        ]
        return random.choice(responses)

    def _handle_help(self, msg: str, context: dict, match: str) -> str:
        return (
            "I'm your **AI Physiotherapy Assistant**. Here's what I can help with:\n\n"
            "🏋️ **Exercise Guidance** — Instructions, tips, and common mistakes for 20+ exercises\n"
            "🧍 **Posture Correction** — Explaining form errors and how to fix them\n"
            "📊 **Dashboard Help** — Understanding your quality scores, rep counts, and progress\n"
            "🩹 **Safety & Pain** — When to stop, ice vs heat, soreness vs pain\n"
            "📈 **Rehabilitation Info** — Recovery stages, frequency, warm-up, and cool-down\n"
            "💬 **General Physio Q&A** — Range of motion, joint angles, muscle activation\n\n"
            "Just type your question naturally — I'll do my best to help!"
        )

    def _handle_default(self, msg: str, context: dict) -> str:
        defaults = [
            "I'm not sure I understood that. Could you rephrase your question? I can help with exercise guidance, posture correction, safety tips, and understanding your session data.",
            "I'd be happy to help! Try asking about a specific exercise (e.g. 'How do I perform shoulder abduction?'), posture tips, or your quality score.",
            "I'm here to help with physiotherapy questions. You can ask me about exercises, safety precautions, your dashboard metrics, or recovery advice. What would you like to know?",
        ]
        resp = random.choice(defaults)
        if context.get("exercise"):
            resp += f"\n\n💡 You're currently working on **{context['exercise']}**. Would you like guidance for this exercise?"
        return resp

    # ──────────────────────────────────────────────
    # FORMATTING HELPERS
    # ──────────────────────────────────────────────
    def _format_exercise_instructions(self, name: str, data: dict) -> str:
        steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(data["instructions"]))
        return (
            f"**{name.title()}**\n"
            f"{data['description']}\n\n"
            f"**Instructions:**\n{steps}\n\n"
            f"**Target:** {data['target_reps']} × {data['target_sets']}\n"
            f"**Range of Motion:** {data['target_rom']}\n"
            f"**Muscles:** {data['muscles']}\n\n"
            f"💡 **Tip:** {data.get('tips', 'Focus on smooth, controlled movement.')}"
        )

    def _format_exercise_summary(self, name: str, data: dict) -> str:
        return (
            f"**{name.title()}** ({data.get('category', '')} — {data.get('difficulty', 'Beginner')})\n"
            f"{data['description']}\n\n"
            f"Target: {data['target_reps']} × {data['target_sets']} | ROM: {data['target_rom']}\n"
            f"Muscles: {data['muscles']}\n\n"
            f"Would you like step-by-step instructions?"
        )

    # ──────────────────────────────────────────────
    # CONVERSATION HISTORY
    # ──────────────────────────────────────────────
    def _record_message(self, user_id: str, role: str, content: str):
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        self.conversation_history[user_id].append({"role": role, "content": content})
        # Keep history bounded
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]

    def clear_history(self, user_id: str = "default"):
        """Clear conversation history for a user."""
        self.conversation_history.pop(user_id, None)


# Global singleton
ai_chatbot = AIChatbotEngine()
