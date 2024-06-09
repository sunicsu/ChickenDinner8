from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
import json
from django.core import serializers
from django.shortcuts import render
from rest_framework import renderers
# from rest_framework import serializers
from rest_framework.response import Response
from django.db.models import Count
from django.db.models import Q
from ServerApp import models
from .auth_required_decorator import eatdd_login_required
from . import utils
from . serializers import FoodSerializer


@require_http_methods(["GET", "PUT", "DELETE"])
@eatdd_login_required
def manage_food(request, restaurantId, foodId):
    if request.method == 'GET':
        queryset = models.Food.objects.filter(restaurant_id=restaurantId, pk=foodId)
        if queryset.exists():
            return utils.eatDDJsonResponse(food_to_dict(queryset.first()))
        else:
            return HttpResponse("Not exist", status=404)
    elif request.method == 'DELETE':
        queryset = models.Food.objects.filter(restaurant_id=restaurantId,
                                              pk=foodId,
                                              restaurant__boss_id=request.session[utils.BOSS_USERNAME])
        if queryset.exists():
            queryset.delete()
            return HttpResponse('Deleted!', status=200)
        else:
            return HttpResponse('This Food did not exist', status=405)
    elif request.method == 'PUT':
        if utils.BOSS_USERNAME in request.session:
            queryset = models.Food.objects.filter(restaurant_id=restaurantId,
                                                  pk=foodId,
                                                  restaurant__boss_id=request.session[utils.BOSS_USERNAME])
            if queryset.exists():
                obj = queryset.first()
                received_data = json.loads(request.body.decode('utf-8'))
                obj.name = received_data['food_name']
                obj.description = received_data['description']
                obj.price = received_data['price']
                obj.image=received_data['image']
                obj.priority=received_data['priority']
                obj.newCode = received_data['newCode']
                obj.category_id = received_data['categoryName']
                obj.newSpec = received_data['newSpec']
                obj.newUnit = received_data['newUnit']
                obj.newStatus = received_data['newStatus']
                obj.save()
                return utils.eatDDJsonResponse(food_to_dict(obj))
            else:
                return HttpResponse('This Food did not exist', status=405)
        else:
            return HttpResponse('You DO NOT have access to modify this food')
    return HttpResponse(restaurantId, status=200)


@require_http_methods(["POST"])
@eatdd_login_required
def create_food(request, restaurantId):
    received_data = json.loads(request.body.decode('utf-8'))
    print(received_data)
    new_food = models.Food(name=received_data['food_name'],
                           description=received_data['description'],
                           price=received_data['price'],
                           image=received_data['image'],
                           newCode=received_data['newCode'],
                           category_id=received_data['categoryName'],
                           newSpec=received_data['newSpec'],
                           newUnit=received_data['newUnit'],
                           newStatus=received_data['newStatus'],
                           priority=received_data['priority'],
                           restaurant_id=restaurantId)
    new_food.save()
    return utils.eatDDJsonResponse(food_to_dict(new_food))

# 菜品分组返回
@require_http_methods(["GET"])
def get_menu(request, restaurantId):
    queryset1 = models.Food.objects.filter(restaurant_id=restaurantId).annotate(num_items=Count('category_id'))
    queryset = queryset1.annotate(name_count=Count('category_id')).order_by('category_id')
    # print(queryset)
    return utils.eatDDJsonResponse({"foods": food_queryset_to_array(queryset)})

# 获取指定分类下的所有菜品
@require_http_methods(["GET"])
def get_category_dish(request, restaurantId, category_id):
    queryset = models.Food.objects.filter(Q(restaurant_id=restaurantId) & Q(category_id=category_id))
    print(queryset)
    return utils.eatDDJsonResponse({"foods": food_queryset_to_array(queryset)})


def food_to_dict(new_food):
    return {
        "food_id": new_food.pk,
        "food_name": new_food.name,
        "description": new_food.description,
        "price": new_food.price,
        "priority": new_food.priority,
        "image": new_food.image,
        "newcode": new_food.newCode,
        "categoryname": new_food.category.name,
        "newspec": new_food.newSpec,
        "newunit": new_food.newUnit,
        "newstatus": new_food.newStatus,
        # "category": new_food.category
    }


def food_queryset_to_array(queryset):
    foods = []
    for item in queryset:
        foods.append(food_to_dict(item))
    return foods


# 读取所有分类下的商品
@require_http_methods(["GET"])
def category_dish(request):
    categories = models.GoodsCategory.objects.all()
    # print(categories)
    # dish_category = {}
    category_all_dish = []
    all_foods = models.Food.objects.all()
    # print(all_foods)
    for category in categories:
        dish_category = {}
        foods = all_foods.filter(category_id=category)
        dish_category['cat_name'] = category.name
        dish_category['children'] = food_queryset_to_array(foods)
        category_all_dish.append(dish_category)
        # dish_category[category.name] = serializers.serialize("json", models.Food.objects.filter(category=category))
    # print(dish_category)
    print(category_all_dish)

    return JsonResponse(category_all_dish, safe=False)

    # products_by_category 现在是一个字典，包含了所有分类及其对应的商品列表