import re
import random
from typing import Dict, List, Optional

class PhysioChatbot:
    def __init__(self):
        self.exercise_instructions = self._load_exercise_instructions()
        self.safety_tips = self._load_safety_tips()
        self.greetings = self._load_greetings()
        self.farewells = self._load_farewells()
        
    def _load_exercise_instructions(self) -> Dict[str, str]:
        """Load exercise-specific instructions"""
        return {
            "shoulder flexion": (
                "Shoulder Flexion Instructions:\n"
                "1. Stand or sit with good posture\n"
                "2. Keep your arm straight\n"
                "3. Raise your arm forward and upward\n"
                "4. Go as high as comfortable\n"
                "5. Slowly lower back to starting position\n"
                "Target: 10-15 repetitions"
            ),
            "shoulder extension": (
                "Shoulder Extension Instructions:\n"
                "1. Stand with good posture\n"
                "2. Keep your arm straight\n"
                "3. Move your arm backward\n"
                "4. Keep the movement controlled\n"
                "5. Return to starting position\n"
                "Target: 10-15 repetitions"
            ),
            "shoulder abduction": (
                "Shoulder Abduction Instructions:\n"
                "1. Stand with good posture\n"
                "2. Raise your arm sideways\n"
                "3. Go up to shoulder height\n"
                "4. Keep movement smooth\n"
                "5. Lower slowly\n"
                "Target: 10-15 repetitions"
            ),
            "elbow flexion": (
                "Elbow Flexion Instructions:\n"
                "1. Sit or stand with arm relaxed\n"
                "2. Bend your elbow\n"
                "3. Bring hand toward shoulder\n"
                "4. Straighten slowly\n"
                "Target: 15-20 repetitions"
            ),
            "elbow extension": (
                "Elbow Extension Instructions:\n"
                "1. Start with elbow bent\n"
                "2. Straighten your arm completely\n"
                "3. Hold briefly\n"
                "4. Bend slowly\n"
                "Target: 15-20 repetitions"
            ),
            "knee flexion": (
                "Knee Flexion Instructions:\n"
                "1. Stand holding support if needed\n"
                "2. Bend your knee\n"
                "3. Bring heel toward buttock\n"
                "4. Lower slowly\n"
                "Target: 15-20 repetitions"
            ),
            "knee extension": (
                "Knee Extension Instructions:\n"
                "1. Sit with knee bent\n"
                "2. Straighten your leg\n"
                "3. Hold for 2 seconds\n"
                "4. Bend slowly\n"
                "Target: 15-20 repetitions"
            ),
            "hip abduction": (
                "Hip Abduction Instructions:\n"
                "1. Stand straight\n"
                "2. Move leg sideways\n"
                "3. Keep toes pointing forward\n"
                "4. Return to center\n"
                "Target: 12-15 repetitions"
            ),
            "hip flexion": (
                "Hip Flexion Instructions:\n"
                "1. Stand straight\n"
                "2. Raise leg forward\n"
                "3. Keep knee straight\n"
                "4. Lower slowly\n"
                "Target: 12-15 repetitions"
            ),
            "neck flexion": (
                "Neck Flexion Instructions:\n"
                "1. Sit with good posture\n"
                "2. Tuck chin to chest\n"
                "3. Hold for 2 seconds\n"
                "4. Return slowly\n"
                "Target: 10 repetitions"
            ),
            "neck extension": (
                "Neck Extension Instructions:\n"
                "1. Sit with good posture\n"
                "2. Look upward gently\n"
                "3. Hold for 2 seconds\n"
                "4. Return slowly\n"
                "Target: 10 repetitions"
            ),
            "neck rotation": (
                "Neck Rotation Instructions:\n"
                "1. Sit with good posture\n"
                "2. Turn head to right\n"
                "3. Hold for 2 seconds\n"
                "4. Turn to left\n"
                "5. Hold for 2 seconds\n"
                "Target: 8-10 repetitions"
            ),
            "wrist flexion": (
                "Wrist Flexion Instructions:\n"
                "1. Hold arm straight\n"
                "2. Bend wrist downward\n"
                "3. Hold for 2 seconds\n"
                "4. Return to neutral\n"
                "Target: 15 repetitions"
            ),
            "wrist extension": (
                "Wrist Extension Instructions:\n"
                "1. Hold arm straight\n"
                "2. Bend wrist upward\n"
                "3. Hold for 2 seconds\n"
                "4. Return to neutral\n"
                "Target: 15 repetitions"
            ),
            "back extension": (
                "Back Extension Instructions:\n"
                "1. Lie on stomach\n"
                "2. Place hands by shoulders\n"
                "3. Gently arch back\n"
                "4. Hold for 3 seconds\n"
                "5. Relax slowly\n"
                "Target: 8-10 repetitions"
            )
        }
    
    def _load_safety_tips(self) -> List[str]:
                "Target: 10-15 repetitions"
            ),
            "hip abduction": (
                "Hip Abduction Instructions:\n"
                "1. Stand straight with support\n"
                "2. Keep your leg straight\n"
                "3. Move leg sideways away from body\n"
                "4. Don't lean your body\n"
                "5. Slowly return leg to center\n"
                "Target: 10-15 repetitions"
            )
        }
    
    def _load_safety_tips(self) -> List[str]:
        """Load general safety tips"""
        return [
            "Always warm up before exercising",
            "Stop if you feel pain - discomfort is normal, pain is not",
            "Maintain proper posture throughout exercises",
            "Breathe normally - don't hold your breath",
            "Start with fewer repetitions and gradually increase",
            "Use support if needed for balance",
            "Consult a physiotherapist for persistent pain",
            "Stay hydrated during exercise sessions",
            "Wear comfortable, non-restrictive clothing",
            "Exercise in a clear, safe space"
        ]
    
    def _load_greetings(self) -> List[str]:
        """Load greeting messages"""
        return [
            "Hello! I'm your physiotherapy assistant. How can I help you today?",
            "Hi there! Ready for some physiotherapy guidance?",
            "Welcome! I'm here to help with your exercise questions.",
            "Greetings! What physiotherapy questions do you have?"
        ]
    
    def _load_farewells(self) -> List[str]:
        """Load farewell messages"""
        return [
            "Take care and keep exercising safely!",
            "Goodbye! Remember to listen to your body.",
            "Stay healthy and keep up the good work!",
            "Until next time! Exercise safely."
        ]
    
    def get_response(self, message: str, exercise_context: Optional[str] = None) -> str:
        """Generate response based on user message and exercise context"""
        message_lower = message.lower()
        
        # Check for greetings
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            return random.choice(self.greetings)
        
        # Check for farewells
        if any(farewell in message_lower for farewell in ["bye", "goodbye", "see you", "exit"]):
            return random.choice(self.farewells)
        
        # Exercise-specific questions
        if exercise_context:
            exercise_key = exercise_context.lower()
            if exercise_key in self.exercise_instructions:
                if "how" in message_lower and ("perform" in message_lower or "do" in message_lower):
                    return self.exercise_instructions[exercise_key]
                elif "instruction" in message_lower or "guide" in message_lower:
                    return self.exercise_instructions[exercise_key]
                elif "reps" in message_lower or "repetitions" in message_lower:
                    return f"For {exercise_context.title()}, aim for 10-15 repetitions per set. Take breaks as needed."
        
        # General exercise questions
        for exercise_key, instructions in self.exercise_instructions.items():
            if exercise_key in message_lower:
                if "how" in message_lower or "instruction" in message_lower:
                    return instructions
        
        # Safety questions
        if any(safety_word in message_lower for safety_word in ["safe", "pain", "hurt", "danger", "careful"]):
            return random.choice(self.safety_tips)
        
        # Repetition questions
        if "reps" in message_lower or "repetition" in message_lower:
            return "Generally, aim for 10-15 repetitions per exercise. Start with fewer if you're new and gradually increase. Listen to your body and don't push through pain."
        
        # Posture questions
        if "posture" in message_lower or "form" in message_lower:
            return "Good posture is crucial! Keep your back straight, shoulders relaxed, and move slowly and controlled. The system will provide real-time feedback on your posture during exercises."
        
        # Default response
        default_responses = [
            "I can help you with exercise instructions, safety tips, and general physiotherapy guidance. What specific exercise would you like to know about?",
            "Feel free to ask me about specific exercises, safety precautions, or general physiotherapy advice. What's on your mind?",
            "I'm here to help with your physiotherapy questions. You can ask me about exercises, safety, or proper form."
        ]
        
        return random.choice(default_responses)
    
    def get_exercise_list(self) -> str:
        """Get list of available exercises"""
        exercises = list(self.exercise_instructions.keys())
        exercise_list = "\n".join([f"• {exercise.title()}" for exercise in exercises])
        return f"Available exercises:\n{exercise_list}\n\nAsk me for instructions on any of these exercises!"
    
    def get_safety_tip(self) -> str:
        """Get a random safety tip"""
        return random.choice(self.safety_tips)

# Global chatbot instance
chatbot = PhysioChatbot()
