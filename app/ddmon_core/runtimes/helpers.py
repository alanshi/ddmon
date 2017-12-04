# coding: utf-8

from __future__ import print_function, unicode_literals, absolute_import

import re
from random import randrange

from ..models import User


# ----------------------------------------------------------------------
def is_moblie_number(moblie_number):
    """检查是否是一个手机号码"""
    if re.match('^1[0-9]{10}$', moblie_number) is None:
        return False

    return True


# ----------------------------------------------------------------------
def create_one_ramdom_sms_code():
    """创建一个短信用密码,格式为字符串"""
    return str(randrange(100000, 999999))


# ----------------------------------------------------------------------
def search_or_create_user_match_mobile_number(mobile_number):
    """基于 mobile_number 查找 user, 如果不存在就创建一个, 并返回
    Return:
        user
        is_new_user
    """
    is_new_user = False

    user = User.objects.filter(mobile_number=mobile_number).first()
    if user is None:
        is_new_user = True
        user = User.objects.create_user(mobile_number=mobile_number)
        user.save()

    return user, is_new_user
