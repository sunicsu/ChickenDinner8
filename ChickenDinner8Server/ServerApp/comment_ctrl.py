from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from ServerApp import models
from . import utils
import json


@require_http_methods(["GET"])
def get_comments(request):
    queryset = models.TakeImage.objects.all()
    return utils.eatDDJsonResponse({"comments": comments_queryset_to_array(queryset)})


@require_http_methods(["GET"])
def update_comments(request, comments_id, likecount, unlikecount):
    obj = models.TakeImage.objects.get(id=comments_id)
    obj.likecount = obj.likecount + likecount
    obj.unlikecount = obj.unlikecount + unlikecount
    obj.save()
    queryset = models.TakeImage.objects.all()
    return utils.eatDDJsonResponse({"comments": comments_queryset_to_array(queryset)})


@require_http_methods(["PUT", "DELETE"])
def manage_comments(request, comments_id):
    if request.method == 'put':
        queryset = models.TakeImage.objects.filter(id=comments_id)
        if queryset.exists():
            obj = queryset.first()
            received_data = json.loads(request.body.decode('utf-8'))
            obj.username = received_data['username']
            obj.text = received_data['text']
            obj.picture = received_data['picture']
            obj.title = received_data['title']
            obj.time = received_data['time']
            obj.save()
            return utils.eatDDJsonResponse(comments_to_dict(obj))
        else:
            return HttpResponse('This Comments is not exist', status=405)
    elif request.method == 'DELETE':
        queryset = models.TakeImage.objects.filter(id=comments_id)
        if queryset.exists():
            queryset.delete()
            return HttpResponse('The selected comments is deleted!', status=200)
        else:
            return HttpResponse('This comments did not exist', status=405)


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
        "likecount": new_comment.likecount,
        "unlikecount": new_comment.unlikecount,
        "canlike": new_comment.canlike,
    }

