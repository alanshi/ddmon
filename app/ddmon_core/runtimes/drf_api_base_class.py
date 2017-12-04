# coding=utf-8


"""
https://gist.github.com/rexzhang/58e80a6e588f0c964c4e9e07385d502b
"""


from __future__ import print_function, unicode_literals, absolute_import

import re
import logging
import inspect

from rest_framework import exceptions
from rest_framework.exceptions import APIException
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import (
    renderer_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response

from .drf_api_error_code import DrfApiErrorCode


logger = logging.getLogger(__name__)


class DrfApiGenericViewSet(GenericViewSet):

    # ----------------------------------------------------------
    # View 代码简化
    def is_request_data_complete(self, request_param_list, method='GET'):
        """request 参数如果有缺失，直接抛异常"""
        if method == 'GET':
            request_param_data = self.request.query_params
        else:
            request_param_data = self.request.data

        for param in request_param_list:
            if param not in request_param_data:
                raise DrfApiError(
                    error_code=DrfApiErrorCode.API_PARAM_MISS,
                    error_message_ext="param miss:{}".format(param)
                )

    def get_params_data(self, required_param_key_list=None, raise_exception=True):
        """获取 request 的数据，无论 GET 还是 POST 方法, 如果缺失任何必要参数，可选抛异常"""
        if self.request.method == 'GET':
            request_params_data = self.request.query_params
        else:
            request_params_data = self.request.data

        if required_param_key_list is not None:
            miss_param_key_set = set(required_param_key_list) - set(request_params_data)
            if len(miss_param_key_set) >= 1 and raise_exception:
                raise DrfApiError(
                    error_code=DrfApiErrorCode.API_PARAM_MISS,
                    error_message_ext="param miss:{}".format(miss_param_key_set)
                )

        return request_params_data

    def get_object_by_pk(self, pk=None, raise_exception=False):
        """根据给定的 pk 获取对应的 object, 如果未找到(包含不存在/没有权限找到/不属于自己)可以选择抛出异常"""
        try:
            obj = self.get_queryset().filter(id=pk).first()
        except ValueError:
            if raise_exception:
                raise exceptions.NotFound()
            else:
                return None

        if obj is None and raise_exception:
            raise exceptions.NotFound()

        return obj

    @staticmethod
    def raise_api_exception(error_code, error_message_ext=None):
        """生成异常 error 信息,并抛出异常"""
        logger.warning('API Error, code:{} name:{} message_ext:{}'.format(
            error_code, error_code.name, error_message_ext
        ))
        raise DrfApiError(error_code=error_code, error_message_ext=error_message_ext)

    # ----------------------------------------------------------
    # 开发阶段工具

    @staticmethod
    def get_django_choices_info(choices, is_display_desc=False):
        """获取 Django choices 类型信息,主要用于开发辅助接口"""
        choices_list = []
        if is_display_desc:
            for name, desc in choices:
                choices_list.append({
                    'name': name,
                    'desc': desc,
                })

        else:
            for item in choices:
                choices_list.append(item[0])

        return choices_list


# TODO: 需要重新设计, 尝试与 DRF 风格一致
# error_message_ext ==> detail ??
# code:
#       number
#       name
class DrfApiError(APIException):
    status_code = 400
    default_detail = 'drf_api extend error info'
    default_code = 'drf_api_extend_error'

    def __init__(self, error_code, error_message_ext=None):
        self.detail = self.get_error_detail_info(error_code=error_code, error_message_ext=error_message_ext)
        return

    @staticmethod
    def get_error_detail_info(error_code, error_message_ext):
        """生成 error detail 信息"""
        error_detail = {
            'detail': 'drf_api extend error',
            'error': {
                'code': error_code.value,
                'name': error_code.name,
            }
        }
        if error_message_ext is None:
            error_detail['error']['message_ext'] = None
        else:
            error_detail['error']['message_ext'] = '{}'.format(error_message_ext)

        return error_detail


class DrfApiErrorCodeViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated, ]

    def __init__(self, drf_api_error_code_class, **kwargs):
        super(DrfApiErrorCodeViewSet, self).__init__(**kwargs)

        self.drf_api_error_code_list = list(drf_api_error_code_class)
        self.drf_api_error_code_source = inspect.getsource(drf_api_error_code_class).decode('utf-8')

        self.drf_api_error_code_number_length = 8
        self.drf_api_error_code_info_list = []
        return

    @staticmethod
    def get_error_message_string(error_code, error_code_source):
        f = re.findall(r'{} .+\n'.format(error_code), error_code_source)
        if len(f) >= 1:
            error_message = f[0]

            m = re.match(r'{}  # (?P<error_message>.+)\n'.format(error_code), error_message)
            error_message = m.group('error_message')
        else:
            error_message = ''

        return error_message

    @renderer_classes((StaticHTMLRenderer, ))
    def list(self, request):
        """[工具接口]列出 error_code"""
        error_info_list = []
        drf_api_check_fail_info_list = []

        for api_error in self.drf_api_error_code_list:
            error_info = {
                'code': api_error.value,
                'name': api_error.name,
                'message': self.get_error_message_string(
                    error_code=api_error.value,
                    error_code_source=self.drf_api_error_code_source
                ),
            }
            if len('{}'.format(api_error.value)) != self.drf_api_error_code_number_length:
                drf_api_check_fail_info_list.append({
                    'code': api_error.value,
                    'message': 'error code length no match',
                })

            error_info_list.append(error_info)

        return Response({
            'drf_api_check_fail_info_list': drf_api_check_fail_info_list,
            'error_info_list': error_info_list,
        })
