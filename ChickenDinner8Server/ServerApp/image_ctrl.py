from ServerApp import models
from django.http import HttpResponse
from .auth_required_decorator import eatdd_login_required
from . import utils
from django.views.decorators.http import require_http_methods
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from .models import TakeImage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from . import models
import os
from rest_framework.views import APIView
from rest_framework.response import Response


def json_getimage(request):
    ret = TakeImage.objects.all().order_by('-id')[:1]
    json_list = []
    for i in ret:
        json_list.append({"id": i.id, "picture": str(i.picture), "title": i.title, "number": i.number, "time": i.time})
    return JsonResponse(json_list, safe=False)


# 获得小程序数据，并存入数据库
class TakeImage(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        data = models.TakeImage(
            picture=request.FILES.get('file'),
            title=request.POST.get('title'),
            username=request.POST.get('username'),
            text=request.POST.get('text'),
        )
        data.save()
        return Response({'status': True})


@require_http_methods(["POST"])
@eatdd_login_required
def upload_image(request):
    print(request)
    print(type(request.FILES['image']))
    image_file = request.FILES['image']
    fs = FileSystemStorage(location='ChickenDinner8Server/ServerApp/static/img')
    filename = fs.save(image_file.name, image_file)
    return utils.eatDDJsonResponse({'url': 'http://127.0.0.1:8000/static/img/' + image_file.name})



