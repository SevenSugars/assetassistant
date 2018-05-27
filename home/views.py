from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
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
                #return render(request, 'error.html', {'error': info})
            else:
                if user.password != password:
                    info = '密码错误！'
                    print(info)
                    #return render(request, 'error.html', {'error': info})
                else:
                    request.session["email"] = email
                    print('登录成功。')
                    #return render(request, 'index.html')
        else:
            print("error")
    if request.method == 'GET':
        if request.GET:
            user = models.User()
            user.username = request.GET.get('username')
            user.password = request.GET.get('password')
            user.emailaddress = request.GET.get('email')
            request.session["email"] = user.emailaddress
            user.save()
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
    news = models.News.objects.all().order_by('-pk')
    news1 = models.News.objects.all()[0]
    news2 = models.News.objects.all()[1]
    news3 = models.News.objects.all()[2]
    news = news[3:]
    return render(request, 'news.html', {'news': news, 'news1': news1, 'news2': news2, 'news3': news3})

def shownews(request, news_id):
    news = models.News.objects.get(pk=news_id)
    return render(request, 'newsdetail.html', {'news': news})

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
    return render(request, 'recommend.html', {'recF': recF, 'recS': recS})

def tutorial(request):
    pass

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
        stock.currentrate = (float(stock.price) - float(stock.close)) / float(stock.close) * 100
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
        stock.currentrate = round((float(stock.price) - float(stock.close)) / float(stock.close) * 100, 4)
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
        else:
            if request.method == 'POST':
                if request.POST.get('number'):
                    number = request.POST.get('number')
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
                        own.buy = (float(own.volume)*float(own.buy) + float(number)*float(stockdatasplit[3]))/(float(own.volume) + float(number))
                        own.volume += float(number)
                        own.save()
            return render(request, 'buy.html', {'item': stock})
    return render(request, 'stockdetail.html', {'stock': stock})

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
    global code
    if code != fund_code:
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
        print(email)
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
            fav.rate = oneyear[0]
            fav.save()
        elif request.POST.__contains__('buy'):
            if request.method == 'POST':
                if request.POST.get('number'):
                    number = request.POST.get('number')
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
                        own.buy = (float(own.volume)*float(own.buy) + float(number)*float(price[-1]))/(float(own.volume) + float(number))
                        own.volume += float(number)
                        own.save()
                    #对历史交易的处理：own  info  hist
                    try:
                        hist = models.Hist_trade.objects.get(emailaddress=email, name=name[0])
                    except:
                        hist = models.Hist_trade()
                        hist.emailaddress = email
                        hist.price = price[-1]
                        hist.code = fund_code
                        hist.name = name[0]
                        hist.volume = number
                        hist.time = models.DateTimeField(default=datetime.now)
                        hist.save()
                    else:
                        hist.price = (own.volume*own.buy + number*price[-1])/(own.volume + number)
                        hist.volume = number
                        hist.save()
                    #info
                    try:
                        info = models.Hist_asset.objects.get(emailaddress=email, name=name[0])
                    except:
                        info = models.Hist_trade()
                        info.emailaddress = email
                        info.fund+=number*price[-1]
                        info.money-=number*price[-1]
                        info.time = models.DateTimeField(default=datetime.now)
                        info.save()
                    else:
                        info.price = (own.volume*own.buy + number*price[-1])/(own.volume + number)
                        info.volume = number
                        info.save()
            return render(request, 'buy.html', {'item': fund})
        else:
            if request.method == 'POST':
                if request.POST.get('number'):
                    number = request.POST.get('number')
                    try:
                        own = models.Own.objects.get(emailaddress=email, name=name[0])
                    except:
                        info = '卖出量大于持有数量！'
                        return render(request, 'error.html', {'error': info})
                    else:
                        if float(own.volume) < float(number):
                            info = '卖出量大于持有数量！'
                            return render(request, 'error.html', {'error': info})
                        if float(own.volume) == float(number):
                            pass
            return render(request, 'sell.html', {'item': fund})
    return render(request, 'funddetail.html', {'fund': fund})

def error(request):
    return render(request, 'error.html')

def showinfo(request):
    email = request.session.get("email")
    # print(email)
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    try:
        info = models.Hist_asset.objects.get(emailaddress=email)
    except:
        info = []
    return render(request, 'favourite.html', {'info': info})

def favourite(request):
    email = request.session.get("email")
    #print(email)
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    try:
        favF = models.FavouriteFund.objects.get(emailaddress=email)
    except:
        favF = []
    try:
        favS = models.FavouriteStock.objects.get(emailaddress=email)
    except:
        favS = []
    return render(request, 'favourite.html', {'favF': favF, 'favS': favS})

def showown(request):
    email = request.session.get("email")
    # print(email)
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    try:
        own = models.Own.objects.get(emailaddress=email)
    except:
        own = []
    return render(request, 'own.html', {'own': own})

def showhist(request):
    email = request.session.get("email")
    # print(email)
    if email is None:
        info = '请先登录！'
        return render(request, 'error.html', {'error': info})
    try:
        hist = models.Hist_trade.objects.get(emailaddress=email)
    except:
        hist = []
    return render(request, 'hist.html', {'hist': hist})