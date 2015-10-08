from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # status - Waiting for tests to complete
    url(r'^hooks/github$', views.github_hook, name='github_hook'),

    # status - Tests failed
    # url(r'^hooks/ci_build$', views.ci_build_hook, name='ci_build_hook'),

    # status - Tests completed, running benchmarks
    # url(r'^hooks/benchmark_start$', views.ci_build_end, name='ci_build_end'),

    # status - Bencmark done + Results
    url(r'^hooks/benchmark$', views.benchmark_hook, name='benchmark_hook'),
]
