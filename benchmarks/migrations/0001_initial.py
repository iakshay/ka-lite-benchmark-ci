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
                ('results', models.CharField(max_length=2048)),
                ('pr_status', models.CharField(max_length=100)),
                ('pr_number', models.IntegerField()),
                ('pr_title', models.CharField(max_length=100)),
                ('pr_body', models.CharField(max_length=100)),
                ('pr_branch', models.CharField(max_length=100)),
                ('pr_repo', models.CharField(max_length=100)),
                ('pr_sha', models.CharField(max_length=100)),
                ('author_login', models.CharField(max_length=100)),
                ('author_id', models.CharField(max_length=100)),
                ('ci_status', models.CharField(max_length=100)),
                ('ci_context', models.CharField(max_length=100)),
                ('ci_build_uri', models.CharField(max_length=100)),
                ('base_branch', models.CharField(max_length=100)),
                ('base_repo', models.CharField(max_length=100)),
                ('base_sha', models.CharField(max_length=100)),
                ('owner_login', models.CharField(max_length=100)),
                ('owner_id', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='GithubToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner', models.CharField(max_length=100)),
                ('repo', models.CharField(max_length=100)),
                ('scope', models.CharField(max_length=100)),
            ],
        ),
    ]
