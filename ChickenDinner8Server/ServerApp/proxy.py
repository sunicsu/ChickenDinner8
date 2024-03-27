#!/usr/bin/python                                                                  
# -*-encoding=utf8 -*-                                                             
# @Author         : imooc
# @Email          : imooc@foxmail.com
# @Created at     : 2018/11/2
# @Filename       : proxy.py
# @Desc           :

import ChickenDinner8Server.settings


def proxy():
    if ChickenDinner8Server.settings.USE_PROXY:
        # add your proxy here
        return {}
    else:
        return {}
