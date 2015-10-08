from django.contrib import admin

from .models import BenchmarkBuild, GithubToken

admin.site.register(BenchmarkBuild)
admin.site.register(GithubToken)
