from functools import wraps
from fastapi import Request
from .exceptions import LoginRequiredException # TODO: 3:48 VERIFICAR / ELIMINAR

from .auth import verify_user_id
from .exceptions import LoginRequiredException

def login_required(func):
    @wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        session_token = request.cookies.get('session_id') # TODO: 3:48 VERIFICAR / ELIMINAR
        user_session = verify_user_id(session_token) # TODO: 3:48 VERIFICAR / ELIMINAR
        if user_session is None or not user_session: # TODO: 3:48 VERIFICAR / ELIMINAR
        # if not request.user.is_authenticated:
            raise LoginRequiredException(status_code=401)
        return func(request, *args, **kwargs)
    return wrapper