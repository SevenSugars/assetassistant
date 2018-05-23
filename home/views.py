from django.shortcuts import render
from . import models
import tushare as ts
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

pd.set_option('max_colwidth', 20000)

def regist(request):
    pass

def login(request):
    pass

def newspage(request):
    info = ts.get_latest_news(top=2, show_content=True)
    news = models.News()
    news.title = info.title[0].__str__()
    news.content = info.content[0].__str__()
    news.save()
    news = models.News()
    news.title = info.title[1].__str__()
    news.content = info.content[1].__str__()
    news.save()
    news = models.News.objects.all()
    return render(request, 'news.html', {'news': news})

def shownews(request, news_id):
    news = models.News.objects.get(pk=news_id)
    return render(request, 'newsdetail.html', {'news': news})

def recommend(request):
    if not models.RecommendFund.objects.all():
        r = requests.get('http://fund.eastmoney.com/trade/default.html')
        encode_content = r.content.decode('gb2312')
        soup = BeautifulSoup(encode_content, 'lxml')
        name = soup.find_all('td', 'fname')
        pattern1 = re.compile("<td>(\d\d\d\d\d\d)</td>")
        code = re.findall(pattern1, encode_content)
        rate = []
        for item in code[0:25]:
            r = requests.get('http://fund.eastmoney.com/pingzhongdata/' + item + '.js')
            pattern3 = re.compile('var syl_1n="(.*?)"')
            tmp = re.findall(pattern3, r.text)
            #tmp[0] += '%'
            rate.append(tmp[0])
        for i in range(0, 25):
            recF = models.RecommendFund()
            recF.code = code[i]
            recF.name = name[i].string
            recF.annualrate = rate[i]
            recF.save()
    recF = models.RecommendFund.objects.all()
    return render(request, 'recommend.html', {'recF': recF})

def tutorial(request):
    pass

def showstock(request):
    pass

def showfund(request, fund_code):
    fund_code = str(fund_code)
    while len(fund_code) < 6:
        fund_code = '0' + fund_code
    r = requests.get('http://fund.eastmoney.com/pingzhongdata/' + fund_code + '.js')
    pattern0 = re.compile('var fS_name = "(.*?)"')
    name = re.findall(pattern0, r.text)
    print(name, fund_code)
    pattern1 = re.compile('var syl_1n="(.*?)"')
    oneyear = re.findall(pattern1, r.text)
    pattern2 = re.compile('var syl_6y="(.*?)"')
    sixmonth = re.findall(pattern2, r.text)
    pattern3 = re.compile('var syl_3y="(.*?)"')
    threemonth = re.findall(pattern3, r.text)
    pattern4 = re.compile('var syl_1y="(.*?)"')
    onemonth = re.findall(pattern4, r.text)
    pattern5 = re.compile('"y":(.*?),"equityReturn"')
    price = re.findall(pattern5, r.text)
    pattern6 = re.compile('"equityReturn":(.*?),"unitMoney"')
    rate = re.findall(pattern6, r.text)
    fund = models.Fund()
    fund.code = fund_code
    fund.name = name[0]
    fund.annualrate = oneyear[0]
    fund.sixmrate = sixmonth[0]
    fund.threemrate = threemonth[0]
    fund.onemrate = onemonth[0]
    fund.price = price[-1]
    fund.currentrate =  rate[-1]
    fund.save()
    return render(request, 'funddetail.html', {'fund': fund})


