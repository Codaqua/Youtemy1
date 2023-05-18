from algoliasearch.search_client import SearchClient

from app import config


from app.courses.models import Course
from app.videos.models import Video

from .schemas import (
    CourseIndexSchema,
    VideoIndexSchema
)

settings = config.get_settings()

def get_index():
    client = SearchClient.create(
            settings.algolia_app_id, 
            settings.algolia_api_key
    )
    index = client.init_index(settings.algolia_index_name)
    return index


def get_dataset():
    course_q = [dict(x) for x in Course.objects.all()]
    courses_dataset = [CourseIndexSchema(**x).dict() for x in course_q]
    video_q = [dict(x) for x in Video.objects.all()]
    videos_dataset = [VideoIndexSchema(**x).dict() for x in video_q]
    dataset = videos_dataset + courses_dataset
    return dataset

def update_index():
    index = get_index()
    dataset = get_dataset()
    idx_resp = index.save_objects(dataset).wait()
    try:
        count = len(list(idx_resp)[0]['objectIDs'])
    except:
        count = None
    return count


def search_index(query):
    index = get_index()
    return index.search(query)