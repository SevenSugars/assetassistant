# Generated by Django 2.0.5 on 2018-05-21 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favourite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Fund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
                ('price', models.FloatField()),
                ('currentrate', models.FloatField()),
                ('onemrate', models.FloatField()),
                ('threemrate', models.FloatField()),
                ('sixmrate', models.FloatField()),
                ('annualrate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Hist_asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('stock', models.FloatField()),
                ('fund', models.FloatField()),
                ('money', models.FloatField()),
                ('time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Hist_trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
                ('volume', models.FloatField()),
                ('price', models.FloatField()),
                ('time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='title', max_length=80)),
                ('content', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Own',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
                ('volume', models.FloatField()),
                ('buy', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Prosenal_asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('stock', models.FloatField()),
                ('stockprofit', models.FloatField()),
                ('fund', models.FloatField()),
                ('fundprofit', models.FloatField()),
                ('money', models.FloatField()),
                ('time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='RecommendFund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
                ('annualrate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='RecommendStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
                ('annualrate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=30)),
                ('price', models.FloatField()),
                ('open', models.FloatField()),
                ('close', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('currentrate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=30)),
                ('emailaddress', models.EmailField(max_length=254)),
            ],
        ),
    ]
