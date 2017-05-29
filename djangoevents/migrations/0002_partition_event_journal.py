# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 17:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangoevents', '0001_initial'),
    ]

    operations = []

    if getattr(settings, 'PARTITION_EVENT_JOURNAL', False):
        partition_num = getattr(settings, 'EVENT_JOURNAL_PARTITION_NUMBER', 40)
        partition_sql = 'ALTER TABLE event_journal PARTITION BY KEY(aggregate_type) PARTITIONS %s;' % (partition_num, )
        operations.append(
            migrations.RunSQL(partition_sql)
        )
