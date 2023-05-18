from starlette.authentication import (
    AuthenticationBackend,
    # SimpleUser,
    UnauthenticatedUser,
    AuthCredentials,
    BaseUser
)

from . import auth

# Añadido para incluir el username
class CustomUser(BaseUser):
    def __init__(self, username: str, user_id: str):
        self.username = username
        self.user_id = user_id
        super().__init__()

    @property
    def is_authenticated(self):
        return True

class JWTCookieBackend(AuthenticationBackend):
    async def authenticate(self, request):
        session_id = request.cookies.get("session_id")
        user_data = auth.verify_user_id(session_id)
        if user_data is None:
            # anon user
            roles = ["anon"] #TODO: MIRAR LOS ROLES
            return AuthCredentials(roles), UnauthenticatedUser()
        user_id = user_data.get("user_id")
        username = user_data.get("username")  # Assuming the JWT token contains a username
        roles = ['authenticated', user_data.get("role")]  #TODO: MIRAR LOS ROLES
        # return AuthCredentials(roles), SimpleUser(user_id) 
        return AuthCredentials(roles), CustomUser(username=username, user_id=user_id)
    # TODO : 4:20 