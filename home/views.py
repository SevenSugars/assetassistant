from django.shortcuts import render
from . import models
import tushare as ts
import pandas as pd

pd.set_option('max_colwidth', 20000)

def regist(request):
    pass

def login(request):
    pass

def news(request):
    info = ts.get_latest_news(top=2, show_content=True)
    news = models.News()
    news.title = info.title[0].__str__()
    news.content = info.content[0].__str__()
    news.save()
    news = models.News()
    news.title = info.title[1].__str__()
    news.content = info.content[1].__str__()
    news.save()
    return render(request, 'news.html', {'news':news})

def recommend(request):
    pass

def tutorial(request):
    pass

def showstock(request):
    pass

def showfund(request):
    pass

