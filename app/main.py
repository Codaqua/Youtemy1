# TODO
# añadido por mi. ver si es necesario. No reconoce confing.py:: SECRET_KEY
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
# añadido por mi

import json
import pathlib
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import requires
from cassandra.cqlengine.management import sync_table
from pydantic.error_wrappers import ValidationError
from . import config, db, utils

from .indexing.client import (
    update_index,
    search_index
)
from .courses.routers import router as course_router

from .shortcuts import redirect, render
from .users.backends import JWTCookieBackend
from .users.decorators import login_required
from .users.models import User
from .users.schemas import (
    UserLoginSchema,
    UserSignupSchema
)
from .videos.models import Video
from .videos.routers import router as video_router

from .watch_events.models import WatchEvent
from .watch_events.routers import router as watch_event_router

from .courses.models import Course
from .courses.routers import router as course_router

DB_SESSION = None
BASE_DIR = pathlib.Path(__file__).resolve().parent # app/
# TEMPLATE_DIR = BASE_DIR / "templates"
 
app = FastAPI()
settings = config.get_settings()
app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())
app.include_router(video_router)
app.include_router(watch_event_router)
app.include_router(course_router)

# templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# @app.get("/")
# def homepage():
#     return {"message": "Hello World"}


from .handlers import * # noqa


@app.on_event("startup")
def on_startup():
    # triggered when fastapi starts
    print("Prueba_main.py")
    global DB_SESSION
    DB_SESSION = db.get_session()
    sync_table(User)
    sync_table(Video)
    sync_table(WatchEvent)
    sync_table(Course)


# @app.get("/", response_class=HTMLResponse)
# def homepage(request: Request):
#     # TODO: BORRAR EL SIGUIENTE PARRAFO
#     # You can pass context data to your template like this.
#     context = {"request": request, "abc": "ABC variable value"} # TODO: 

#     if request.user.is_authenticated:  # Assuming you have implemented authentication.
#         return templates.TemplateResponse("dashboard.html", context, status_code=200)
#     else:
#         return templates.TemplateResponse("home.html", context, status_code=200)


# TODO: ORIGINAL --> 4:14
@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html", {}, status_code=200)
    return render(request, "home.html", {})

 
@app.get("/account", response_class=HTMLResponse)
@login_required
def account_view(request: Request):
    """
    hello world
    """
    context = {}
    return render(request, "account.html", context)

@app.get("/login", response_class=HTMLResponse)
def login_get_view(request: Request):
    # TODO: BORRAR EL SIGUIENTE PARRAFO
    # return templates.TemplateResponse("auth/login.html", {"request": request})
    return render(request, "auth/login.html", {})


@app.post("/login", response_class=HTMLResponse)
def login_post_view(request: Request, 
    email: str=Form(...), 
    password: str = Form(...),
    next: Optional[str] = "/"
    ):

    raw_data  = {
        "email": email,
        "password": password,
       
    }
    data, errors = utils.valid_schema_data_or_error(raw_data, UserLoginSchema)
    context = {
                "request": request,
                "data": data,
                "errors": errors,
            }
    if len(errors) > 0:
        return render(request, "auth/login.html", context, status_code=400)
    if "http://127.0.0.1" not in next:
        next = '/'
    return redirect(next, cookies=data)


@app.get("/logout", response_class=HTMLResponse)
def logout_get_view(request: Request):
    if not request.user.is_authenticated:
        return redirect('/login')
    return render(request, "auth/logout.html", {})

@app.post("/logout", response_class=HTMLResponse)
def logout_post_view(request: Request):
    return redirect("/login", remove_session=True)

#  TODO: BORRAR EL SIGUIENTE metodo /users
@app.get("/users")
def users_list_view(request: Request):
    users = User.objects.all()
    return list(users)

@app.get("/signup", response_class=HTMLResponse)
def signup_get_view(request: Request):
    return render(request, "auth/signup.html")


@app.post("/signup", response_class=HTMLResponse)
def signup_post_view(request: Request, 
    email: str=Form(...), 
    username: str=Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...)
    ):
    raw_data  = {
        "email": email,
        "username": username, # TODO: "username": "username
        "password": password,
        "password_confirm": password_confirm
    }
    data, errors = utils.valid_schema_data_or_error(raw_data, UserSignupSchema)
    if len(errors) > 0:
        context = {
            "data": data,
            "errors": errors,
        }
        return render(request, "auth/signup.html", context, status_code=400)
    User.create_user(email=data["email"], password=data["password"].get_secret_value(), username=data["username"])  # creating user
    # User.create_user(email=data["email"], password=data["password"].get_secret_value())  # creating user
    return redirect("/login")
   
#    TODO: ORIGINAL, PERO NO GUARDA EN DB
    # if len(errors) > 0:
    #     return render(request, "auth/signup.html", context, status_code=400)
    # return redirect("/login")


@app.post('/update-index', response_class=HTMLResponse)
def htmx_update_index_view(request:Request):
    count = update_index()
    return HTMLResponse(f"({count}) Refreshed")


@app.get("/search", response_class=HTMLResponse)
def search_detail_view(request:Request, q:Optional[str] = None):
    query = None
    context = {}
    if q is not None:
        query = q
        results = search_index(query)
        hits = results.get('hits') or []
        num_hits = results.get('nbHits')
        context = {
            "query": query,
            "hits": hits,
            "num_hits": num_hits
        }
    return render(request, "search/detail.html", context)


