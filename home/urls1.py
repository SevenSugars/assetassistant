from django.urls import path
from . import views

urlpatterns = [
    path('favourite/', views.favourite),
    path('own/', views.showown),
    path('hist/', views.showhist),
    path('asset/', views.showasset),
    path('recharge/', views.recharge),
    path('profit/', views.showprofit),
]