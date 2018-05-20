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
    news = models.News()
    news.title = ts.get_latest_news(top=1, show_content=True).title.to_string(index=False)
    news.content = ts.get_latest_news(top=1, show_content=True).content.to_string(index=False)
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

