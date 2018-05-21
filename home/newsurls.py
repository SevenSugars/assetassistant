from django.urls import path
from . import views

urlpatterns = [
    path('', views.newspage),
    path('<int:news_id>/', views.shownews),
]