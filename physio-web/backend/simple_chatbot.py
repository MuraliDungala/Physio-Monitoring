"""
Simple Fallback Chatbot for Physiotherapy Guidance
"""

class SimpleChatbot:
    def __init__(self):
        self.responses = {
            "hello": "Hello! I'm your physiotherapy assistant. How can I help you today?",
            "hi": "Hi there! I'm here to help with your physiotherapy exercises.",
            "help": "I can help you with exercise instructions, safety tips, and general guidance. Ask me about specific exercises!",
            "exercise": "I can provide instructions for various exercises like shoulder flexion, elbow flexion, knee exercises, and more. Just ask about a specific exercise!",
            "shoulder": "For shoulder exercises, I can help with shoulder flexion, extension, abduction, and rotation exercises. Which one would you like to know about?",
            "elbow": "For elbow exercises, I can help with elbow flexion and extension exercises. These are great for building arm strength.",
            "knee": "For knee exercises, I can help with knee flexion and extension exercises. These are important for leg strength and mobility.",
            "hip": "For hip exercises, I can help with hip abduction and flexion exercises. These help with hip mobility and strength.",
            "neck": "For neck exercises, I can help with neck flexion, extension, and rotation exercises. Always perform these gently!",
            "wrist": "For wrist exercises, I can help with wrist flexion and extension exercises. These are great for wrist mobility.",
            "back": "For back exercises, I can help with back extension exercises. These help strengthen your back muscles.",
            "pain": "If you're experiencing pain, please stop the exercise and consult with your healthcare provider. Never push through sharp pain.",
            "safety": "Always warm up before exercising, start slowly, and stop if you feel pain. Consult your healthcare provider before starting new exercises.",
            "form": "Good form is important! Move slowly and controlled, focus on the target muscle, and breathe normally during exercises.",
            "reps": "Start with 8-12 repetitions per set. As you get stronger, you can gradually increase the number of repetitions.",
            "sets": "Start with 2-3 sets of each exercise. Rest for 30-60 seconds between sets.",
            "frequency": "Aim to exercise 3-4 times per week for best results. Consistency is key!",
            "progress": "Track your progress by noting how many reps you can do and how you feel after each session.",
            "beginner": "As a beginner, start with basic exercises, focus on proper form, and gradually increase intensity as you get comfortable.",
            "default": "I'm here to help with physiotherapy exercises! You can ask me about specific exercises, safety tips, or general guidance. Try asking about shoulder, elbow, knee, hip, neck, wrist, or back exercises."
        }
    
    def get_response(self, message: str) -> str:
        """Get chatbot response for user message"""
        message = message.lower().strip()
        
        # Check for keywords
        for keyword, response in self.responses.items():
            if keyword in message and keyword != "default":
                return response
        
        # Check for exercise names
        exercises = ["shoulder flexion", "shoulder extension", "shoulder abduction", "shoulder adduction",
                    "elbow flexion", "elbow extension", "knee flexion", "knee extension",
                    "hip abduction", "hip flexion", "neck flexion", "neck extension", "neck rotation",
                    "wrist flexion", "wrist extension", "back extension"]
        
        for exercise in exercises:
            if exercise in message:
                return f"{exercise.title()}: This is a great exercise! Start with 8-12 repetitions, focus on good form, and breathe normally. If you feel pain, stop immediately. Would you like more specific instructions for this exercise?"
        
        return self.responses["default"]

# Create global instance
simple_chatbot = SimpleChatbot()
