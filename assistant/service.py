import logging

from Project import settings
from google import genai


logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_SECRET_KEY)
SYSTEM_PROMPT = settings.SYSTEM_PROMPT
PROMPT_TO_TITLE = settings.PROMPT_TO_TITLE


def create_title(model, user_prompt):
    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=PROMPT_TO_TITLE,
                candidate_count=1,
                temperature=0.3,
                max_output_tokens=15
            )
        )
        if response.text:
            return response.text.strip().replace('"', '')
        return user_prompt[:50]
    except Exception as e:
        logger.exception(f"Gemini error {e}")
        return user_prompt[:50]


def ask_to_gemini(model, user_prompt, history):
    all_history = []

    for msg in history:
        all_history.append({
            "role": msg.role,
            "parts": [{"text": msg.content}]
        })

    all_history.append({
        "role": "user",
        "parts": [{"text": user_prompt}]
    })

    try:
        response = client.models.generate_content(
            model=model,
            contents=all_history,
            config = genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            )
        )
        if response.text:
            return response.text.strip().replace('"', '')
        return "Answer not generated"
    except Exception as e:
        logger.exception(f"Gemini error {e}")
        return "An error occurred while accessing the service"