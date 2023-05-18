# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from .auth import verify_user_id

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     user_data = verify_user_id(token)
#     if user_data:
#         return user_data
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid authentication credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.role != "active":
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

# async def get_current_active_tutor(current_user: User = Depends(get_current_active_user)):
#     if current_user.role != "tutor":
#         raise HTTPException(status_code=400, detail="Not a tutor")
#     return current_user