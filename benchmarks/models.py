from django.db import models
from django.core.urlresolvers import reverse

class BenchmarkBuild(models.Model):
    results = models.CharField(max_length=2048)

    pr_status = models.CharField(max_length=100) # open, closed
    pr_number = models.IntegerField()
    pr_title = models.CharField(max_length=100)
    pr_body = models.CharField(max_length=100)

    pr_branch = models.CharField(max_length=100)
    pr_repo = models.CharField(max_length=100)
    pr_sha = models.CharField(max_length=100)

    # author_name = models.CharField(max_length=100)
    author_login = models.CharField(max_length=100)
    author_id = models.CharField(max_length=100)

    ci_status = models.CharField(max_length=100)
    ci_context = models.CharField(max_length=100)
    ci_build_uri = models.CharField(max_length=100)

    base_branch = models.CharField(max_length=100)
    base_repo = models.CharField(max_length=100)
    base_sha = models.CharField(max_length=100)

    # owner_name = models.CharField(max_length=100)
    owner_login = models.CharField(max_length=100)
    owner_id = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Build {0} <{1}>'.format(self.id, self.sha)

    def url(self):
        return reverse('details', args=[str(self.id)])

    def pretty_status(self):
        if self.ci_status is 'pending':
            return ('pending', 'Waiting for %s to complete.' % self.ci_context)

        if self.ci_status is 'success':
            if results:
                return ('success', 'Benchmark has completed.')
            else:
                return ('pending', 'Tests completed. Waiting for benchmarks')

        if self.ci_status is 'failure':
            return ('failure', 'Tests failed,')

        if self.ci_status is 'error':
            return ('error', 'Error running tests on %s.' % self.ci_context)

class GithubToken(models.Model):
    owner = models.CharField(max_length=100)
    access_token = models.CharField(max_length=250)
    scope = models.CharField(max_length=100)
