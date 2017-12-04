# coding: utf-8

from __future__ import print_function, unicode_literals, absolute_import

from rest_framework import serializers

from .models import (
    User,
    Profile,
    MonitorData
)

class MobileNumberField(serializers.Field):
    """手机号显示格式化"""
    def get_attribute(self, obj):
        # We pass the object instance onto `to_representation`,
        # not just the field attribute.
        return obj

    def to_representation(self, obj):
        """
        只显示最后4位，其它位用 * 号替代
        """
        last_4_number = obj.mobile_number[len(obj.mobile_number)-4:]

        return '{:*>11}'.format(last_4_number)


class UserSerializer(serializers.ModelSerializer):
    """"""
    mobile_number = MobileNumberField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'mobile_number')


class ProfileSerializer(serializers.ModelSerializer):
    """"""
    class Meta:
        model = Profile
        read_only_fields = ('user', 'time_created', 'avatar','intro','nickname')
        fields = '__all__'


class MonitorDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonitorData
        fields = ('json_data','time_created')





