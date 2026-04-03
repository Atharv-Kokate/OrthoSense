from groq import AsyncGroq
from app.core.config import settings

# Global client cache
_client = None

def get_groq_client():
    global _client
    if _client is None:
        try:
            # We must load from the .env or settings to protect the secret key
            api_key = settings.GROQ_API_KEY 
            if not api_key:
                print("WARNING: GROQ_API_KEY is not defined in your environment/settings!")
            _client = AsyncGroq(api_key=api_key)
            print("Successfully initialized Groq with explicitly provided test key!")
        except Exception as e:
            print(f"Groq Initialization Error: {e}")
            _client = None
    return _client

async def generate_patient_feedback(
    patient_first_name: str, 
    exercise: str, 
    current_rep: int, 
    target_reps: int, 
    errors: list = None, 
    is_fatigued: bool = False, 
    fatigue_metrics: dict = None
) -> str:
    """
    Leverages Groq (Llama 3) to generate dynamic, clinically-grounded, zero-hallucination coaching 
    based on the exact state of their session (fatigue timeline, rep progression, specific errors).
    """
    if not errors and not is_fatigued:
        return "Great job! Your form is looking absolutely perfect."

    # 2-WAY PATIENT INTERVENTION CHECK
    patient_statement = None
    if errors:
        for err in errors:
            if err.get('type') == "Patient Verbal Intervention":
                patient_statement = err.get("achieved")
                break

    current_client = get_groq_client()
    if current_client is None:
        if patient_statement:
            return "I heard you, but my AI language functions are offline. Please contact your doctor if you need help."
        if is_fatigued:
            return f"{patient_first_name}, I noticed your form degrading. Let's wrap up this set here to prevent injury. Great work today!"
        error_types = [err["type"].replace("_", " ") for err in errors] if errors else []
        return f"Warning: Please watch out for {', '.join(error_types)}."       

    # Extract the exact physical errors triggered by the deep learning model 
    error_types = [err["type"].replace("_", " ") for err in errors] if errors else []

    if patient_statement:
        user_prompt = f"""Patient {patient_first_name} is currently on Rep {current_rep} out of {target_reps}.
The patient just spoke directly to you through the app's microphone and said: {patient_statement}.
Acknowledge what they said, answer briefly, and tell them you are ending/pausing their set if they indicated pain or discomfort."""
    elif is_fatigued:
        decline = fatigue_metrics.get("decline_percentage", 15) if fatigue_metrics else 15
        user_prompt = f"""Patient {patient_first_name} is currently on Rep {current_rep} out of {target_reps} for their {exercise}. 
Their structural form score has degraded rapidly by {decline:.1f}% over the last 3 reps, indicating severe muscular fatigue. 
Intervene immediately. Tell them to safely end their set to prevent injury, and commend them for the work they put in."""
    else:
        user_prompt = f"""Patient {patient_first_name} is currently on Rep {current_rep} out of {target_reps} for their {exercise}. 
Our biometric sensors just detected the following form errors: {', '.join(error_types)}. 
Tell them precisely how to correct their form."""

    system_prompt = """You are 'Ortho', an empathetic, professional AI physical therapy assistant.
Your goal is to provide concise, real-time verbal coaching.
Rules:
1. NEVER hallucinate or guess diagnoses. Rely strictly on the provided real-time session context.
2. Keep your response to exactly 1 or 2 short sentences max.
3. Speak directly and warmly to the patient (e.g., "Sarah, try to...").
4. Be encouraging but medically firm, especially if stopping a session due to fatigue.
5. Do NOT use markdown formatting. Do NOT say 'Here is your feedback'."""

    try:
        chat_completion = await current_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="gemma2-9b-it",
            temperature=0.2, # Keep it extremely deterministic and professional
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Inference Error: {e}")
        error_msg = str(e).lower()
        if "rate_limit" in error_msg or "429" in error_msg:
            return "The AI server is experiencing high traffic. Your session is still tracking safely."
        if patient_statement:
            return f"I heard you, but my AI functions are offline due to: {error_msg}. Please check the server logs."
        if is_fatigued:
            return "Let's stop here due to fatigue. Excellent effort!"
        return "Please pause and adjust your form before continuing."
