from django.db import models

#用户
class User(models.Model):
    username = models.CharField(max_length=30)  #用户名
    password = models.CharField(max_length=30)  #密码

#新闻
class News(models.Model):
    title = models.CharField(max_length=80, default='title')    #新闻标题
    content = models.TextField(null=True)   #新闻内容

    def __str__(self):
        return self.title

#推荐
class Recommend(models.Model):
    code = models.IntegerField      #推荐基金、股票、代码
    name = models.CharField(max_length=30)      #名字
    annualrate = models.FloatField      #年涨跌幅

#股票
class stock(models.Model):
    code = models.IntegerField      #代码
    name = models.CharField(max_length=30)      #名字
    price = models.FloatField      #当前价格
    open = models.FloatField       #今日开盘价
    close = models.FloatField      #今日收盘价
    high = models.FloatField       #今日最高价
    low = models.FloatField        #今日最低价
    currentrate = models.FloatField     #当前涨跌幅

#基金
class fund(models.Model):
    code = models.IntegerField      #代码
    name = models.CharField(max_length=30)      #名字
    price = models.FloatField      #当前价格
    currentrate = models.FloatField     #当前涨跌幅
    onemrate = models.FloatField      #近1月收益率
    threemrate = models.FloatField    #近3月收益率
    sixmrate = models.FloatField      #近6月收益率
    annualrate = models.FloatField  #年收益率

#收藏
class favourite(models.Model):
    username = models.CharField(max_length=30)  #用户名
    code = models.IntegerField      #代码
    name = models.CharField(max_length=30)      #名字

#当前持有
class own(models.Model):
    username = models.CharField(max_length=30)  #用户名
    code = models.IntegerField      #代码
    name = models.CharField(max_length=30)      #名字
    volumn = models.FloatField      #持有量
    buy = models.FloatField         #买入价

#历史交易
class hist_trade(models.Model):
    username = models.CharField(max_length=30)  #用户名
    code = models.IntegerField      #代码
    name = models.CharField(max_length=30)      #名字
    volumn = models.FloatField      #交易量
    price = models.FloatField       #交易价格
    time = models.TimeField         #交易时间

#按操作结算资产
class prosenal_asset(models.Model):
    username = models.CharField(max_length=30)  #用户名
    stock = models.FloatField       #股票资产
    stockprofit = models.FloatField #股票收益
    fund = models.FloatField        #基金资产
    fundprofit = models.FloatField  #基金收益
    money = models.FloatField       #现金资产
    time = models.TimeField         #交易时间

#按日结算资产
class hist_asset(models.Model):
    username = models.CharField(max_length=30)  #用户名
    stock = models.FloatField       #股票资产
    fund = models.FloatField        #基金资产
    money = models.FloatField       #现金资产
    time = models.TimeField         #交易时间

