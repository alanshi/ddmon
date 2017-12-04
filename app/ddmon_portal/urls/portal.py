# coding: utf-8

from django.conf.urls import  url

from app.ddmon_portal.views import (
    dashboard,
)

urlpatterns = [
    url(r'^$', dashboard.Dashboard.as_view(), name='portal-dashboard' ),
]
