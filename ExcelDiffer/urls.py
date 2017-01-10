"""ExcelDiffer URL Configuration

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
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from ExcelDifferApp import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^listHistory/', views.listHistory, name='listHistory'),
    url(r'^getHistoryReport/(\d+)', views.getHistoryReport, name='getHistoryReport'),
    url(r'^downloadReport/(\d+)', views.downloadReport, name='downloadReport'),
    url(r'^diff/',views.diff, name='diff'),
    url(r'^admin/', include(admin.site.urls)),
]
