# Generated by Django 2.1.5 on 2019-03-11 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0003_auto_20190311_0120'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='display_name',
            field=models.TextField(default='User'),
        ),
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.TextField(default='password'),
        ),
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.TextField(default='Username'),
        ),
    ]
