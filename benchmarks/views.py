from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from .models import BenchmarkBuild, GithubToken
from oauthlib.oauth2 import WebApplicationClient
from oauthlib.common import extract_params
from github import Github
import json
import os
import requests

TESTS_WAITING = 0
TESTS_SUCCESS = 1
TESTS_FAIL = 2
BENCHMARK_SUCCESS = 3

REQUEST_TOKEN_URL = 'https://github.com/login/oauth/access_token'
AUTHORIZATION_URL = 'https://github.com/login/oauth/authorize'


def index(request):
    client = WebApplicationClient(settings.GITHUB_CLIENT_ID)

    if not request.GET.has_key('code'):
        uri = client.prepare_request_uri(AUTHORIZATION_URL, redirect_uri=request.build_absolute_uri(reverse('index')),
                                   scope=['repo'])
        context = {'uri': uri}
    else:
        code = request.GET['code']
        body = client.prepare_request_body(code=code)
        response = requests.post(REQUEST_TOKEN_URL, body)
        params = extract_params(response.text)
        access_token = params[0][1]
        scope = params[1][1]
        owner = Github(access_token).get_user()
        token = GithubToken(owner=owner.login, access_token=access_token)
        token.save()
        context = {'owner': owner.name}
    return render(request, 'benchmarks/index.html', context)

def update_build_status(build):
    owner, repo = build.repo.split('/')
    try:
        token_user = GithubToken.objects.get(owner=owner)
    except DoesNotExist:
        return HttpResponse("No permissions for owner - {}", owner)

    commit = Github(token_user.access_token).get_user().get_repo(repo).get_commit(build.sha)
    commit.create_status(build.github_status(), description=build.pretty_status(), target_url=build.url(),
                         context=settings.GITHUB_CI_CONTEXT)


def handle_status(payload):
    # todo - check if this is circleci or travis
    # ci/circleci
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

    update_build_status(build)

def github_hook(request):
    """
        POST Hook when PR (open, synchronize) or its status is updated
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
        POST Hook for benchmark results
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

