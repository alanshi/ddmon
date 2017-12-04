"""ipast URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    # url(r'^', include(router.urls)),

    # url(r'^article/', include('app.article.urls')),
    # url(r'^users/', include('app.account.urls')),
    #url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('app.ddmon_core.urls.api')),
    url(r'^portal/', include('app.ddmon_portal.urls.portal')),
]


if settings.DEBUG:

    urlpatterns += [
        url(r'^admin/', admin.site.urls),
        #url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]

    # # for swagger v0.3
    # urlpatterns += [
    #     url(r'^api/v1/docs/', include('rest_framework_swagger.urls')),
    # ]

    # for swagger v2
    # from rest_framework_swagger.views import get_swagger_view
    from app.ddmon_core.runtimes.swagger_utils import get_swagger_view
    schema_view = get_swagger_view(title='Asset Checker API')
    urlpatterns += [
        url(r'^api/docs/', schema_view),
    ]

    # for DRF built-in API documentation
    from rest_framework.documentation import include_docs_urls
    urlpatterns += [
        url(r'^api/docs-drf/', include_docs_urls(title='Asset Checker API'))
    ]

    # for static files
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
