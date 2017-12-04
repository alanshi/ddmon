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
    api_view
)

from rest_framework.response import Response

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

from app.ddmon_core.runtimes.drf_api_base_class import DrfApiGenericViewSet
from app.ddmon_core.runtimes.drf_api_error_code import DrfApiErrorCode, get_api_error_info
from app.ddmon_core.serializers import (
    MonitorData,
    Profile
)

from app.ddmon_core.serializers import (
    MonitorDataSerializer
)


class MonitorViewSet(DrfApiGenericViewSet):

    serializer_class = MonitorDataSerializer
    permission_classes = (AllowAny,)

    def create(self, request):

        secret_key = request.data.get('secret_key')
        access_token = request.data.get('access_token')
        json_data = request.data.get('json_data')

        profile = Profile.objects.get(
            secret_key=secret_key,
            access_token=access_token
        )

        if not profile:
            return Response({'msg': 'access&secret error'})

        md = MonitorData(
            uid=profile.user.id,
            json_data=json_data
        )
        md.save()
        return Response(
            {'msg': 'success'},
            status=status.HTTP_200_OK
        )

class MonitorDataChartSet(DrfApiGenericViewSet,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                          ):

    serializer_class = MonitorDataSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):

        """只能获取自己的信息"""
        data =  MonitorData.objects.filter(uid=self.request.user.id)
        return data


