# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-02-20 12:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carceropolis', '0003_remove_especialista_telefone'),
    ]

    operations = [
        migrations.AddField(
            model_name='especialista',
            name='ddd',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'DDD'),
        ),
        migrations.AddField(
            model_name='especialista',
            name='ddi',
            field=models.IntegerField(blank=True, default=55, null=True, verbose_name=b'DDI'),
        ),
        migrations.AddField(
            model_name='especialista',
            name='telefone',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'Telefone'),
        ),
    ]
