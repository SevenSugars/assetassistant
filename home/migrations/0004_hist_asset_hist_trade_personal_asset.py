# Generated by Django 2.0.5 on 2018-05-29 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_favouritefund'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hist_asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emailaddress', models.EmailField(max_length=254)),
                ('stock', models.FloatField()),
                ('stockprofit', models.FloatField()),
                ('fund', models.FloatField()),
                ('fundprofit', models.FloatField()),
                ('money', models.FloatField()),
                ('time', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hist_trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emailaddress', models.EmailField(max_length=254)),
                ('code', models.CharField(max_length=6)),
                ('name', models.CharField(max_length=30)),
                ('volume', models.FloatField()),
                ('price', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Personal_asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emailaddress', models.EmailField(max_length=254)),
                ('stock', models.FloatField()),
                ('fund', models.FloatField()),
                ('money', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]