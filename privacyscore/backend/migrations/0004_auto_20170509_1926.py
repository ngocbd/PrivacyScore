# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-09 19:26
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_auto_20170509_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawscanresult',
            name='test',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='scanresult',
            name='additional_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scanresult',
            name='test',
            field=models.CharField(max_length=80),
        ),
    ]