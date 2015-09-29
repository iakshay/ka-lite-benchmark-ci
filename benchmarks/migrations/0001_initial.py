# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BenchmarkBuild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ci_build_url', models.URLField()),
                ('sha', models.CharField(max_length=50)),
                ('repo', models.CharField(max_length=100)),
                ('status', models.IntegerField(choices=[(0, b'Waiting for tests to completes'), (1, b'Tests completed, running benchmarks'), (2, b'Tests failed'), (3, b'Benchmark complete')])),
                ('results', models.CharField(max_length=2048)),
            ],
        ),
    ]
