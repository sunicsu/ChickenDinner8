from django.http import HttpResponse
import decimal
import simplejson as json
from .models import NormalUser
import requests
import ChickenDinner8Server.settings
from .proxy import proxy
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import permissions


BOSS_USERNAME = 'username'
BUYER_USERNAME = 'session_key'


# 状态码
class ReturnCode:
    SUCCESS = 0

    FAILED = -100
    WRONG_PARMAS = -101
    RESOURCE_NOT_FOUND = -102

    UNAUTHORIZED = -500
    BROKEN_AUTHORIZED_DATA = -501

    @classmethod
    def message(cls, code):
        if code == cls.SUCCESS:
            return 'success'
        elif code == cls.FAILED:
            return 'failed'
        elif code == cls.UNAUTHORIZED:
            return 'unauthorized'
        elif code == cls.WRONG_PARMAS:
            return 'wrong params'
        elif code == cls.RESOURCE_NOT_FOUND:
            return 'resources not found'


def wrap_json_response(data=None, code=None, message=None):
    response = {}
    if not code:
        code = ReturnCode.SUCCESS
    if not message:
        message = ReturnCode.message(code)
    if data is not None:
        response['data'] = data
    response['result_code'] = code
    response['message'] = message
    return response


class CommonResponseMixin(object):
    @classmethod
    def wrap_json_response(cls, data=None, code=None, message=None):
        response = {}
        if not code:
            code = ReturnCode.SUCCESS
        if not message:
            message = ReturnCode.message(code)
        if data is not None:
            response['data'] = data
        response['result_code'] = code
        response['message'] = message
        return response

def eatDDJsonResponse(obj):
    return HttpResponse(json.dumps(obj, use_decimal=True), content_type="application/json")


# 判断是否已经授权
def already_authorized(request):
    is_authorized = False
    print(request.session.get('is_authorized'))
    if request.session['is_authorized']:
        is_authorized = True
    return is_authorized


def get_user(request):
    if not already_authorized(request):
        raise Exception('not authorized request')
    open_id = request.session.get('open_id')
    user = NormalUser.objects.get(open_id=open_id)
    return user


def c2s(appid, code):
    return code2session(appid, code)

'''
return data 的格式
{
  "session_key": "JmRNs6uPEpFzlMRmg4NqJQ==",
  "expires_in": 7200,
  "openid": "oXSML0ZH05BItFTFILfgCGxXxxik"
}
'''
def code2session(appid, code):
    API = 'https://api.weixin.qq.com/sns/jscode2session'
    params = 'appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % \
             (appid, ChickenDinner8Server.settings.WX_APP_SECRET, code)
    url = API + '?' + params
    # response = requests.get(url=url, proxies=proxy.proxy())
    response = requests.get(url=url)
    data = json.loads(response.text)
    print(data)
    return data


class BaseAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,)
