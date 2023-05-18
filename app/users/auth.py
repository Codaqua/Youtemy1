import datetime
from jose import jwt, ExpiredSignatureError
from app import config

from .models import User

settings = config.get_settings()

def authenticate(email, password):
    try:
        user_obj = User.objects.get(email=email)
    except Exception as e:
        user_obj = None
    if not user_obj.verify_password(password):
        return None
    return user_obj

def login(user_obj, expires=settings.session_duration):
    raw_data = {
        "user_id": f"{user_obj.user_id}",
        "role": user_obj.role,
        "username": user_obj.username,
        # "role": "admin", # TODO : add roles . quitarlo de aquí porque aparece en el token
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires)
    }
    return jwt.encode(raw_data, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_user_id(token):
    data = {}
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except ExpiredSignatureError as e:
        print(e, "log out user")
    except:
        pass
    if 'user_id' not in data:
        return None
    # if 'user_id' not in data.keys():
    #     return None
    return data