from django.views.decorators.http import require_http_methods
from ServerApp import models
from . import utils
import json

@require_http_methods(["GET"])
def get_comments(request):
    queryset = models.TakeImage.objects.all()
    print(queryset)
    return utils.eatDDJsonResponse({"comments": comments_queryset_to_array(queryset)})


def comments_queryset_to_array(queryset):
    comments = []
    for item in queryset:
        comments.append(comments_to_dict(item))
    return comments


def comments_to_dict(new_comment):
    return {
        "comments_id": new_comment.id,
        "comments_title": new_comment.title,
        "comments_name": new_comment.username,
        "description": new_comment.text,
        "time": str(new_comment.time)[0:10],  #只显示年月日，对字符串切片处理。
        "image": 'http://127.0.0.1:8000/static' + new_comment.picture.url if new_comment.picture else "",
    }

