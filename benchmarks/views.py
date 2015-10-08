from django.shortcuts import render
from django.http import HttpResponse
from .models import BenchmarkBuild
import json
import os
import github

TESTS_WAITING = 0
TESTS_SUCCESS = 1
TESTS_FAIL = 2
BENCHMARK_SUCCESS = 3

GITHUB_CLIENT_ID = os.environ['GITHUB_CLIENT_ID']
GITHUB_CLIENT_SECRET = os.environ['GITHUB_CLIENT_SECRET']

gh = github.Github(client_id=GITHUB_CLIENT_ID, client_secret=GITHUB_CLIENT_SECRET)

def index(request):
    return HttpResponse("Hello, world. You're at the build index. build# %s" % os.environ['GITHUB_CLIENT_ID'])

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

