from django.urls import path
from . import views

urlpatterns = [
    path('', views.showinfo),
    path('favourite/', views.favourite),
    path('own/', views.showown),
]