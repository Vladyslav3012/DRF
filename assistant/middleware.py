import logging
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.db import close_old_connections
import jwt
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from Project.settings import SECRET_KEY
from users.models import CustomUser

algorithm = 'HS256'

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        logger.info(f'Payload: {payload}')
    except jwt.ExpiredSignatureError:
        logger.exception("Token expired")
        return AnonymousUser()
    except jwt.InvalidTokenError:
        logger.exception("Invalid token")
        return AnonymousUser()
    except Exception as e:
        logger.exception(f'Payload error: {e}')
        return AnonymousUser()

    try:
        user = CustomUser.objects.get(id=payload['user_id'])
        logger.info(f"Token #{token} check success")
    except Exception as e:
        logger.exception(f"User get error: {e}")
        return AnonymousUser()

    return user


class TokenAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        close_old_connections()

        try:
            query_string = scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token_list = query_params.get('token')

            if token_list:
                token_key = token_list[0]
                scope['user'] = await get_user(token_key)
            else:
                scope['user'] = AnonymousUser()
        except Exception as e:
            logger.exception(f"Error with decode token: {e}")

        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner=inner)
