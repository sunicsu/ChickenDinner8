from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from . import utils
from ServerApp import models
import json
# from weixin import Weixin
from weixin import WXAPPAPI
from ServerApp import utils
from django.http import JsonResponse
from django.views import View
from .utils import  wrap_json_response, ReturnCode, CommonResponseMixin
from .utils import already_authorized, c2s
from .models import NormalUser
@require_http_methods(["POST", "GET"])
# def wechat_login(request):
#     if request.method == "POST":
#         received_data = json.loads(request.body.decode('utf-8'))
#         code = received_data['code']
#         # nickname = received_data['nickname']
#         # avatar = received_data['avatar']
#         print(code)
#         api = WXAPPAPI(appid='wx6b2174da78c30a9f', app_secret='e59f011ac1ef1e312a7e2b17abc9c840')
#         try:
#             session_info = api.exchange_code_for_session_key(code=code)
#             # session_info = api.access_token(code=code)
#             open_id = session_info['openid']
#             print(open_id)
#             # Check whether first log in
#             queryset = models.NormalUser.objects.filter(open_id=open_id)
#             if queryset.exists():
#                 # Not first log in, refresh nickname and avator
#                 user = queryset.first()
#                 # user.nickname = nickname
#                 # user.avatar = avatar
#                 # user.save()
#                 print('old user')
#             else:
#                 user = models.NormalUser(open_id=open_id)
#                 user.save()
#             request.session[utils.BUYER_USERNAME] = user.pk
#             return HttpResponse('Log In Success!', status=200)
#         except Exception as err:
#             print(err)
#             return HttpResponse('Wechat Log In Fail!', status=500)
#
#     if request.method == "GET":
#         if utils.BUYER_USERNAME in request.session:
#             # Logged In
#             login = True
#         else:
#             login = False
#         return utils.eatDDJsonResponse({"login": login})

def __authorize_by_code(request):
    '''
    使用wx.login的到的临时code到微信提供的code2session接口授权
    '''
    post_data = request.body.decode('utf-8')
    post_data = json.loads(post_data)
    code = post_data.get('code')
    print(post_data)
    app_id = post_data.get('appId')
    nickname = post_data.get('nickname')
    avatar = post_data.get('avatar')

    response = {}
    if not code or not app_id:
        response['message'] = 'authorized failed, need entire authorization data.'
        response['code '] = ReturnCode.BROKEN_AUTHORIZED_DATA
        return JsonResponse(data=response, safe=False)

    data = c2s(app_id, code)
    openid = data.get('openid')
    print('get openid: ', openid)

    if not openid:
        response = wrap_json_response(code=ReturnCode.FAILED, message='auth failed')
        return JsonResponse(data=response, safe=False)

    request.session['open_id'] = openid
    request.session['is_authorized'] = True
    print(request.session['is_authorized'])

    if not NormalUser.objects.filter(open_id=openid):
        new_user = NormalUser.objects.filter(open_id=openid)
        print('new user: open_id: %s' % openid)
        new_user.nickname = nickname
        new_user.avatar = avatar
        new_user.save()
        request.session[utils.BUYER_USERNAME] = new_user.first().id
        print(request.session['buyer_username'])
    if NormalUser.objects.filter(open_id=openid):
        old_user = NormalUser.objects.filter(open_id=openid)
        print('old user: open_id: %s' % openid)
        request.session[utils.BUYER_USERNAME] = old_user.first().id
        print(request.session[utils.BUYER_USERNAME])

    response = wrap_json_response(code=ReturnCode.SUCCESS, message='auth success.')
    return JsonResponse(data=response, safe=False)
    pass


def wechat_login(request):
    return __authorize_by_code(request)

