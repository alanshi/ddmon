# coding: utf-8

from __future__ import unicode_literals

import uuid
from random import randrange

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField



class ModelBase(models.Model):
    """基本数据库模型"""
    id = models.UUIDField(
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False
    )

    """记录创建时间"""

    time_created = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True


# #######################################################################
class UserManager(BaseUserManager):
    """"""
    # ----------------------------------------------------------------------
    def _create_user(self, mobile_number, password, is_staff, is_superuser, **extra_fields):
        """"""
        if mobile_number is None:
            raise ValueError('User must have an moblie_number')

        now = timezone.now()

        user = self.model(
            mobile_number=mobile_number,
            last_login=now,
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser,

            **extra_fields
        )
        user.set_password(password)

        user.save(using=self._db)

        # create user's profile
        profile = Profile(user=user)
        profile.save()

        return user

    # ----------------------------------------------------------------------
    def create_user(self, mobile_number, password=None, **extra_fields):
        """"""
        if password is None:
            password = self.get_one_default_random_password()

        return self._create_user(
            mobile_number, password,
            is_staff=False, is_superuser=False,
            **extra_fields
        )

    # ----------------------------------------------------------------------
    def create_superuser(self, mobile_number, password, **extra_fields):
        """
        create supper user
        """
        return self._create_user(
            mobile_number, password,
            is_staff=True, is_superuser=True,
            **extra_fields
        )

    @staticmethod
    # ----------------------------------------------------------------------
    def get_one_default_random_password():
        """为 user 生成一个随机密码"""
        return randrange(0, stop=999999999)


class User(ModelBase, AbstractBaseUser, PermissionsMixin):
    """帐号用户模型，只保存基本信息"""

    mobile_number = models.CharField(
        max_length=11,
        blank=False,
        unique=True
    )  # 暂时只支持、保存11位部分

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )

    objects = UserManager()

    USERNAME_FIELD = 'mobile_number'

    def get_short_name(self):
        pass


# #######################################################################
class Profile(models.Model):
    """用户 profile 信息
    已经使用 User 作为主键，所以不能使用 ModelBase 为父类
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)

    # 记录创建时间
    time_created = models.DateTimeField(
        auto_now_add=True,
    )

    email = models.EmailField(
        max_length=100,
    )

    nickname = models.CharField(
        max_length=100,
        verbose_name='用户昵称',
        blank=True
    )
    intro = models.CharField(
        max_length=200,
        verbose_name='简介'
    )

    access_token = models.CharField(
        max_length=200,
        unique=True
    )
    secret_key = models.CharField(
        max_length=200,
        unique=True
    )


class MonitorData(models.Model):

    uid = models.CharField(
        max_length=100,
        verbose_name='uid',
        blank = True
    )

    json_data = JSONField()

    # 记录创建时间
    time_created = models.DateTimeField(
        auto_now_add=True,
    )
