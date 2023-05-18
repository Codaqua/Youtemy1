import uuid
from pydantic import (
    BaseModel,
    validator,
    root_validator
)

from app.videos.extractors import extract_video_id
from app.videos.models import Video

from .models import Course

class CourseCreateSchema(BaseModel):
    title: str # user generated
    user_id: uuid.UUID # request.session user_id


class CourseVideoAddSchema(BaseModel):
    url: str # user generated
    title: str # user generated
    user_id: uuid.UUID # request.session user_id
    course_id: uuid.UUID  # Course db_id

    @validator("url")
    def validate_youtube_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f"{url} is not a valid YouTube URL")
        return url

    @validator("course_id")
    def validate_course_id(cls, v, values, **kwargs):
        q = Course.objects.filter(db_id=v)
        if q.count() == 0:
            raise ValueError(f"{v} is not a valid Course")
        return v

    @root_validator
    def validate_data(cls, values):
        url = values.get("url")
        title = values.get("title")
        course_id = values.get('course_id')
        if url is None:
            raise ValueError("A valid url is required.")
        user_id = values.get("user_id")
        video_obj = None
        extra_data = {}
        if title is not None:
            extra_data['title'] = title
        try:
            video_obj, created = Video.get_or_create(url, user_id=user_id, **extra_data)
        except:
            raise ValueError("There's a problem with your request, please try again.")
        if not isinstance(video_obj, Video):
            raise ValueError("There's a problem with your account, please try again.")
        if course_id:
            course_obj = Course.objects.get(db_id=course_id)
            course_obj.add_host_ids(host_ids=[video_obj.host_id])
            course_obj.save()
        return video_obj.as_data()


        