# coding: utf-8

from __future__ import print_function, unicode_literals, absolute_import

from enum import IntEnum, unique


@unique
class DrfApiErrorCode(IntEnum):
    """
    AABBBBCC
    A: django app, 起始值 10
    B: group, 起始值 0001
    C: number, 起始值 01
    """
    # API 接口通用错误
    API_COMMON_UNDEFINED = 10000000  # 通用未定义错误, 在 API client 端需要解析的情况下, 不能返回这个错误码
    API_COMMON_DEPRECATED = 10000001  # 已废弃的接口

    API_PARAM_MISS = 10000101  # 缺少参数
    API_PARAM_INVALID = 10000102  # 参数值不正确

    # API auth 接口错误
    API_AUTH_UNDEFINED = 200100  # 未定义错误
    API_AUTH_LOGIN_SMS_CODE_REQUEST_SO_FAST = 200101

    # API users 接口错误
    API_USERS_UNDEFINED = 200200  # 未定义错误

    # API assets 接口错误
    API_ASSETS_UNDEFINED = 210100  # 未定义错误
    API_ASSETS_HOLDER_STATUS_ERROR = 210101  # 持有人状态错误


def get_api_error_info(error_code, error_message_ext=None):
    """废弃"""
    result = {
        'code': 'E{}'.format(error_code.value),
    }

    if error_message_ext is None:
        result['message'] = error_code.name
    else:
        result['message'] = '{}: {}'.format(error_code.name, error_message_ext)

    return result
