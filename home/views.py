import matplotlib
matplotlib.use('Agg')
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core import serializers
from . import models
import tushare as ts
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import date, datetime
import matplotlib.pyplot as plt
import json
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
from PIL import Image
from io import BytesIO
pd.set_option('max_colwidth', 20000)

code = '123456'

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
            try:
                user = models.User.objects.get(emailaddress=email)
            except:
                sendemail(vericode, email)
            else:
                info = '该邮箱已注册！'
                print(info)
                #return HttpResponseRedirect("/error/")
        elif request.POST.get('email'):
            email = request.POST.get('email')
            password = request.POST.get('password')
            try:
                user = models.User.objects.get(emailaddress=email)
            except:
                info = '该邮箱未注册！'
                print(info)
                try:
                    del request.session["username"]
                    del request.session["email"]
                except:
                    pass
                #return render(request, 'error.html', {'error': info})
            else:
                if user.password != password:
                    info = '密码错误！'
                    print(info)
                    try:
                        del request.session["username"]
                        del request.session["email"]
                    except:
                        pass
                    #return render(request, 'error.html', {'error': info})
                else:
                    request.session["email"] = email
                    username = user.username
                    request.session["username"] = username
                    print('登录成功。')
                    #return render(request, 'index.html')
        else:
            print("error")
    if request.method == 'GET':
        if request.GET:
            #用户数据库添加
            user = models.User()
            user.username = request.GET.get('username')
            user.password = request.GET.get('password')
            user.emailaddress = request.GET.get('email')
            #request.session["email"] = user.emailaddress
            #request.session["username"] = user.username
            user.save()
            #资产数据库创立
            asset = models.Personal_asset()
            asset.emailaddress = request.GET.get('email')
            asset.stock = 0
            asset.fund = 0
            asset.money = 5000000
            asset.save()
            info = models.Hist_asset()
            info.emailaddress = request.GET.get('email')
            info.stock = 0
            info.stockprofit = 0
            info.fund = 0
            info.fundprofit = 0
            info.money = 5000000
            info.save()
    return render(request, 'sign.html')


def newspage(request):
    info = ts.get_latest_news(top=2, show_content=True)
    newstmp1 = models.News.objects.order_by('-pk')[0]
    newstmp2 = models.News.objects.order_by('-pk')[1]
    news = models.News()
    news.title = info.title[0].__str__()
    news.content = info.content[0].__str__()
    if news.title != newstmp1.title and news.title != newstmp2.title:
        news.save()
    news = models.News()
    news.title = info.title[1].__str__()
    news.content = info.content[1].__str__()
    if news.title != newstmp1.title and news.title != newstmp2.title:
        news.save()
    news = models.News.objects.order_by('-pk')
    news1 = news[0]
    news2 = news[1]
    news3 = news[2]
    news = news[3:]
    return render(request, 'news.html', {'news': news, 'news1': news1, 'news2': news2, 'news3': news3})

def shownews(request, news_id):
    news = models.News.objects.get(pk=news_id)
    allnews = models.News.objects.order_by('-pk')[:5]
    return render(request, 'newsdetail.html', {'news': news, 'allnews': allnews})

def recommend(request):
    #基金
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
    #股票
    if not models.RecommendStock.objects.all():
        rs = ts.cap_tops()
        for i in range(0, 30):
            stock_code=rs.code[i]
            stockdata = requests.get('http://hq.sinajs.cn/list=sh' + stock_code)
            stockdatasplit = stockdata.text.split(',')
            if (len(stockdata.text) == 24):
                stockdata = requests.get('http://hq.sinajs.cn/list=sz' + stock_code)
                stockdatasplit = stockdata.text.split(',')
                stock = models.Stock()
                stock.code = stock_code
                stock.name = stockdatasplit[0][21:]
                stock.open = stockdatasplit[1]
                stock.close = stockdatasplit[2]
                if float(stock.close)==0:
                    continue
                stock.high = stockdatasplit[4]
                stock.low = stockdatasplit[5]
                stock.price = stockdatasplit[3]
                stock.currentrate = (float(stock.price) - float(stock.close)) / float(stock.close) * 100
            else:
                stock = models.Stock()
                stock.code = stock_code
                stock.name = stockdatasplit[0][21:]
                stock.open = stockdatasplit[1]
                stock.close = stockdatasplit[2]
                if float(stock.close)==0:
                    continue
                stock.high = stockdatasplit[4]
                stock.low = stockdatasplit[5]
                stock.price = stockdatasplit[3]
                stock.currentrate = (float(stock.price) - float(stock.close)) / float(stock.close) * 100
            w = round(stock.currentrate, 4)
            if abs(w)>11:
                continue
            recS = models.RecommendStock()
            recS.code = rs.code[i]
            recS.name = rs.name[i]
            recS.rate = w
            recS.save()
    recF = models.RecommendFund.objects.all()
    recS = models.RecommendStock.objects.all()
    if request.method == 'POST':
        code = request.POST.get('code')
        code = str(code)
        if len(code) != 6:
            info = '代码错误！'
            return render(request, 'error.html', {'error': info})
        stockdata = requests.get('http://hq.sinajs.cn/list=sh' + code)
        if (len(stockdata.text) <= 24):
            stockdata = requests.get('http://hq.sinajs.cn/list=sz' + code)
            if (len(stockdata.text) <= 24):
                r = requests.get('http://fund.eastmoney.com/pingzhongdata/' + code + '.js')
                pattern0 = re.compile('var fS_name = "(.*?)"')
                name = re.findall(pattern0, r.text)
                if len(name) == 0:
                    info = '代码错误！'
                    return render(request, 'error.html', {'error': info})
                pattern5 = re.compile('"y":(.*?),"equityReturn"')
                price = re.findall(pattern5, r.text)
                if price == []:
                    info = '代码错误！'
                    return render(request, 'error.html', {'error': info})
                path = r'http://127.0.0.1:8000/fund/' + code
                return HttpResponseRedirect(path)
        path = r'http://127.0.0.1:8000/stock/' + code
        return HttpResponseRedirect(path)
    return render(request, 'recommend.html', {'recF': recF, 'recS': recS})

def tutorial(request):
    return render(request, 'tutorial.html')

def blog1(request):
    return render(request, 'blog1.html')

def blog2(request):
    return render(request, 'blog2.html')

def blog3(request):
    return render(request, 'blog3.html')

def blog4(request):
    return render(request, 'blog4.html')

def blog5(request):
    return render(request, 'blog5.html')

def blog6(request):
    return render(request, 'blog6.html')

def blog7(request):
    return render(request, 'blog7.html')

def blog8(request):
    return render(request, 'blog8.html')

def blog9(request):
    return render(request, 'blog9.html')

def blog10(request):
    return render(request, 'blog10.html')

def showstock(request, stock_code):
    stock_code = str(stock_code)
    while len(stock_code) < 6:
        stock_code = '0' + stock_code

    stockdata = requests.get('http://hq.sinajs.cn/list=sh' + stock_code )
    stockdatasplit = stockdata.text.split(',')
    if(len(stockdata.text)==24):
        stockdata = requests.get('http://hq.sinajs.cn/list=sz' + stock_code)
        stockdatasplit = stockdata.text.split(',')

        stock = models.Stock()
        stock.code = stock_code
        stock.name = stockdatasplit[0][21:]
        stock.open = stockdatasplit[1]
        stock.close = stockdatasplit[2]
        stock.high = stockdatasplit[4]
        stock.low = stockdatasplit[5]
        stock.price = stockdatasplit[3]
        try:
            stock.currentrate = round((float(stock.price) - float(stock.close)) / float(stock.close) * 100, 4)
        except:
            stock.currentrate = 0
        stock.save()

        response = requests.get('http://image.sinajs.cn/newchart/min/n/sz' + stock_code + '.gif')
        image = Image.open(BytesIO(response.content))
        image.save('static\stock0.png')

        response = requests.get('http://image.sinajs.cn/newchart/daily/n/sz' + stock_code + '.gif')
        image = Image.open(BytesIO(response.content))
        image.save('static\stock1.png')

        response = requests.get('http://image.sinajs.cn/newchart/weekly/n/sz' + stock_code + '.gif')
        image = Image.open(BytesIO(response.content))
        image.save('static\stock2.png')

        response = requests.get('http://image.sinajs.cn/newchart/monthly/n/sz' + stock_code + '.gif')
        image = Image.open(BytesIO(response.content))
        image.save('static\stock3.png')
    else:
        stock = models.Stock()
        stock.code = stock_code
        stock.name = stockdatasplit[0][21:]
        stock.open = stockdatasplit[1]
        stock.close = stockdatasplit[2]
        stock.high = stockdatasplit[4]
        stock.low = stockdatasplit[5]
        stock.price = stockdatasplit[3]
        try:
            stock.currentrate = round((float(stock.price) - float(stock.close)) / float(stock.close) * 100, 4)
        except:
            stock.currentrate = 0
        stock.save()
        response = requests.get('http://image.sinajs.cn/newchart/min/n/sh' + stock_code + '.gif')
        image = Image.open(BytesIO(response.content))
        image.save('static\stock0.png')

        response = requests.get('http://image.sinajs.cn/newchart/daily/n/sh' + stock_code + '.gif')
        image = Image.open(BytesIO(response.content))
        image.save('static\stock1.png')

        response = requests.get('http://image.sinajs.cn/newchart/weekly/n/sh' + stock_code + '.gif')
        image = Image.open(BytesIO(response.content))
        image.save('static\stock2.png')

        response = requests.get('http://image.sinajs.cn/newchart/monthly/n/sh' + stock_code + '.gif')
        image = Image.open(BytesIO(response.content))
        image.save('static\stock3.png')

    if request.method == 'POST':
        email = request.session.get("email")
        print(email)
        if email is None:
            info = '请先登录！'
            return render(request, 'error.html', {'error': info})
        elif request.POST.__contains__('shoucang'):
            favall = models.FavouriteStock.objects.all()
            for item in favall:
                if stock_code == item.code:
                    info = '请勿重复收藏！'
                    return render(request, 'error.html', {'error': info})
            fav = models.FavouriteStock()
            fav.code = stock_code
            fav.emailaddress = email
            fav.name = stockdatasplit[0][21:]
            fav.rate = round((float(stock.price) - float(stock.close)) / float(stock.close) * 100, 4)
            fav.save()
        elif request.POST.__contains__('buy'):
            if request.method == 'POST':
                if request.POST.get('number'):
                    number = request.POST.get('number')
                    number = float(number)
                    lastasset = models.Personal_asset.objects.filter(emailaddress=email).order_by('-pk')[0]
                    if number <= 0:
                        info = '请输入大于0的数字！'
                        return render(request, 'error.html', {'error': info})
                    if number*float(stockdatasplit[3]) > lastasset.money:
                        info = '您没有足够的余额！'
                        return render(request, 'error.html', {'error': info})
                    #own
                    try:
                        own = models.Own.objects.get(emailaddress=email, name=stockdatasplit[0][21:])
                    except:
                        own = models.Own()
                        own.emailaddress = email
                        own.buy = stockdatasplit[3]
                        own.code = stock_code
                        own.name = stockdatasplit[0][21:]
                        own.volume = number
                        own.save()
                    else:
                        own.buy = (float(own.volume)*float(own.buy) + number*float(stockdatasplit[3]))/(float(own.volume) + number)
                        own.volume += number
                        own.save()
                    #对历史交易的处理：hist
                    hist = models.Hist_trade()
                    hist.emailaddress = email
                    hist.price = stockdatasplit[3]
                    hist.code = stock_code
                    hist.name = stockdatasplit[0][21:]
                    hist.volume = number
                    hist.save()
                    #个人资产（按操作）
                    asset = models.Personal_asset()
                    asset.emailaddress = email
                    asset.stock = lastasset.stock + number*float(stockdatasplit[3])
                    asset.fund = lastasset.fund
                    asset.money = lastasset.money - number*float(stockdatasplit[3])
                    asset.save()
            return render(request, 'buy.html', {'item': stock})
        else:
            if request.method == 'POST':
                if request.POST.get('number'):
                    number = request.POST.get('number')
                    number = float(number)
                    lastasset = models.Personal_asset.objects.filter(emailaddress=email).order_by('-pk')[0]
                    if number <= 0:
                        info = '请输入大于0的数字！'
                        return render(request, 'error.html', {'error': info})
                    #own
                    try:
                        own = models.Own.objects.get(emailaddress=email, name=stockdatasplit[0][21:])
                    except:
                        info = '无法卖出不持有的股票！'
                        return render(request, 'error.html', {'error': info})
                    else:
                        if float(own.volume) < number:
                            info = '卖出量大于持有数量！'
                            return render(request, 'error.html', {'error': info})
                        elif float(own.volume) == number:
                            own.delete()
                        else:
                            own.volume = float(own.volume) - number
                            own.save()
                    #对历史交易的处理：hist
                    hist = models.Hist_trade()
                    hist.emailaddress = email
                    hist.price = stockdatasplit[3]
                    hist.code = stock_code
                    hist.name = stockdatasplit[0][21:]
                    hist.volume = 0 - number
                    hist.save()
                    #个人资产（按操作）
                    asset = models.Personal_asset()
                    asset.emailaddress = email
                    asset.stock = lastasset.stock - number*float(stockdatasplit[3])
                    asset.fund = lastasset.fund
                    asset.money = lastasset.money + number*float(stockdatasplit[3])
                    asset.save()
            return render(request, 'sell.html', {'item': stock})
    return render(request, 'stockdetail.html', {'stock': stock})

def showfund(request, fund_code):
    global code
    #print(code, fund_code)
    fund_code = str(fund_code)
    if code != fund_code:
        print('plot')
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
        fund.currentrate = rate[-1]
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
        plt.cla()
        plt.clf()
        plt.close('all')
        code = fund_code
    if request.method == 'POST':
        email = request.session.get("email")
        #print(email)
        if email is None:
            info = '请先登录！'
            return render(request, 'error.html', {'error': info})
        elif request.POST.__contains__('shoucang'):
            favall = models.FavouriteFund.objects.all()
            for item in favall:
                if fund_code == item.code:
                    info = '请勿重复收藏！'
                    return render(request, 'error.html', {'error': info})
            fav = models.FavouriteFund()
            fav.code = fund_code
            fav.emailaddress = email
            fav.name = name[0]
            fav.rate = rate[-1]
            fav.save()
        elif request.POST.__contains__('buy'):
            if request.method == 'POST':
                if request.POST.get('number'):
                    number = request.POST.get('number')
                    number = float(number)
                    lastasset = models.Personal_asset.objects.filter(emailaddress=email).order_by('-pk')[0]
                    if number <= 0:
                        info = '请输入大于0的数字！'
                        return render(request, 'error.html', {'error': info})
                    if number*float(price[-1]) > lastasset.money:
                        info = '您没有足够的余额！'
                        return render(request, 'error.html', {'error': info})
                    #own
                    try:
                        own = models.Own.objects.get(emailaddress=email, name=name[0])
                    except:
                        own = models.Own()
                        own.emailaddress = email
                        own.buy = price[-1]
                        own.code = fund_code
                        own.name = name[0]
                        own.volume = number
                        own.save()
                    else:
                        own.buy = (float(own.volume)*float(own.buy) + number*float(price[-1]))/(float(own.volume) + number)
                        own.volume += number
                        own.save()
                    #对历史交易的处理：hist
                    hist = models.Hist_trade()
                    hist.emailaddress = email
                    hist.price = price[-1]
                    hist.code = fund_code
                    hist.name = name[0]
                    hist.volume = number
                    hist.save()
                    #个人资产（按操作）
                    asset = models.Personal_asset()
                    asset.emailaddress = email
                    asset.stock = lastasset.stock
                    asset.fund = lastasset.fund + number*float(price[-1])
                    asset.money = lastasset.money - number*float(price[-1])
                    asset.save()
            return render(request, 'buy.html', {'item': fund})
        else:
            if request.method == 'POST':
                if request.POST.get('number'):
                    number = request.POST.get('number')
                    number = float(number)
                    lastasset = models.Personal_asset.objects.filter(emailaddress=email).order_by('-pk')[0]
                    if number <= 0:
                        info = '请输入大于0的数字！'
                        return render(request, 'error.html', {'error': info})
                    #own
                    try:
                        own = models.Own.objects.get(emailaddress=email, name=name[0])
                    except:
                        info = '无法卖出不持有的基金！'
                        return render(request, 'error.html', {'error': info})
                    else:
                        if float(own.volume) < number:
                            info = '卖出量大于持有数量！'
                            return render(request, 'error.html', {'error': info})
                        elif float(own.volume) == number:
                            own.delete()
                        else:
                            own.volume = float(own.volume) - number
                            own.save()
                    #对历史交易的处理：hist
                    hist = models.Hist_trade()
                    hist.emailaddress = email
                    hist.price = price[-1]
                    hist.code = fund_code
                    hist.name = name[0]
                    hist.volume = 0 - number
                    hist.save()
                    #个人资产（按操作）
                    asset = models.Personal_asset()
                    asset.emailaddress = email
                    asset.stock = lastasset.stock
                    asset.fund = lastasset.fund - number*float(price[-1])
                    asset.money = lastasset.money + number*float(price[-1])
                    asset.save()
            return render(request, 'sell.html', {'item': fund})
    return render(request, 'funddetail.html', {'fund': fund})

def error(request):
    return render(request, 'error.html')

def favourite(request):
    email = request.session.get("email")
    username = request.session.get("username")
    #print(username)
    #print(email)
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    try:
        favF = models.FavouriteFund.objects.filter(emailaddress=email)
        for item in favF:
            fund_code = str(item.code)
            while len(fund_code) < 6:
                fund_code = '0' + fund_code
            r = requests.get('http://fund.eastmoney.com/pingzhongdata/' + fund_code + '.js')
            pattern6 = re.compile('"equityReturn":(.*?),"unitMoney"')
            rate = re.findall(pattern6, r.text)
            item.rate = rate[-1]
            item.save()
    except:
        favF = []
    try:
        favS = models.FavouriteStock.objects.filter(emailaddress=email)
        for item in favS:
            stock_code = str(item.code)
            while len(stock_code) < 6:
                stock_code = '0' + stock_code
            stockdata = requests.get('http://hq.sinajs.cn/list=sh' + stock_code)
            stockdatasplit = stockdata.text.split(',')
            if (len(stockdata.text) == 24):
                stockdata = requests.get('http://hq.sinajs.cn/list=sz' + stock_code)
                stockdatasplit = stockdata.text.split(',')
            close = stockdatasplit[2]
            price = stockdatasplit[3]
            currentrate = round((float(price) - float(close)) / float(close) * 100, 4)
            item.rate = currentrate
            item.save()
    except:
        favS = []
    return render(request, 'favorite.html', {'favF': favF, 'favS': favS, 'username': username, 'email': email})

def showown(request):
    email = request.session.get("email")
    username = request.session.get("username")
    # print(email)
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    try:
        own = models.Own.objects.filter(emailaddress=email)
    except:
        own = []
    return render(request, 'own.html', {'own': own, 'username': username, 'email': email})

def showhist(request):
    email = request.session.get("email")
    username = request.session.get("username")
    # print(email)
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    try:
        hist = models.Hist_trade.objects.filter(emailaddress=email)
    except:
        hist = []
    return render(request, 'record.html', {'hist': hist, 'username': username, 'email': email})

def alterasset(request):
    emails = models.User.objects.values_list('emailaddress')
    for email in emails:
        email = email[0]
        asset = models.Hist_asset()
        asset.emailaddress = email
        asset.fund = 0
        asset.stock = 0
        pfund = 0
        pstock = 0
        own = models.Own.objects.filter(emailaddress=email)
        for item in own:
            if len(item.name) > 4:
                #print(item.name)
                r = requests.get('http://fund.eastmoney.com/pingzhongdata/' + item.code + '.js')
                pattern = re.compile('"y":(.*?),"equityReturn"')
                pricelist = re.findall(pattern, r.text)
                price = pricelist[-1]
                #print(price)
                asset.fund += float(price) * float(item.volume)
                pfund += float(item.buy) * float(item.volume)
            else:
                #price = 0
                stockdata = requests.get('http://hq.sinajs.cn/list=sh' + item.code)
                stockdatasplit = stockdata.text.split(',')
                if (len(stockdata.text) == 24):
                    stockdata = requests.get('http://hq.sinajs.cn/list=sz' + item.code)
                    stockdatasplit = stockdata.text.split(',')
                    price = stockdatasplit[3]
                else:
                    price = stockdatasplit[3]
                asset.stock += float(price) * float(item.volume)
                pstock += float(item.buy) * float(item.volume)
        #print(asset.fund)
        if pfund != 0:
            asset.fundprofit = (asset.fund - pfund) / pfund * 100
        else:
            asset.fundprofit = 0
        if pstock != 0:
            asset.stockprofit = (asset.stock - pstock) / pstock * 100
        else:
            asset.stockprofit = 0
        lastasset = models.Personal_asset.objects.filter(emailaddress=email).order_by('-pk')[0]
        asset.money = lastasset.money
        asset.save()
        return render(request, 'alterasset.html')

def showasset(request):
    email = request.session.get("email")
    username = request.session.get("username")
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    info = models.Personal_asset.objects.filter(emailaddress=email).order_by('-pk')[0]
    return render(request, 'asset.html', {'info': info, 'username': username, 'email': email})

def showprofit(request):
    email = request.session.get("email")
    username = request.session.get("username")
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    info = models.Hist_asset.objects.filter(emailaddress=email)
    info = serializers.serialize("json", info)
    #print(info)
    return render(request, 'profit.html', {'info': info, 'username': username, 'email': email})

def recharge(request):
    email = request.session.get("email")
    username = request.session.get("username")
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    if request.method == 'POST':
        if request.POST.get('number'):
            number = request.POST.get('number')
            number = float(number)
            lastasset = models.Personal_asset.objects.filter(emailaddress=email).order_by('-pk')[0]
            if number <= 0:
                info = '请输入大于0的数字！'
                return render(request, 'error.html', {'error': info})
            # 个人资产（按操作）
            asset = models.Personal_asset()
            asset.emailaddress = email
            asset.stock = lastasset.stock
            asset.fund = lastasset.fund
            asset.money = lastasset.money + number
            asset.save()
    return render(request, 'recharge.html', {'username': username, 'email': email})
