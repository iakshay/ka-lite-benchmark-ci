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

REQUEST_TOKEN_URL = 'https://github.com/login/oauth/access_token'
AUTHORIZATION_URL = 'https://github.com/login/oauth/authorize'


def index(request):
    client = WebApplicationClient(settings.GITHUB_CLIENT_ID)

    if not request.GET.has_key('code'):
        # todo - also setup hook for repo
        # todo - check http referrer = 'https://github.com/'
        uri = client.prepare_request_uri(AUTHORIZATION_URL, redirect_uri=request.build_absolute_uri(reverse('index')),
                                   scope=['repo'])
        context = {'uri': uri}
    else:
        code = request.GET['code']
        body = client.prepare_request_body(code=code, client_secret=settings.GITHUB_CLIENT_SECRET)
        headers = {'Accept': 'application/json'}
        response = requests.post(REQUEST_TOKEN_URL, body, headers=headers)
        response = response.json()
        owner = Github(response['access_token']).get_user()
        # todo - check if user already exists => show repo settings
        token = GithubToken(owner=owner.login, access_token=response['access_token'], scope=response['scope'])
        token.save()
        context = {'owner': owner.name}
    return render(request, 'benchmarks/index.html', context)

def update_build_status(build):
    try:
        token_user = GithubToken.objects.get(owner=build.owner_login)
    except DoesNotExist:
        return HttpResponse("No permissions for owner - {}", build.owner_login)

    commit = Github(token_user.access_token).get_user().get_repo(build.pr_repo).get_commit(build.pr_sha)
    status, status_msg = build.pretty_status()
    commit.create_status(status, description=status_msg, target_url=build.url(),
                         context=settings.GITHUB_CI_CONTEXT)


def handle_status(payload):
    # todo - check if this is circleci or travis
    # ci/circleci
    kwargs = {}
    kwargs['base_repo'] = payload['repository']['name']
    kwargs['owner_login'] = payload['repository']['owner']['login']
    kwargs['pr_sha'] = payload['commit']['sha']

    try:
        build = BenchmarkBuild.objects.get(**kwargs)
    except DoesNotExist:
        return HttpResponse("Benchmark build does not exist")

    if not build.ci_context:
        build.ci_context = payload['context']

    if not build.ci_context:
        build.ci_build_uri = payload['target_url']

    build.ci_status = payload['state']

    build.save()
    update_build_status(build)


def handle_pull_request(payload):
    action = payload['action']

    # create new build object
    if action == 'opened' or action == 'synchronize':
        kwargs = {}
        kwargs['pr_number'] = payload['pull_request']['number']
        kwargs['pr_status'] = payload['pull_request']['state']
        kwargs['pr_title'] = payload['pull_request']['title']
        kwargs['pr_body'] = payload['pull_request']['body']

        kwargs['pr_branch'] = payload['pull_request']['head']['ref']
        kwargs['pr_repo'] = payload['pull_request']['head']['repo']['name']
        kwargs['pr_sha'] = payload['pull_request']['head']['sha']

        kwargs['author_id'] = payload['pull_request']['head']['user']['id']
        kwargs['author_login'] = payload['pull_request']['head']['user']['login']

        kwargs['owner_id'] = payload['repository']['owner']['id']
        kwargs['owner_login'] = payload['repository']['owner']['login']

        kwargs['base_repo'] = payload['pull_request']['base']['repo']['name']
        kwargs['base_branch'] = payload['pull_request']['base']['ref']
        kwargs['base_sha'] = payload['pull_request']['base']['sha']

        build = BenchmarkBuild(**kwargs)
        build.save()
        update_build_status(build)
    elif action == 'close':
        # todo - update pr_status of all builds
        pass



def github_hook(request):
    """
        POST Hook when PR (open, synchronize) or its status is updated
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request')

    event = request.META.get('HTTP_X_GITHUB_EVENT')
    payload = json.loads(request.body)

    if event == 'pull_request':
        handle_pull_request(payload)
    elif event == 'status':
        handle_status(payload)

    return HttpResponse("Github hook")


def benchmark_hook(request):
    """
        POST Hook for benchmark results
    """
    if request.method != 'POST':
        return HttpResponse('Invalid request')

    payload = json.loads(request.body)

    kwargs = {}
    kwargs['pr_sha'] = payload['sha']
    kwargs['author_login'], kwargs['pr_repo'] = payload['repo'].split(':')

    try:
        build = BenchmarkBuild.objects.get(**kwargs)
    except DoesNotExist:
        return HttpResponse("Benchmark build does not exist")

    build.results = payload['results']

    build.save()

    update_build_status(build)
    return HttpResponse("Benchmark hook")

def details(request, build_id):
    try:
        build = BenchmarkBuild.objects.get(id=build_id)
    except DoesNotExist:
        return HttpResponse("Benchmark build does not exist")
    context = {'build': build}
    return render(request, 'benchmarks/details.html', context)

