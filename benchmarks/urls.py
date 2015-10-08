from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # status - Waiting for tests to complete
    url(r'^hooks/github$', views.github_hook, name='github_hook'),

    # status - Bencmark done + Results
    url(r'^hooks/benchmark$', views.benchmark_hook, name='benchmark_hook'),
]
