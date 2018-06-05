"""assetassistant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('account/', views.sign),
    path('news/', include('home.newsurls')),
    path('recommend/', views.recommend),
    path('tutorial/', views.tutorial),
    path('tutorial/blog1/', views.blog1),
    path('tutorial/blog2/', views.blog2),
    path('tutorial/blog3/', views.blog3),
    path('tutorial/blog4/', views.blog4),
    path('tutorial/blog5/', views.blog5),
    path('tutorial/blog6/', views.blog6),
    path('tutorial/blog7/', views.blog7),
    path('tutorial/blog8/', views.blog8),
    path('tutorial/blog9/', views.blog9),
    path('tutorial/blog10/', views.blog10),
    path('home/', include('home.urls1')),
    path('stock/', include('home.urls2')),
    path('fund/', include('home.urls3')),
    path('error/', views.error),
    path('alterasset/', views.alterasset),
]
