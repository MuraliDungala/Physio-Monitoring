"""
Comprehensive Physiotherapy Knowledge Base
Provides structured knowledge for the AI chatbot covering exercises,
biomechanics, rehabilitation, posture correction, safety, and progress monitoring.
"""

from typing import Dict, List, Optional


class PhysioKnowledgeBase:
    """Central knowledge repository for the physiotherapy chatbot."""

    def __init__(self):
        self.exercises = self._build_exercise_knowledge()
        self.posture_corrections = self._build_posture_corrections()
        self.rehab_stages = self._build_rehab_stages()
        self.safety_guidelines = self._build_safety_guidelines()
        self.biomechanics = self._build_biomechanics()
        self.dashboard_help = self._build_dashboard_help()
        self.motivational_messages = self._build_motivational_messages()
        self.faq = self._build_faq()

    # ──────────────────────────────────────────────
    # EXERCISE KNOWLEDGE
    # ──────────────────────────────────────────────
    def _build_exercise_knowledge(self) -> Dict[str, dict]:
        return {
            "shoulder abduction": {
                "description": "Shoulder abduction involves raising your arm sideways away from your body.",
                "instructions": [
                    "Stand upright with your arms at your sides and shoulders relaxed.",
                    "Slowly raise your arm sideways, keeping your elbow straight.",
                    "Lift until your arm reaches shoulder height (about 90 degrees).",
                    "Hold for 1-2 seconds at the top.",
                    "Slowly lower your arm back to the starting position.",
                ],
                "target_reps": "10-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 90-180° depending on recovery stage",
                "muscles": "Deltoid (middle fibers), Supraspinatus, Trapezius",
                "common_errors": [
                    "Shrugging shoulders upward during the lift",
                    "Bending the elbow instead of keeping it straight",
                    "Leaning the torso to the opposite side",
                    "Using momentum instead of controlled movement",
                ],
                "tips": "Focus on smooth, controlled movement. Imagine sliding your arm along a wall.",
                "category": "Shoulder",
                "difficulty": "Beginner",
            },
            "shoulder flexion": {
                "description": "Shoulder flexion involves raising your arm forward and upward.",
                "instructions": [
                    "Stand or sit with good upright posture.",
                    "Keep your arm straight with palm facing inward.",
                    "Slowly raise your arm forward and upward.",
                    "Go as high as comfortable without arching your back.",
                    "Hold for 1-2 seconds, then slowly lower back.",
                ],
                "target_reps": "10-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 180°",
                "muscles": "Anterior Deltoid, Pectoralis Major (clavicular), Biceps",
                "common_errors": [
                    "Arching the lower back as the arm rises",
                    "Bending the elbow during the movement",
                    "Shrugging the shoulders",
                    "Moving too fast without control",
                ],
                "tips": "Keep your core engaged and back straight throughout the movement.",
                "category": "Shoulder",
                "difficulty": "Beginner",
            },
            "shoulder extension": {
                "description": "Shoulder extension involves moving your arm backward behind your body.",
                "instructions": [
                    "Stand with good posture and arms at your sides.",
                    "Keep your arm straight.",
                    "Slowly move your arm backward behind you.",
                    "Keep the movement controlled — don't swing.",
                    "Return slowly to the starting position.",
                ],
                "target_reps": "10-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 45-60°",
                "muscles": "Posterior Deltoid, Latissimus Dorsi, Triceps (long head)",
                "common_errors": [
                    "Leaning forward to increase range",
                    "Rotating the trunk during the movement",
                    "Using jerky or fast movements",
                ],
                "tips": "Imagine pushing a door closed behind you with a straight arm.",
                "category": "Shoulder",
                "difficulty": "Beginner",
            },
            "shoulder internal rotation": {
                "description": "Shoulder internal rotation involves rotating your arm inward toward your body.",
                "instructions": [
                    "Stand with your elbow bent at 90 degrees, arm at your side.",
                    "Keep your elbow pinned to your side.",
                    "Rotate your forearm inward across your belly.",
                    "Hold for 1-2 seconds, then return slowly.",
                ],
                "target_reps": "10-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 70-90°",
                "muscles": "Subscapularis, Pectoralis Major, Latissimus Dorsi, Teres Major",
                "common_errors": [
                    "Lifting the elbow away from the body",
                    "Using body rotation instead of arm rotation",
                ],
                "tips": "Use a light resistance band for added strengthening if appropriate.",
                "category": "Shoulder",
                "difficulty": "Intermediate",
            },
            "shoulder external rotation": {
                "description": "Shoulder external rotation involves rotating your arm outward away from your body.",
                "instructions": [
                    "Stand with your elbow bent at 90 degrees, arm at your side.",
                    "Keep your elbow pinned to your side.",
                    "Rotate your forearm outward, away from your belly.",
                    "Hold for 1-2 seconds, then return slowly.",
                ],
                "target_reps": "10-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 70-90°",
                "muscles": "Infraspinatus, Teres Minor",
                "common_errors": [
                    "Lifting the elbow away from the body",
                    "Using trunk rotation to compensate",
                ],
                "tips": "This exercise is crucial for rotator cuff rehabilitation.",
                "category": "Shoulder",
                "difficulty": "Intermediate",
            },
            "shoulder adduction": {
                "description": "Shoulder adduction involves bringing your arm toward or across your body.",
                "instructions": [
                    "Stand with your arm raised to the side at shoulder height.",
                    "Slowly bring your arm down and across your body.",
                    "Control the movement throughout the entire range.",
                    "Return to the starting position.",
                ],
                "target_reps": "10-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "90° to 0°",
                "muscles": "Pectoralis Major, Latissimus Dorsi, Teres Major",
                "common_errors": [
                    "Moving too quickly",
                    "Not controlling the return phase",
                ],
                "tips": "Think of it as the opposite of shoulder abduction.",
                "category": "Shoulder",
                "difficulty": "Beginner",
            },
            "elbow flexion": {
                "description": "Elbow flexion involves bending the elbow to bring your hand toward your shoulder.",
                "instructions": [
                    "Sit or stand with your arm relaxed at your side, palm facing forward.",
                    "Slowly bend your elbow, bringing your hand toward your shoulder.",
                    "Keep your upper arm still — only the forearm should move.",
                    "Hold at the top for 1-2 seconds.",
                    "Slowly straighten your arm back to the starting position.",
                ],
                "target_reps": "15-20 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 145-150°",
                "muscles": "Biceps Brachii, Brachialis, Brachioradialis",
                "common_errors": [
                    "Swinging the upper arm forward",
                    "Using momentum instead of muscle control",
                    "Not fully extending at the bottom",
                ],
                "tips": "Keep your shoulder blade pulled back and down for stability.",
                "category": "Elbow",
                "difficulty": "Beginner",
            },
            "elbow extension": {
                "description": "Elbow extension involves straightening your arm from a bent position.",
                "instructions": [
                    "Start with your elbow bent at about 90 degrees.",
                    "Slowly straighten your arm completely.",
                    "Hold the fully extended position for 1-2 seconds.",
                    "Slowly bend your elbow back to the starting position.",
                ],
                "target_reps": "15-20 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "145° to 0°",
                "muscles": "Triceps Brachii, Anconeus",
                "common_errors": [
                    "Locking the joint aggressively at full extension",
                    "Moving the shoulder during the exercise",
                    "Rushing through the movement",
                ],
                "tips": "Stop just short of locking out to protect the joint.",
                "category": "Elbow",
                "difficulty": "Beginner",
            },
            "knee flexion": {
                "description": "Knee flexion involves bending the knee to bring the heel toward the buttock.",
                "instructions": [
                    "Stand facing a wall or chair for balance support.",
                    "Slowly bend your knee, bringing your heel toward your buttock.",
                    "Keep your thighs parallel — don't let the knee drift forward.",
                    "Hold at maximum bend for 1-2 seconds.",
                    "Slowly lower your foot back to the floor.",
                ],
                "target_reps": "15-20 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 130-135°",
                "muscles": "Hamstrings (Biceps Femoris, Semimembranosus, Semitendinosus)",
                "common_errors": [
                    "Leaning forward during the movement",
                    "Swinging the leg instead of controlled bending",
                    "Not maintaining balance",
                ],
                "tips": "Hold onto a stable surface if needed for balance.",
                "category": "Knee",
                "difficulty": "Beginner",
            },
            "knee extension": {
                "description": "Knee extension involves straightening the knee from a bent position.",
                "instructions": [
                    "Sit in a chair with feet flat on the floor.",
                    "Slowly straighten one leg until it is parallel with the floor.",
                    "Hold the extended position for 2-3 seconds.",
                    "Slowly lower your foot back to the floor.",
                ],
                "target_reps": "15-20 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "90° to 0°",
                "muscles": "Quadriceps (Rectus Femoris, Vastus Lateralis, Medialis, Intermedius)",
                "common_errors": [
                    "Lifting the thigh off the chair",
                    "Locking the knee aggressively",
                    "Dropping the leg instead of lowering it controlled",
                ],
                "tips": "Squeeze the quadricep muscle at the top for best results.",
                "category": "Knee",
                "difficulty": "Beginner",
            },
            "hip abduction": {
                "description": "Hip abduction involves moving the leg sideways away from the body's midline.",
                "instructions": [
                    "Stand straight, holding a wall or chair for balance.",
                    "Keep your leg straight and toes pointing forward.",
                    "Slowly move your leg sideways away from your body.",
                    "Don't lean your body to the opposite side.",
                    "Slowly return your leg to the center.",
                ],
                "target_reps": "12-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 40-45°",
                "muscles": "Gluteus Medius, Gluteus Minimus, Tensor Fasciae Latae",
                "common_errors": [
                    "Leaning the torso away from the moving leg",
                    "Rotating the leg outward instead of lifting sideways",
                    "Using hip hiking (elevating the pelvis) to compensate",
                ],
                "tips": "Keep your pelvis level and core engaged throughout.",
                "category": "Hip",
                "difficulty": "Beginner",
            },
            "hip flexion": {
                "description": "Hip flexion involves lifting the leg forward in front of the body.",
                "instructions": [
                    "Stand straight with support if needed.",
                    "Keep your leg straight (or slightly bent at the knee).",
                    "Slowly raise your leg forward.",
                    "Lift until your thigh is about parallel with the floor.",
                    "Lower slowly back to the starting position.",
                ],
                "target_reps": "12-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 90-120°",
                "muscles": "Iliopsoas, Rectus Femoris, Sartorius",
                "common_errors": [
                    "Leaning backward to lift the leg higher",
                    "Using momentum instead of control",
                    "Not keeping the standing leg stable",
                ],
                "tips": "Engage your core to keep your trunk upright.",
                "category": "Hip",
                "difficulty": "Beginner",
            },
            "neck flexion": {
                "description": "Neck flexion involves gently tucking the chin toward the chest.",
                "instructions": [
                    "Sit or stand with good posture, looking straight ahead.",
                    "Slowly and gently tuck your chin toward your chest.",
                    "Hold for 2-3 seconds.",
                    "Slowly return to the starting position.",
                ],
                "target_reps": "8-10 repetitions per set",
                "target_sets": "2 sets",
                "target_rom": "0° to 45-50°",
                "muscles": "Sternocleidomastoid, Longus Colli, Longus Capitis",
                "common_errors": [
                    "Moving too quickly or forcefully",
                    "Rounding the upper back instead of just the neck",
                    "Holding the breath",
                ],
                "tips": "Move very gently — the neck is sensitive. Stop if you feel any sharp pain.",
                "category": "Neck",
                "difficulty": "Beginner",
            },
            "neck extension": {
                "description": "Neck extension involves gently looking upward toward the ceiling.",
                "instructions": [
                    "Sit or stand with good posture, looking straight ahead.",
                    "Slowly and gently tilt your head backward, looking up.",
                    "Hold for 2-3 seconds.",
                    "Slowly return to the starting position.",
                ],
                "target_reps": "8-10 repetitions per set",
                "target_sets": "2 sets",
                "target_rom": "0° to 45-55°",
                "muscles": "Trapezius (upper), Splenius Capitis, Semispinalis Capitis",
                "common_errors": [
                    "Tilting too far back and causing dizziness",
                    "Compressing the neck instead of gentle extension",
                ],
                "tips": "Only tilt as far as is comfortable — never force the movement.",
                "category": "Neck",
                "difficulty": "Beginner",
            },
            "neck rotation": {
                "description": "Neck rotation involves turning the head to look over each shoulder.",
                "instructions": [
                    "Sit or stand with good posture, looking straight ahead.",
                    "Slowly turn your head to the right as far as comfortable.",
                    "Hold for 2-3 seconds.",
                    "Return to center, then turn to the left.",
                    "Hold for 2-3 seconds, then return to center.",
                ],
                "target_reps": "8-10 repetitions per side",
                "target_sets": "2 sets",
                "target_rom": "0° to 70-80° each side",
                "muscles": "Sternocleidomastoid, Splenius Capitis, Upper Trapezius",
                "common_errors": [
                    "Rotating the shoulders instead of just the head",
                    "Moving too quickly",
                    "Forcing past the comfortable range",
                ],
                "tips": "Think of turning to look over your shoulder at something behind you.",
                "category": "Neck",
                "difficulty": "Beginner",
            },
            "wrist flexion": {
                "description": "Wrist flexion involves bending the wrist so the palm moves toward the forearm.",
                "instructions": [
                    "Rest your forearm on a table with your hand hanging over the edge, palm up.",
                    "Hold a light weight or keep your hand empty.",
                    "Slowly bend your wrist upward (curl your hand toward your forearm).",
                    "Hold for 1-2 seconds.",
                    "Slowly lower your hand back to the starting position.",
                ],
                "target_reps": "12-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 70-80°",
                "muscles": "Flexor Carpi Radialis, Flexor Carpi Ulnaris, Palmaris Longus",
                "common_errors": [
                    "Lifting the forearm off the table",
                    "Using too heavy a weight",
                    "Moving too quickly",
                ],
                "tips": "Start without weight and add light resistance as you get stronger.",
                "category": "Wrist",
                "difficulty": "Beginner",
            },
            "wrist extension": {
                "description": "Wrist extension involves bending the wrist so the back of the hand moves toward the forearm.",
                "instructions": [
                    "Rest your forearm on a table with your hand hanging over the edge, palm down.",
                    "Hold a light weight or keep your hand empty.",
                    "Slowly bend your wrist upward (lift the back of your hand).",
                    "Hold for 1-2 seconds.",
                    "Slowly lower your hand back.",
                ],
                "target_reps": "12-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 60-70°",
                "muscles": "Extensor Carpi Radialis, Extensor Carpi Ulnaris, Extensor Digitorum",
                "common_errors": [
                    "Lifting the forearm off the support",
                    "Using excessive weight",
                ],
                "tips": "This exercise helps prevent and manage conditions like tennis elbow.",
                "category": "Wrist",
                "difficulty": "Beginner",
            },
            "back extension": {
                "description": "Back extension involves gently arching the back from a prone position.",
                "instructions": [
                    "Lie face down (prone) on a mat with hands beside your shoulders.",
                    "Slowly press up through your hands, arching your back gently.",
                    "Keep your hips on the mat.",
                    "Hold the position for 2-3 seconds.",
                    "Slowly lower back down.",
                ],
                "target_reps": "8-10 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 25-30° extension",
                "muscles": "Erector Spinae, Multifidus, Quadratus Lumborum",
                "common_errors": [
                    "Lifting the hips off the mat",
                    "Pushing up too far causing pain",
                    "Holding the breath",
                ],
                "tips": "If done on the floor, this is similar to a gentle cobra stretch in yoga.",
                "category": "Back",
                "difficulty": "Beginner",
            },
            "squat": {
                "description": "Squats involve lowering the body by bending the hips and knees simultaneously.",
                "instructions": [
                    "Stand with feet shoulder-width apart, toes slightly turned out.",
                    "Keep your chest up and core engaged.",
                    "Slowly lower your body by bending your hips and knees.",
                    "Lower until your thighs are roughly parallel with the floor (or as far as comfortable).",
                    "Push through your heels to stand back up.",
                ],
                "target_reps": "10-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 90-120° knee flexion",
                "muscles": "Quadriceps, Hamstrings, Gluteus Maximus, Core stabilizers",
                "common_errors": [
                    "Knees caving inward",
                    "Heels lifting off the floor",
                    "Leaning too far forward",
                    "Not reaching adequate depth",
                    "Rounding the lower back",
                ],
                "tips": "Imagine sitting back into a chair. Keep your weight over your mid-foot.",
                "category": "Squat",
                "difficulty": "Beginner",
            },
            "ankle dorsiflexion": {
                "description": "Ankle dorsiflexion involves pulling the foot upward toward the shin.",
                "instructions": [
                    "Sit with your leg extended or stand with support.",
                    "Pull your toes and foot upward toward your shin.",
                    "Hold for 2-3 seconds.",
                    "Slowly point your toes back to neutral.",
                ],
                "target_reps": "12-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 20°",
                "muscles": "Tibialis Anterior, Extensor Digitorum Longus",
                "common_errors": [
                    "Only moving the toes instead of the whole foot",
                    "Not achieving full range of motion",
                ],
                "tips": "This exercise is important for walking mechanics and fall prevention.",
                "category": "Ankle",
                "difficulty": "Beginner",
            },
            "ankle plantarflexion": {
                "description": "Ankle plantarflexion involves pointing the foot downward (like pressing a gas pedal).",
                "instructions": [
                    "Stand with support or sit with your leg extended.",
                    "Point your toes downward as far as comfortable.",
                    "Hold for 2 seconds.",
                    "Return to the neutral position.",
                ],
                "target_reps": "12-15 repetitions per set",
                "target_sets": "2-3 sets",
                "target_rom": "0° to 45-50°",
                "muscles": "Gastrocnemius, Soleus, Plantaris",
                "common_errors": [
                    "Only curling the toes instead of moving the ankle",
                    "Cramping from holding too long",
                ],
                "tips": "For standing calf raises, hold the top position for 2 seconds.",
                "category": "Ankle",
                "difficulty": "Beginner",
            },
        }

    # ──────────────────────────────────────────────
    # POSTURE CORRECTIONS
    # ──────────────────────────────────────────────
    def _build_posture_corrections(self) -> Dict[str, str]:
        return {
            "elbow_not_straight": (
                "Your elbow is not fully extended during the movement. "
                "Try straightening your arm completely before starting the next repetition."
            ),
            "shoulder_shrugging": (
                "You're shrugging your shoulders upward. Relax your shoulders down and back — "
                "imagine sliding your shoulder blades into your back pockets."
            ),
            "leaning_torso": (
                "Your torso is leaning to compensate for the movement. "
                "Keep your trunk upright and core engaged throughout the exercise."
            ),
            "knee_caving": (
                "Your knees are caving inward. Push your knees outward in line with your toes "
                "to maintain proper alignment."
            ),
            "back_rounding": (
                "Your lower back is rounding during the exercise. "
                "Maintain a neutral spine by engaging your core and keeping your chest up."
            ),
            "incomplete_rom": (
                "You're not reaching the full recommended range of motion. "
                "Try to extend the movement a bit further, but never push through sharp pain."
            ),
            "too_fast": (
                "You're moving too quickly through the exercise. "
                "Slow down your movement — aim for about 2 seconds up and 2 seconds down for each repetition."
            ),
            "head_position": (
                "Your head position seems off. Keep your head in a neutral position, "
                "looking straight ahead or slightly upward. Avoid jutting your chin forward."
            ),
            "general_good": (
                "Your form looks good! Maintain this posture and keep a steady, controlled pace."
            ),
        }

    # ──────────────────────────────────────────────
    # REHABILITATION STAGES
    # ──────────────────────────────────────────────
    def _build_rehab_stages(self) -> Dict[str, dict]:
        return {
            "acute": {
                "name": "Acute Phase (0-2 weeks)",
                "description": (
                    "Focus on pain management, reducing inflammation, and protecting the injured area. "
                    "Gentle range of motion exercises within pain-free limits."
                ),
                "goals": ["Reduce pain and swelling", "Protect the injury", "Maintain general fitness"],
                "exercises": "Gentle mobility exercises, isometric holds, ice/heat therapy",
            },
            "subacute": {
                "name": "Subacute / Mobility Phase (2-6 weeks)",
                "description": (
                    "You are currently in the mobility stage of rehabilitation. "
                    "Focus on improving joint flexibility and restoring range of motion before increasing strength exercises."
                ),
                "goals": ["Restore range of motion", "Begin light strengthening", "Improve flexibility"],
                "exercises": "Active range of motion, light resistance, stretching, balance work",
            },
            "strengthening": {
                "name": "Strengthening Phase (6-12 weeks)",
                "description": (
                    "Time to progressively build strength. Increase resistance gradually "
                    "while maintaining proper form on every repetition."
                ),
                "goals": ["Build strength", "Improve endurance", "Restore functional movement"],
                "exercises": "Progressive resistance, functional movements, sport-specific exercises",
            },
            "return_to_activity": {
                "name": "Return to Activity (12+ weeks)",
                "description": (
                    "Prepare to return to normal activities or sport. "
                    "Focus on power, agility, and activity-specific movements."
                ),
                "goals": ["Full functional recovery", "Sport-specific training", "Prevention of re-injury"],
                "exercises": "Plyometrics, agility drills, sport-specific movements, maintenance program",
            },
        }

    # ──────────────────────────────────────────────
    # SAFETY GUIDELINES
    # ──────────────────────────────────────────────
    def _build_safety_guidelines(self) -> List[str]:
        return [
            "Always warm up for 5-10 minutes before starting exercises to increase blood flow to muscles.",
            "Stop immediately if you feel sharp or sudden pain during any exercise.",
            "Breathe normally throughout exercises — inhale during the relaxation phase and exhale during exertion.",
            "Start with fewer repetitions and lighter resistance, gradually increasing as you get stronger.",
            "Use support (wall, chair, or railing) for balance during standing exercises if needed.",
            "Maintain proper hydration — drink water before, during, and after exercise sessions.",
            "Allow 48 hours of rest between intense sessions targeting the same muscle group.",
            "Wear comfortable, non-restrictive clothing and supportive footwear.",
            "Exercise in a clear, well-lit space free from obstacles and trip hazards.",
            "If you experience persistent pain, swelling, or reduced function, consult a physiotherapist.",
            "Cool down with gentle stretching after your exercise session to reduce muscle soreness.",
            "Never push through pain — discomfort during stretching is normal, but sharp pain is a warning sign.",
            "If you feel dizzy or lightheaded, stop exercising immediately and rest.",
            "Consult your healthcare provider before starting any new exercise program.",
        ]

    # ──────────────────────────────────────────────
    # BIOMECHANICS
    # ──────────────────────────────────────────────
    def _build_biomechanics(self) -> Dict[str, str]:
        return {
            "range_of_motion": (
                "Range of Motion (ROM) is the full extent a joint can move through its complete arc. "
                "It's measured in degrees. Limited ROM may indicate stiffness, swelling, or muscle tightness. "
                "Your ROM typically improves with consistent, gentle exercise over time."
            ),
            "joint_angle": (
                "Joint angle measures the angle between two body segments at a joint. "
                "For example, a fully extended elbow is at 0° and a fully flexed elbow is about 145°. "
                "The system tracks your joint angles in real time to assess exercise quality."
            ),
            "muscle_activation": (
                "Muscle activation refers to how well a muscle contracts during an exercise. "
                "Proper form ensures the correct muscles are doing the work. "
                "The system detects body landmarks to infer which muscles are engaged."
            ),
            "movement_quality": (
                "Movement quality is assessed based on smoothness, speed consistency, "
                "symmetry, and adherence to the ideal movement pattern. "
                "Higher quality scores indicate better form and more controlled movements."
            ),
            "posture_alignment": (
                "Posture alignment refers to the optimal positioning of body segments. "
                "Good alignment reduces stress on joints and muscles, making exercises safer and more effective. "
                "The system continuously monitors your posture during exercises."
            ),
        }

    # ──────────────────────────────────────────────
    # DASHBOARD HELP
    # ──────────────────────────────────────────────
    def _build_dashboard_help(self) -> Dict[str, str]:
        return {
            "quality_score": (
                "The quality score (0-100%) represents how accurately you performed the exercise. "
                "It considers your range of motion, posture alignment, movement smoothness, and consistency. "
                "A score above 80% indicates excellent form, 60-80% is good, and below 60% suggests areas for improvement."
            ),
            "rep_count": (
                "The repetition counter tracks completed reps during each exercise. "
                "A rep is counted when you complete the full movement cycle — going through the start position, "
                "the end position, and returning. The system uses joint angle thresholds to detect each phase."
            ),
            "joint_angle_display": (
                "The joint angle display shows the real-time angle at the primary joint being tracked for your exercise. "
                "For example, during elbow flexion, it shows the angle at your elbow. "
                "This helps you ensure you're achieving the full recommended range of motion."
            ),
            "posture_feedback": (
                "The posture feedback indicator shows whether your overall body alignment is correct during the exercise. "
                "Green = good posture, Yellow = slight deviation, Red = needs correction. "
                "Follow the system's specific correction tips to improve your posture."
            ),
            "session_history": (
                "Session history shows a record of your past exercise sessions including the date, "
                "exercise performed, number of reps, average quality score, and duration. "
                "Use it to track your progress over time."
            ),
            "progress_trend": (
                "The progress trend charts show how your performance has changed over time. "
                "Look for upward trends in quality scores and rep counts. "
                "Consistent improvement indicates effective rehabilitation."
            ),
            "body_performance": (
                "The body performance section shows how different body areas are progressing. "
                "It aggregates data from exercises targeting specific body regions "
                "to give you an overview of your recovery across all areas."
            ),
            "range_of_motion_chart": (
                "The Range of Motion section shows your best recorded ROM for each major joint. "
                "The bar shows your current ROM as a percentage of the normal range. "
                "Aim for gradual improvement; don't rush to reach full ROM."
            ),
            "ai_insights": (
                "AI Insights are automatically generated recommendations based on your exercise history. "
                "They highlight strengths, areas for improvement, and suggest adjustments to your routine."
            ),
        }

    # ──────────────────────────────────────────────
    # MOTIVATIONAL MESSAGES
    # ──────────────────────────────────────────────
    def _build_motivational_messages(self) -> List[str]:
        return [
            "Great job! Keep up the consistent effort — every rep brings you closer to recovery.",
            "You're making progress! Consistency is the key to successful rehabilitation.",
            "Well done on completing your session! Rest, recover, and come back stronger.",
            "Every exercise you complete is building a stronger, more resilient body.",
            "Stay positive! Recovery takes time, but you're on the right track.",
            "Excellent effort today! Your body will thank you for this work.",
            "Remember — progress isn't always linear. Some days are harder, and that's completely normal.",
            "You showed up and put in the work. That's what matters most!",
            "Your dedication to your exercises is impressive. Keep going!",
            "Small steps lead to big results. You're doing amazing!",
        ]

    # ──────────────────────────────────────────────
    # FAQ
    # ──────────────────────────────────────────────
    def _build_faq(self) -> Dict[str, str]:
        return {
            "how_many_reps": (
                "For most rehabilitation exercises, a typical range is 10-15 repetitions per set, "
                "with 2-3 sets per exercise. However, this depends on your specific condition and recovery stage. "
                "Start with fewer reps if you're a beginner and gradually increase as you get stronger."
            ),
            "how_often": (
                "Aim for 3-5 exercise sessions per week for best results. "
                "Always allow at least one rest day per week. "
                "Consistency matters more than intensity — regular, moderate sessions are better than occasional intense ones."
            ),
            "when_to_stop": (
                "Stop exercising if you experience sharp or sudden pain, dizziness, lightheadedness, "
                "abnormal swelling, or any symptom that feels 'wrong'. "
                "Mild muscle fatigue and gentle stretching discomfort are normal; sharp joint pain is not."
            ),
            "tight_feeling": (
                "Feeling tightness may indicate limited range of motion or muscle tension. "
                "Try performing gentle mobility and stretching exercises before your main workout. "
                "If the tightness persists or is accompanied by pain, consult your physiotherapist."
            ),
            "pain_during_exercise": (
                "If you feel pain during an exercise, stop immediately. Mild discomfort or muscle fatigue is normal, "
                "but sharp, stabbing, or worsening pain is a sign to stop. "
                "Do not try to push through pain — consult a physiotherapist if it continues."
            ),
            "warm_up": (
                "A good warm-up includes 5-10 minutes of light activity such as walking, gentle arm circles, "
                "or light marching in place. This increases blood flow and prepares your muscles for exercise. "
                "You can also start with the first set of your exercise at a reduced range of motion."
            ),
            "cool_down": (
                "After your exercise session, spend 5-10 minutes cooling down with gentle stretches. "
                "Hold each stretch for 15-30 seconds. This helps reduce muscle soreness and improve flexibility."
            ),
            "ice_or_heat": (
                "Use ice for acute injuries or swelling (first 48-72 hours after injury) — apply for 15-20 minutes. "
                "Use heat for muscle tightness and chronic conditions — apply for 15-20 minutes. "
                "When in doubt, consult your physiotherapist."
            ),
            "soreness_vs_pain": (
                "Muscle soreness (DOMS) is a dull ache that appears 24-48 hours after exercise and is usually normal. "
                "Pain that is sharp, occurs during the exercise, or is localized to a joint is NOT normal. "
                "If you're unsure, err on the side of caution and consult a professional."
            ),
        }

    # ──────────────────────────────────────────────
    # LOOKUP METHODS
    # ──────────────────────────────────────────────
    def get_exercise(self, name: str) -> Optional[dict]:
        """Get exercise knowledge by name (case-insensitive, fuzzy)."""
        key = name.lower().strip()
        if key in self.exercises:
            return self.exercises[key]
        # Fuzzy match
        for ex_key, ex_data in self.exercises.items():
            if key in ex_key or ex_key in key:
                return ex_data
        return None

    def get_exercise_names(self) -> List[str]:
        """Get list of all known exercise names."""
        return [name.title() for name in self.exercises.keys()]

    def get_exercises_by_category(self, category: str) -> List[str]:
        """Get exercise names filtered by body category."""
        cat_lower = category.lower()
        return [
            name.title()
            for name, data in self.exercises.items()
            if data.get("category", "").lower() == cat_lower
        ]

    def get_random_safety_tip(self) -> str:
        """Return a random safety guideline."""
        import random
        return random.choice(self.safety_guidelines)

    def get_random_motivation(self) -> str:
        """Return a random motivational message."""
        import random
        return random.choice(self.motivational_messages)


# Singleton instance
knowledge_base = PhysioKnowledgeBase()
