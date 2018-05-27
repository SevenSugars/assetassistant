from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from . import models
import tushare as ts
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import date
import matplotlib.pyplot as plt
import json
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
pd.set_option('max_colwidth', 20000)

def index(request):
    return render(request, 'index.html')

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def sendemail(c, e):
    from_addr = '178414306@qq.com'
    password = 'afipsxglvphmcahg'
    to_addr = e
    smtp_server = 'smtp.qq.com'
    message = '您好！您的验证码是：' + c
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = _format_addr('理财小助手 <%s>' % from_addr)
    msg['To'] = _format_addr('尊敬的用户 <%s>' % to_addr)
    msg['Subject'] = Header('[理财小助手]激活邮箱账号', 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def sign(request):
    if request.is_ajax():
        if request.POST.get('vericode'):
            vericode = request.POST.get('vericode')
            email = request.POST.get('email')
            sendemail(vericode, email)
        else:
            print("error")
    if request.method == 'GET':
        if request.GET:
            user = models.User()
            user.username = request.GET.get('username')
            user.password = request.GET.get('password')
            user.emailaddress = request.GET.get('email')

    return render(request, 'sign.html')

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
    #print(name, fund_code)
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
    pattern = re.compile('var Data_grandTotal = \[(.*?)\];')
    tmp = re.findall(pattern, r.text)
    data = tmp[0].split('},{')
    data[0] = data[0] + '}'
    data[1] = '{' + data[1] + '}'
    data[2] = '{' + data[2]
    funddata = pd.DataFrame(json.loads(data[0]))
    averagedata = pd.DataFrame(json.loads(data[1]))
    hsdata = pd.DataFrame(json.loads(data[2]))
    #画图
    time = []
    rate = []
    for item in funddata['data']:
        x = date.fromtimestamp(item[0] / 1000)
        time.append(date.strftime(x, '%Y-%m-%d'))
        rate.append(item[1])
    funddata['time'] = time
    funddata['rate'] = rate
    funddata.drop('data', axis=1, inplace=True)
    funddata.rename(columns={'rate': funddata['name'][0]}, inplace=True)
    funddata.drop('name', axis=1, inplace=True)
    # funddata = funddata.set_index(['time'])
    time = []
    rate = []
    for item in averagedata['data']:
        x = date.fromtimestamp(item[0] / 1000)
        time.append(date.strftime(x, '%Y-%m-%d'))
        rate.append(item[1])
    averagedata['time'] = time
    averagedata['rate'] = rate
    averagedata.drop('data', axis=1, inplace=True)
    averagedata.rename(columns={'rate': averagedata['name'][0]}, inplace=True)
    averagedata.drop('name', axis=1, inplace=True)
    # averagedata = averagedata.set_index(['time'])
    tmp = pd.merge(funddata, averagedata, on='time')
    time = []
    rate = []
    for item in hsdata['data']:
        x = date.fromtimestamp(item[0] / 1000)
        time.append(date.strftime(x, '%Y-%m-%d'))
        rate.append(item[1])
    hsdata['time'] = time
    hsdata['rate'] = rate
    hsdata.drop('data', axis=1, inplace=True)
    hsdata.rename(columns={'rate': hsdata['name'][0]}, inplace=True)
    hsdata.drop('name', axis=1, inplace=True)
    result = pd.merge(tmp, hsdata, on='time')
    result = result.set_index(['time'])
    plt.figure()
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    result.plot(rot=30)
    plt.ylabel('累计涨跌率(%)')
    plt.legend(loc='best')
    plt.savefig(r'static\fund.png')
    plt.close('all')
    if request.method == 'POST':
        favall = models.Favourite.objects.all()
        flag = False
        for item in favall:
            if fund_code == item.code:
                flag = True
                break
        if flag == False:
            fav = models.Favourite()
            fav.code = fund_code
            fav.name = name[0]
            fav.rate = oneyear[0]
            fav.save()
    return render(request, 'funddetail.html', {'fund': fund})

def buy(request):
    pass

def sell(request):
    pass

def showinfo(request):
    pass

def favourite(request):
    fav = models.Favourite.objects.all()
    return render(request, 'favourite.html', {'fav': fav})

def showown(request):
    pass

def showhist(request):
    pass