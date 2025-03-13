from django.http import HttpResponse
from ServerApp import models

from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count
from .auth_required_decorator import eatdd_login_required
from . import utils
import threading
from threading import Thread
import sched, time
import asyncio
# from django_async import async_view
from .utils import already_authorized
from . import food_ctrl
from django.views.decorators.http import require_http_methods
import json


@require_http_methods(["GET", "POST"])
@eatdd_login_required
def manage_table_order(request, restaurantId, tableId):
    # if already_authorized(request):
    if request.method == "POST":
        # create new order
        received_data = json.loads(request.body.decode('utf-8'))
        foods = received_data['foods']
        notes = received_data['notes']
        mobile = received_data['mobile']
        nickname = received_data['nickname']
        # First get the menu of this restaurant
        menu_queryset = models.Food.objects.filter(restaurant_id=restaurantId)
        food_objs = []
        total_price = 0
        print(notes)
        for item in foods:
            food_queryset = menu_queryset.filter(pk=item['food_id'], )
            print(food_queryset)
            if food_queryset.exists() is False:
                return HttpResponse('Food with id : %s not exist.' % (item['food_id']), status=500)
            else:
                food_objs.append({"food": food_queryset.first(), "num": item['num']})
                total_price = total_price + food_queryset.first().price * item['num']
        # Good to make order
        order = models.Order(user_id=request.session[utils.BUYER_USERNAME],
                             restaurant_id=restaurantId,
                             table_id=tableId,
                             totalPrice=total_price,
                             notes=notes['notes'],
                             mobile=mobile['mobile'],
                             nickname=nickname['nickname'])
        order.save()
        for item in food_objs:
            order_item = models.OrderItem(order=order, food=item['food'], num=item['num'])
            order_item.save()

        # change the status of table!
        table = models.Table.objects.get(table_id=tableId)
        table.status = 0
        table.save()
        # recover the status of table
        change_table_status(tableId)

        return_result = {}
        return_result['order_id'] = order.pk
        return_result['restaurant_id'] = restaurantId
        return_result['table_id'] = tableId
        return_result['customer_id'] = request.session[utils.BUYER_USERNAME]
        return_result['order_time'] = order.time.__str__()
        return_result['total_price'] = order.totalPrice
        return_result['detail'] = []
        # return_result['nickname'] = order.nickname
        for item in food_objs:
            return_result['detail'].append({"food": food_ctrl.food_to_dict(item['food']), "num": item["num"]})
        return utils.eatDDJsonResponse(return_result)

    elif request.method == "GET":
        if utils.BOSS_USERNAME in request.session:
            # Get certain boss' restaurant order
            order_queryset = models.Order.objects.filter(restaurant_id=restaurantId,
                                                         restaurant__boss_id=request.session[utils.BOSS_USERNAME],
                                                         table_id=tableId)
        elif utils.BUYER_USERNAME in request.session:
            order_queryset = models.Order.objects.filter(restaurant_id=restaurantId,
                                                         restaurant__order__user_id=request.session[
                                                             utils.BUYER_USERNAME],
                                                         table_id=tableId)

        return utils.eatDDJsonResponse(order_queryset_to_array(order_queryset))
    return HttpResponse('OK', status=200)


@require_http_methods(["POST"])
@eatdd_login_required
def system_order(request, restaurantId, tableId):
        received_data = json.loads(request.body.decode('utf-8'))
        foods = received_data['foods']
        notes = received_data['notes']
        mobile = received_data['mobile']
        nickname = received_data['nickname']
        # First get the menu of this restaurant
        menu_queryset = models.Food.objects.filter(restaurant_id=restaurantId)
        food_objs = []
        total_price = 0
        print(notes)
        for item in foods:
            food_queryset = menu_queryset.filter(pk=item['food_id'], )
            print(food_queryset)
            if food_queryset.exists() is False:
                return HttpResponse('Food with id : %s not exist.' % (item['food_id']), status=500)
            else:
                food_objs.append({"food": food_queryset.first(), "num": item['num']})
                total_price = total_price + food_queryset.first().price * item['num']
        # Set the user_id to 4 for systemOrder.
        order = models.Order(user_id=4,
                             restaurant_id=restaurantId,
                             table_id=tableId,
                             totalPrice=total_price,
                             notes=notes,
                             mobile=mobile,
                             nickname=nickname)
        order.save()
        for item in food_objs:
            order_item = models.OrderItem(order=order, food=item['food'], num=item['num'])
            order_item.save()

        # change the status of table!
        table = models.Table.objects.get(table_id=tableId)
        table.status = 0
        table.save()
        # recover the status of table
        change_table_status(tableId)

        return_result = {}
        return_result['order_id'] = order.pk
        return_result['restaurant_id'] = restaurantId
        return_result['table_id'] = tableId
        return_result['customer_id'] = 4
        return_result['order_time'] = order.time.__str__()
        return_result['total_price'] = order.totalPrice
        return_result['detail'] = []
        return_result['nickname'] = order.nickname
        for item in food_objs:
            return_result['detail'].append({"food": food_ctrl.food_to_dict(item['food']), "num": item["num"]})
        return utils.eatDDJsonResponse(return_result)




@require_http_methods(["POST"])
@eatdd_login_required
def change_table_order(request, restaurantId, tableId, order_id):
    # if already_authorized(request):
    if request.method == "POST":
        # create new order
        received_data = json.loads(request.body.decode('utf-8'))
        foods = received_data['foods']
        print(foods)
        total_price = 0
        # change the order.
        for item in foods:
            total_price = total_price + int(item['food']['price']) * int(item['num'])
        print(total_price)
        order = models.Order.objects.filter(id=order_id)
        order.update(totalPrice=total_price)

        # delete old data
        order_queryset = models.OrderItem.objects.filter(order_id=order_id)
        order_queryset.delete()

        # create new data
        for item in foods:
            models.OrderItem(order_id=order_id, food_id=item['food']['food_id'], num=item['num']).save()


        # change table status
        table = models.Table.objects.get(table_id=tableId)
        table.status = 0
        table.save()
        # recover the status of table
        change_table_status(tableId)

    return HttpResponse('OK', status=200)


@require_http_methods(["GET"])
@eatdd_login_required
def get_restaurant_order(request, restaurantId):
    if utils.BOSS_USERNAME in request.session:
        # Get certain boss' restaurant order
        order_queryset = models.Order.objects.filter(restaurant_id=restaurantId,
                                                     boss_id=request.session[utils.BOSS_USERNAME]).order_by('time').reverse()
    elif utils.BUYER_USERNAME in request.session:
        order_queryset = models.Order.objects.filter(restaurant_id=restaurantId,
                                                     user_id=request.session[utils.BUYER_USERNAME]).order_by('time').reverse()

    return utils.eatDDJsonResponse(order_queryset_to_array(order_queryset))


@require_http_methods(["GET"])
@eatdd_login_required
def get_today_order_statistics(request, restaurantId, daysNum):
    # today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    now = timezone.now()
    # today_end = today_start + timezone.timedelta(days=7)
    # before_orders = now - timezone.timedelta(days=7)
    before_orders = now - timezone.timedelta(days=daysNum)
    if utils.BOSS_USERNAME in request.session:
        # Get certain boss' restaurant order
        order_queryset = models.Order.objects.filter(restaurant_id=restaurantId,
                                                     boss_id=request.session[utils.BOSS_USERNAME],
                                                     time__range=(before_orders, now)).order_by('time').reverse()
    elif utils.BUYER_USERNAME in request.session:
        order_queryset = models.Order.objects.filter(restaurant_id=restaurantId,
                                                     user_id=request.session[utils.BUYER_USERNAME],
                                                     time__range=(before_orders, now)).order_by('time').reverse()
    total_price = sum(
        order.totalPrice for order in order_queryset)
    # 汇总桌数
    total_table_num = len(order_queryset)
    #每桌均价
    if total_table_num == 0:
        average_price = 0
    else:
        average_price = total_price/total_table_num
    # return HttpResponse(total_price, total_table_num)
    return JsonResponse({"total_price": total_price, "total_table_num": total_table_num,
                         "average_price": average_price})


@require_http_methods(["GET"])
@eatdd_login_required
def weekly_dish_sales(request):
    # 获取当前日期和时间
    now = timezone.now()
    before_orders = now - timezone.timedelta(days=7)
    # 查询本周内每个菜品的销量总和,除小料外，排行前6名的菜品。
    dish_sales = models.OrderItem.objects.filter(order__time__range=[before_orders, now]).values(
        'food__name').exclude(food_id='46').annotate(total_sales=Sum('num')).order_by('-total_sales')[:6]
    # 将查询结果转换为字典列表
    data_list = list(dish_sales)
    # 返回JSON响应
    return JsonResponse(data_list, safe=False)


@require_http_methods(["GET"])
@eatdd_login_required
# 后台调用定单
def manage_restaurant_order(request, restaurantId):
    if utils.BOSS_USERNAME in request.session:
        # Get certain boss' restaurant order
        order_queryset = models.Order.objects.filter(restaurant_id=restaurantId,
                                                     restaurant__boss_id=request.session[utils.BOSS_USERNAME]).order_by('time').reverse()
    elif utils.BUYER_USERNAME in request.session:
        order_queryset = models.Order.objects.filter(restaurant_id=restaurantId,
                                                     restaurant__order__user_id=request.session[utils.BUYER_USERNAME]).order_by('time').reverse()

    return utils.eatDDJsonResponse(order_queryset_to_array(order_queryset))


def order_to_dict(order):
    order_item_queryset = models.OrderItem.objects.filter(order=order)
    food_queryset = models.Food.objects.filter(orderitem__order=order)

    return_result = {}
    return_result['order_id'] = order.pk
    return_result['restaurant_id'] = order.restaurant_id
    return_result['table_name'] = order.table.table_name
    return_result['table_id'] = order.table_id
    return_result['nickname'] = order.nickname
    return_result['customer_id'] = order.user_id
    return_result['order_time'] = order.time.__str__()
    return_result['total_price'] = order.totalPrice
    return_result['notes'] = order.notes
    return_result['mobile'] = order.mobile
    return_result['detail'] = []
    for item in food_queryset:
        num = order_item_queryset.filter(food=item).first().num
        return_result['detail'].append({"food": food_ctrl.food_to_dict(item), "num": num})
    return return_result


def order_queryset_to_array(order_queryset):
    return_result = []
    for order in order_queryset:
        return_result.append(order_to_dict(order))
    return return_result


# 装饰器的函数会自动调用wrapper，然后用启动多线程来执行这个函数。
def async_call(fn):
    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

# 恢复包间状态
@async_call
def change_table_status(table_id):
    table = models.Table.objects.get(table_id=table_id)
    print("任务开始执行:", time.ctime())
    time.sleep(10800)
    table.status = 1
    table.save()
    print("任务执行结束:", time.ctime())
