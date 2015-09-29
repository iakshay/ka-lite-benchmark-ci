from django.shortcuts import render
from django.http import HttpResponse
from .models import BenchmarkBuild
import json

TESTS_WAITING = 0
TESTS_SUCCESS = 1
TESTS_FAIL = 2
BENCHMARK_SUCCESS = 3

def index(request, build_num):
    return HttpResponse("Hello, world. You're at the build index. build# %d" % int(build_num))


def github_hook(request):
    """
        POST Hook when PR is updated
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request')

    data = json.loads(request.body)
    sha = data['pull_request']['head']['sha']
    repo = data['pull_request']['head']['label']
    build = BenchmarkBuild(sha=sha, repo=repo, status=TESTS_WAITING)
    build.save()
    return HttpResponse("Github hook")


def ci_build_hook(request):
    """
        POST Hook for CI server
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request')

    data = json.loads(request.body)
    repo = data['username'] + ':' + data['reponame']
    sha = data['vcs_revision']
    status = data['status']
    ci_build_url = data['build_url']

    try:
        build = BenchmarkBuild.objects.get(sha=sha, repo=repo)
    except DoesNotExist:
        return HttpResponse("Benchmark build does not exist")

    if status is 'success':
        build.status = TESTS_SUCCESS
    else:
        build.status = TESTS_FAIL

    build.save()
    return HttpResponse("CI Build hook")


def benchmark_hook(request):
    """
        POST Hook with benchmark results
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request')

    data = json.loads(request.body)

    sha = data['sha']
    repo = data['repo']
    results = data['results']

    try:
        build = BenchmarkBuild.objects.get(sha=sha, repo=repo)
    except DoesNotExist:
        return HttpResponse("Benchmark build does not exist")

    build.status = BENCHMARK_SUCCESS
    build.results = results

    build.save()
    return HttpResponse("Benchmark hook")

