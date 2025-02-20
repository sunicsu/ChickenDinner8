from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class BusinessUser(models.Model):
    username = models.CharField(max_length=100, primary_key=True)
    password = models.TextField()
    avatar = models.URLField()


class NormalUser(models.Model):
    id = models.AutoField(primary_key=True)
    open_id = models.CharField(max_length=100)
    nickname = models.CharField(null=True, max_length=100)
    telephone = models.TextField(null=True, max_length=100)
    avatar = models.URLField(null=True, max_length=100)


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    image = models.URLField()
    description = models.CharField(max_length=100)
    boss = models.ForeignKey(BusinessUser, on_delete=models.CASCADE)


class Table(models.Model):
    id = models.AutoField(primary_key=True)
    table_id = models.IntegerField()
    table_name = models.CharField(max_length=20)
    station = models.CharField(max_length=50)
    status = models.BooleanField(default=True, verbose_name="是否可定")


class GoodsCategory(models.Model):
    """
    商品类别
    """
    CATEGORY_TYPE = (
        (1, "一级类目"),
        (2, "二级类目"),
        (3, "三级类目"),
    )

    name = models.CharField(default="", max_length=30, verbose_name="类别名", help_text="类别名")
    code = models.CharField(default="", max_length=30, verbose_name="类别code", help_text="类别code")
    desc = models.TextField(default="", verbose_name="类别描述", help_text="类别描述")
    category_type = models.IntegerField(choices=CATEGORY_TYPE, verbose_name="类目级别", help_text="类目级别")
    parent_category = models.ForeignKey("self", blank=True, verbose_name="父类目级别", help_text="父目录",
                                        related_name="sub_cat", on_delete=models.SET_NULL, null=True )
    is_tab = models.BooleanField(default=False, verbose_name="是否导航", help_text="是否导航")
    # add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "商品类别"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Food(models.Model):
    category = models.ForeignKey(GoodsCategory, verbose_name="商品类目", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    newCode = models.CharField(max_length=50, default="", verbose_name="商品唯一编码", null=True)
    price = models.DecimalField(decimal_places=5, max_digits=10)
    newSpec = models.TextField(null=True)
    newUnit = models.TextField(null=True)
    newStatus = models.TextField(null=True)
    description = models.TextField(null=True)
    image = models.URLField()
    priority = models.IntegerField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    add_time = models.DateTimeField(auto_now_add=True, editable=False)


class Order(models.Model):
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    totalPrice = models.DecimalField(decimal_places=5, max_digits=10)
    notes = models.TextField(null=True)
    mobile = models.TextField(null=True)
    nickname = models.TextField(null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    num = models.IntegerField()


class image(models.Model):
    data = models.ImageField(upload_to='upload/')


class TakeImage(models.Model):
    picture = models.ImageField(upload_to='upload/', verbose_name='晒图')
    title = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    text = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True, editable=False)
    likecount = models.IntegerField(default=0)
    unlikecount = models.IntegerField(default=0)
    canlike = models.BooleanField(default=True)




# class GoodsCategoryBrand(models.Model):
#     """
#     品牌名
#     """
#     category = models.ForeignKey(GoodsCategory, related_name='brands', blank=True, verbose_name="商品类目", on_delete=models.SET_NULL, null=True)
#     name = models.CharField(default="", max_length=30, verbose_name="品牌名", help_text="品牌名")
#     desc = models.TextField(default="", max_length=200, verbose_name="品牌描述", help_text="品牌描述")
#     image = models.ImageField(max_length=200, upload_to="brands/")
#     add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
#
#     class Meta:
#         verbose_name = "品牌"
#         verbose_name_plural = verbose_name
#         db_table = "goods_goodsbrand"
#
#     def __str__(self):
#         return self.name
#
#
# class Goods(models.Model):
#     """
#     商品
#     """
#     category = models.ForeignKey(GoodsCategory, verbose_name="商品类目", on_delete=models.SET_NULL, null=True)
#     goods_sn = models.CharField(max_length=50, default="", verbose_name="商品唯一货号")
#     name = models.CharField(max_length=100, verbose_name="商品名")
#     click_num = models.IntegerField(default=0, verbose_name="点击数")
#     sold_num = models.IntegerField(default=0, verbose_name="商品销售量")
#     fav_num = models.IntegerField(default=0, verbose_name="收藏数")
#     goods_num = models.IntegerField(default=0, verbose_name="库存数")
#     market_price = models.FloatField(default=0, verbose_name="市场价格")
#     shop_price = models.FloatField(default=0, verbose_name="本店价格")
#     goods_brief = models.TextField(max_length=500, verbose_name="商品简短描述")
#     # goods_desc = UEditorField(verbose_name=u"内容", imagePath="goods/images/", width=1000, height=300,
#     #                           filePath="goods/files/", default='')
#
#     ship_free = models.BooleanField(default=True, verbose_name="是否承担运费")
#     goods_front_image = models.ImageField(upload_to="goods/images/", null=True, blank=True, verbose_name="封面图")
#     is_new = models.BooleanField(default=False, verbose_name="是否新品")
#     is_hot = models.BooleanField(default=False, verbose_name="是否热销")
#     add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
#
#     class Meta:
#         verbose_name = '商品'
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.name