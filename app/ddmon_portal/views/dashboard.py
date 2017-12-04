# coding: utf-8

from django.shortcuts import render
from django.views.generic import View
from django.http import response
from app.ddmon_core.models import (
    MonitorData
)


class Dashboard(View):
    template_name = 'dashboard/index.html'
    def get(self, request):
        info = MonitorData.objects.all().last()

        return render(
            request,
            self.template_name,
            {
                'info': info.json_data
            }
        )

    def post(self, request):
        pass
