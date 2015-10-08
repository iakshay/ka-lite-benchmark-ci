from django.db import models

class BenchmarkBuild(models.Model):
    TESTS_WAITING = 0
    TESTS_SUCCESS = 1
    TESTS_FAIL = 2
    BENCHMARK_SUCCESS = 3

    BUILD_STATES = (
        (TESTS_WAITING, 'Waiting for tests to completes'),
        (TESTS_SUCCESS, 'Tests completed, running benchmarks'),
        (TESTS_FAIL, 'Tests failed'),
        (BENCHMARK_SUCCESS, 'Benchmark complete'),
    )
    ci_build_url = models.URLField()
    sha = models.CharField(max_length=50)
    repo = models.CharField(max_length=100)
    status = models.IntegerField(choices=BUILD_STATES)
    results = models.CharField(max_length=2048)

    # to add
    # base_repo
    # pull request number
    # pull request title
    # commit message
    # branch name
    # author name
    # branch
    # last updated
    # compare - base commit
    # ci_context
    # ci_build_uri
    def __str__(self):
        return 'Build {0} <{1}>'.format(self.id, self.sha)

    def url(self):
        return 'http://example.com'

    def pretty_status(self):
        return "sample status"

    def github_status(self):
        return "pending"

class GithubToken(models.Model):
    owner = models.CharField(max_length=100)
    repo = models.CharField(max_length=100)
    scope = models.CharField(max_length=100)
