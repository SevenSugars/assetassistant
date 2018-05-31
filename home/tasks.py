from celery import Celery
from . import models
import requests
import re

broker = 'redis://127.0.0.1:6379/0'

app = Celery('tasks')
app.conf.update(
    CELERY_RESULT_BACKEND='redis://127.0.0.1:6379/1'
)

@app.task()
def alterasset():
    emails = models.User.objects.values_lists('emailaddress')
    for email in emails:
        asset = models.Hist_asset()
        asset.emailaddress = email
        asset.fund = 0
        asset.stock = 0
        pfund = 0
        pstock = 0
        own = models.Own.objects.filter(emailaddress='email')
        for item in own:
            if len(item.name) > 4:
                r = requests.get('http://fund.eastmoney.com/pingzhongdata/' + item.code + '.js')
                pattern = re.compile('"y":(.*?),"equityReturn"')
                pricelist = re.findall(pattern, r.text)
                price = pricelist[-1]
                asset.fund += float(price) * float(item.volume)
                pfund += float(item.buy) * float(item.volume)
            else:
                price = 0
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
        asset.fundprofit = (asset.fund - pfund) / pfund * 100
        asset.stockprofit = (asset.stock - pstock) / pstock * 100