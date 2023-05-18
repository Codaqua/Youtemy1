import uuid
from typing import Optional
from starlette.exceptions import HTTPException


from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse

from app import utils
from app.users.decorators import login_required
from app.shortcuts import (
    render,
    redirect, 
    get_object_or_404,
    is_htmx
)
from app.videos.schemas import VideoCreateSchema

from app.watch_events.models import WatchEvent
from .models import Course
from .schemas import CourseCreateSchema, CourseVideoAddSchema


router = APIRouter(
    prefix='/courses'
)


@router.get("/create", response_class=HTMLResponse)
@login_required
def course_create_view(request: Request):
    return render(request, "courses/create.html", {})

@router.post("/create", response_class=HTMLResponse)
@login_required
def course_create_post_view(request: Request, title: str=Form(...)):
    raw_data = {
        "title": title,
        # "user_id": request.user.username
        "user_id": request.user.user_id
    }
    data, errors = utils.valid_schema_data_or_error(raw_data, CourseCreateSchema)
    context = {
        "data": data,
        "errors": errors,
    }
    if len(errors) > 0:
        return render(request, "courses/create.html", context, status_code=400)
    obj = Course.objects.create(**data)
    redirect_path = obj.path or "/courses/create" 
    return redirect(redirect_path)


@router.get("/", response_class=HTMLResponse)
def course_list_view(request: Request):
    q = Course.objects.all().limit(100)
    context = {
        "object_list": q
    }
    return render(request, "courses/list.html", context)

# host_id='course-1'
# f"{host_id} is cool"

@router.get("/{db_id}", response_class=HTMLResponse)
def course_detail_view(request: Request, db_id: uuid.UUID):
    obj = get_object_or_404(Course, db_id=db_id)
    if request.user.is_authenticated:
        # user_id = request.user.username
        user_id = request.user.user_id
    context = {
        "object": obj,
        "videos": obj.get_videos(),
    }
    return render(request, "courses/detail.html", context) 




@router.get("/{db_id}/add-video", response_class=HTMLResponse)
@login_required
def course_video_add_view(
    request: Request, 
    db_id: uuid.UUID,
    is_htmx=Depends(is_htmx),
    ):
    context = {"db_id": db_id}
    if not is_htmx:
        raise HTTPException(status_code=400)
    return render(request, "courses/htmx/add-video.html", context)
    


@router.post("/{db_id}/add-video", response_class=HTMLResponse)
@login_required
def course_video_add_post_view(
    request: Request,
    db_id: uuid.UUID,
    is_htmx=Depends(is_htmx), 
    title: str=Form(...), 
    url: str = Form(...)):
    raw_data = {
        "title": title,
        "url": url,
        # "user_id": request.user.username,
        "user_id": request.user.user_id,
        "course_id": db_id
    }
    data, errors = utils.valid_schema_data_or_error(raw_data, CourseVideoAddSchema)
    redirect_path = data.get('path') or f"/courses/{db_id}" 
    
    context = {
        "data": data,
        "errors": errors,
        "title": title,
        "url": url,
        "db_id": db_id,
    }

    if not is_htmx:
        raise HTTPException(status_code=400)
    """
    Handle all HTMX requests
    """
    if len(errors) > 0:
        return render(request, "courses/htmx/add-video.html", context)
    context = {"path": redirect_path, "title": data.get('title')}
    return render(request, "videos/htmx/link.html", context)



@router.post("/{db_id}/{host_id}/delete/", response_class=HTMLResponse)
def course_remove_video_item_view(
        request: Request, 
        db_id: uuid.UUID,
        host_id: str,
        is_htmx=Depends(is_htmx),
        index: Optional[int] = Form(default=None)
    ):
    if not is_htmx:
        raise HTTPException(status_code=400)
    try:
        obj = get_object_or_404(Course, db_id=db_id)
    except:
        return HTMLResponse("Error. Please reload the page.")
    if not request.user.is_authenticated:
        return HTMLResponse("Please login and continue")
    if isinstance(index, int):
        host_ids = obj.host_ids
        host_ids.pop(index)
        obj.add_host_ids(host_ids=host_ids, replace_all=True)
    return HTMLResponse("Deleted")