# coding=utf-8


from __future__ import print_function, unicode_literals, absolute_import


from django.conf.urls import include, url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from app.ddmon_core.views import api


# default ---
router_default = routers.DefaultRouter()

# auth
router_default.register(r'auth', api.user.AuthViewSet, base_name='api-users-login')

# users/profiles
router_default.register(r'users', api.user.UserViewSet, base_name='api-users')
router_default.register(r'profiles', api.user.ProfileViewSet, base_name='api-profiles')

# monitors
router_default.register(r'monitors', api.monitor.MonitorViewSet, base_name='api-monitors')

router_default.register(r'data', api.monitor.MonitorDataChartSet, base_name='api-data')


urlpatterns = [
    url(r'^', include(router_default.urls)),
]
