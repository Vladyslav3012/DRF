from google import genai
from Project import settings
from Project.settings import PROMPT_TO_TITLE

client = genai.Client(api_key=settings.GEMINI_SECRET_KEY)

SYSTEM_PROMPT = settings.SYSTEM_PROMPT
PROMPT_TO_TITLE = PROMPT_TO_TITLE

def create_title(model, user_prompt):
    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config = genai.types.GenerateContentConfig(
                system_instruction=PROMPT_TO_TITLE,
                candidate_count=1
            )
        )
        if response.text:
            return response.text.strip().replace('"', '')
        return user_prompt[:50]
    except Exception:
        return user_prompt[:50]


def ask_to_gemini(model, user_prompt):
    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config = genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        if response.text:
            return response.text.strip().replace('"', '')
        return "Answer not generated"
    except Exception:
        return "An error occurred while accessing the service"

