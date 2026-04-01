from groq import Groq
from app.core.config import settings

def get_groq_client():
    # Only initialize if a key exists
    if settings.GROQ_API_KEY:
        try:
            return Groq(api_key=settings.GROQ_API_KEY)
        except Exception:
            return None
    return None

client = get_groq_client()

def generate_patient_feedback(patient_first_name: str, exercise: str, errors: list) -> str:
    """
    Takes the strict mathematical errors from the BiLSTM models and uses
    Groq (Llama 3) to generate natural, encouraging, and highly specific voice feedback
    for the patient in real-time.
    """
    if not errors:
        return "Great job! Your form is looking absolutely perfect."
    
    # Extract the exact physical errors triggered by the deep learning model
    error_types = [err["type"].replace("_", " ") for err in errors]
    
    prompt = f"""You are 'Ortho', an empathetic, professional AI physical therapy assistant. 
Your patient, {patient_first_name}, is performing their prescribed {exercise} exercise. 
Our biometric sensors just detected the following form errors: {', '.join(error_types)}.

In exactly 1 or 2 short sentences, tell them how to correct their form. 
Speak directly to them. Be encouraging, but medically clear. Do NOT use markdown. Do NOT say 'Here is your feedback'."""

    if client is None:
        # Fallback if no API key is provided yet
        return f"Warning: Please watch out for {', '.join(error_types)}."

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized physiotherapy AI with extremely low latency."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192", 
            temperature=0.3, # Keep it professional and deterministic
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API Inference Error: {e}")
        return "Please pause and adjust your form before continuing."
