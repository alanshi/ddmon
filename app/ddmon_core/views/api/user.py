# coding: utf-8

from __future__ import print_function, unicode_literals, absolute_import

from django.conf import settings
from django.core.cache import caches
from django.utils import timezone
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import (
    list_route,
    detail_route,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from app.ddmon_core.models import (
    User,
    Profile,
)

from app.ddmon_core.runtimes.helpers import (
    is_moblie_number,
    create_one_ramdom_sms_code,
    search_or_create_user_match_mobile_number,
)

from app.ddmon_core.runtimes.drf_api_base_class import DrfApiGenericViewSet
from app.ddmon_core.runtimes.drf_api_error_code import DrfApiErrorCode, get_api_error_info
from app.ddmon_core.serializers import (
    UserSerializer,
    ProfileSerializer,
)


class AuthViewSet(DrfApiGenericViewSet):
    """"""
    permission_classes = (AllowAny,)

    @list_route()
    def login_sms_code(self, request):
        """获取 登录用手机短信验证码
        ---
        parameters:
            - name: mobile_number
              description: 电话号码
              required: true
              type: string
              location: query
        """
        if request.GET.get('mobile_number') is None:
            return Response({
                'error': get_api_error_info(
                    DrfApiErrorCode.API_PARAM_MISS,
                    error_message_ext='mobile_number'
                ),
            }, status=status.HTTP_400_BAD_REQUEST)

        mobile_number = request.GET['mobile_number']
        # 检查 mobile_number 格式是否正确
        if not is_moblie_number(mobile_number):
            return Response({
                'error': get_api_error_info(
                    DrfApiErrorCode.API_PARAM_INVALID,
                    error_message_ext='mobile_number'
                ),
            }, status=status.HTTP_400_BAD_REQUEST)

        # 生成 login_sms_code 保存到 cache 中，并加上有效时间
        cache = caches['login_sms_code']
        if cache.get(mobile_number) and  settings.DEBUG:
            self.raise_api_exception(
                error_code=DrfApiErrorCode.API_AUTH_LOGIN_SMS_CODE_REQUEST_SO_FAST
            )

        # 生成验证码
        login_sms_code = create_one_ramdom_sms_code()
        cache.set(mobile_number, login_sms_code)

        if settings.DEBUG:

            response_data = {
                'login_sms_code': login_sms_code,
            }
        else:
            # 发送验证码短信, 待实现!!!!
            response_data = {}

        return Response(response_data, status=status.HTTP_200_OK)

    @list_route()
    def login(self, request):
        """使用 手机号 + 登录用手机短信验证码 完成 登录／自动创建账号 操作
        ---
        parameters:
            - name: mobile_number
              description: 电话号码
              required: true
              type: string
              location: query

            - name: login_sms_code
              description: 短信校验码
              required: true
              location: query

        responseMessages:
            - code: '400'
              message: 输入参数错误
        """
        if request.GET.get('mobile_number') is None or request.GET.get('login_sms_code') is None:
            return Response({
                'error': get_api_error_info(
                    DrfApiErrorCode.API_PARAM_MISS,
                    error_message_ext='mobile_number, login_sms_code'
                ),
            }, status=status.HTTP_400_BAD_REQUEST)

        mobile_number = request.GET['mobile_number']
        # 检查 mobile_number 格式是否正确
        if not is_moblie_number(mobile_number):
            return Response({
                'error': get_api_error_info(
                    DrfApiErrorCode.API_PARAM_INVALID,
                    error_message_ext='mobile_number'
                ),
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查 login_sms_code 是否存在、正确
        cache = caches['login_sms_code']
        login_sms_code_in_cache = cache.get(mobile_number)
        try:
            login_sms_code_in_input = request.GET['login_sms_code']
        except (ValueError, TypeError):
            login_sms_code_in_input = None

        if login_sms_code_in_cache is None or login_sms_code_in_cache != login_sms_code_in_input:
            return Response({
                'error': get_api_error_info(
                    DrfApiErrorCode.API_PARAM_INVALID,
                    error_message_ext='login_sms_code'
                ),
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查电话号码（用户）已经存在？如果不存在就创建用户
        user, is_new_user = search_or_create_user_match_mobile_number(mobile_number)

        # 获取 auth Token
        token, is_new_token = Token.objects.get_or_create(user=user)
        if not is_new_token:
            # 强制生成新的 auth token
            # 因为 key 是 pk ，所以直接 update 会导致异常
            Token.objects.filter(user=user).update(key=token.generate_key(), created=timezone.now())
            token = Token.objects.filter(user=user).first()

        # 获取用户信息
        profile = Profile.objects.filter(user=user).first()

        # 更新 user.last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login', ])

        return Response({
            'token': token.key,
            'is_new_user': is_new_user,
            'user': UserSerializer(user).data,
            'profile': ProfileSerializer(profile).data,
        }, status=status.HTTP_200_OK)


class UserViewSet(DrfApiGenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  ):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]


    def get_queryset(self):
        """只能获取自己的信息"""
        return User.objects.filter(id=self.request.user.id)

    @detail_route()
    def logout(self, request):
        return


class ProfileViewSet(DrfApiGenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin):
    """"""
    serializer_class = ProfileSerializer
    permission_classes = (AllowAny,)


    def get_queryset(self):
        """只能获取自己的信息"""
        return Profile.objects.filter(user=self.request.user)
        #return Profile.objects.all()
