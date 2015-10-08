from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from .models import BenchmarkBuild
from oauthlib.oauth2 import WebApplicationClient
import json
import os
import requests
import github

TESTS_WAITING = 0
TESTS_SUCCESS = 1
TESTS_FAIL = 2
BENCHMARK_SUCCESS = 3

REQUEST_TOKEN_URL = 'https://github.com/login/oauth/access_token'
AUTHORIZATION_URL = 'https://github.com/login/oauth/authorize'


gh = github.Github(client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_CLIENT_SECRET)

def index(request):
    client = WebApplicationClient(settings.GITHUB_CLIENT_ID)

    if not request.GET.has_key('code'):
        uri = client.prepare_request_uri(AUTHORIZATION_URL, redirect_uri=request.build_absolute_uri(reverse('index')),
                                   scope=['repo:status'])
        context = {'uri': uri}
    else:
        code = request.GET['code']
        body = client.prepare_request_body(code=code)
        response = requests.post(REQUEST_TOKEN_URL, body)
        context = {'response': response}
    return render(request, 'benchmarks/index.html', context)

def get_status_msg(build):
    return "foo"


def update_build_status(build):
    user, repo = build.repo.split('/')
    commit = gh.get_user(user).get_repo(repo).get_commit(build.sha)
    status_msg = get_status_msg("foo")
    commit.create_status(status_msg)


def handle_status(payload):
    try:
        build = BenchmarkBuild.objects.get(sha=payload['sha'], repo=payload['name'])
    except DoesNotExist:
        return HttpResponse("Benchmark build does not exist")

    if payload['state'] == 'failure' or payload['state'] == 'error':
        build.status = TESTS_FAIL
    elif payload['status'] == 'pending':
        build.status = TESTS_WAITING
    elif payload['status'] == 'success':
        build.status = TESTS_SUCCESS

    build.save()
    update_build_status(build)

def handle_pull_request(payload):
    action = payload['action']

    if action == 'opened' or action == 'synchronize':
        sha = payload['pull_request']['head']['sha']
        repo = payload['pull_request']['repo']['full_name']
        build = BenchmarkBuild(sha=sha, repo=repo, status=TESTS_WAITING)
        build.save()

def github_hook(request):
    """
        POST Hook when PR is updated
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request')

    event = request.meta['X-GitHub-Event']
    payload = json.loads(request.body)

    if event is 'pull_request':
        handle_pull_request(payload)
    elif event is 'status':
        handle_status(payload)

    # if event is status:
    return HttpResponse("Github hook")


def benchmark_hook(request):
    """
        POST Hook with benchmark results
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request')

    payload = json.loads(request.body)

    sha = payload['sha']
    repo = payload['repo']
    results = payload['results']

    try:
        build = BenchmarkBuild.objects.get(sha=sha, repo=repo)
    except DoesNotExist:
        return HttpResponse("Benchmark build does not exist")

    build.status = BENCHMARK_SUCCESS
    build.results = results

    build.save()

    update_build_status(build)
    return HttpResponse("Benchmark hook")

