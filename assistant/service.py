import logging
from datetime import datetime

from Project import settings, prompts
from google import genai
from google.genai import errors

from flights.service import get_active_flight, search_flight
from users.service import get_user_order, generate_payment_link

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_SECRET_KEY)
SYSTEM_PROMPT = prompts.SYSTEM_PROMPT
PROMPT_TO_TITLE = prompts.PROMPT_TO_TITLE


def create_title(model, user_prompt):
    # try:
    #     response = client.models.generate_content(
    #         model=model,
    #         contents=user_prompt,
    #         config=genai.types.GenerateContentConfig(
    #             system_instruction=PROMPT_TO_TITLE,
    #             candidate_count=1,
    #             temperature=0.3,
    #             max_output_tokens=15
    #         )
    #     )
    #     if response.text:
    #         return response.text.strip().replace('"', '')
    #     return user_prompt[:50]
    # except Exception as e:
    #     logger.exception(f"Gemini error {e}")
    #     return user_prompt[:50]
    return user_prompt[:50]


def ask_to_gemini(model, user_prompt, history, user_id=None):
    all_history = []

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_user_id = user_id
    formatted_prompt = prompts.SYSTEM_PROMPT.format(current_date=today,
                                                     current_user=current_user_id)

    for msg in history:
        all_history.append({
            "role": msg.role,
            "parts": [{"text": msg.content}]
        })

    try:
        chat = client.chats.create(
            model=model,
            history=all_history,
            config=genai.types.GenerateContentConfig(
                tools=[get_active_flight,
                       search_flight,
                       get_user_order,
                       generate_payment_link,],
                temperature=0.7,
                system_instruction=formatted_prompt,
                automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                    disable=False,
                    maximum_remote_calls=3
                )
            )
        )

        response = chat.send_message(user_prompt)
        if response.text:
            return response.text.strip().replace('"', '')
        return "Answer not generated"
    except errors.ClientError as e:
        if e.code == 429:
            logger.error(f"Error with limit {e}")
            return "Too Many Requests, you limit in this version wiil be over"
        logger.exception(f"Gemini error {e}")
        return "Exceptions please got correct answer"
    except Exception as e:
        logger.exception(f"Gemini error {e}")
        return "An error occurred while accessing the service"
