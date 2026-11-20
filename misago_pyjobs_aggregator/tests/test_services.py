import pytest

from misago_pyjobs_aggregator import utils
from misago_pyjobs_aggregator.models import ImportedJob


@pytest.mark.django_db
def test_collect_jobs_creates_import_record(
    monkeypatch, aggregator_config, published_job
):
    class FakeSource:
        def __init__(self, *args):
            pass

        def fetch(self, boundary):
            return iter([published_job])

    class FakePublisher:
        def __init__(self, *args):
            pass

        def create_thread(self, title, content):
            return 99

    monkeypatch.setattr(utils, "SolidJobsSource", FakeSource)
    monkeypatch.setattr(utils, "MisagoPublisher", FakePublisher)

    result = utils.collect_jobs(published_job.published_at)

    assert result["fetched"] == 1
    assert result["matched"] == 1
    assert result["created"] == 1
    assert ImportedJob.objects.get().thread_id == 99


@pytest.mark.django_db
def test_collect_jobs_skips_unchanged_import(
    monkeypatch, aggregator_config, published_job
):
    class FakeSource:
        def __init__(self, *args):
            pass

        def fetch(self, boundary):
            return iter([published_job])

    class FakePublisher:
        def __init__(self, *args):
            pass

        def create_thread(self, title, content):
            raise AssertionError("an unchanged job must not create a thread")

    ImportedJob.objects.create(
        source_id=published_job.source_id,
        job_id=published_job.job_id,
        content_hash=published_job.content_hash(),
        thread_id=99,
    )
    monkeypatch.setattr(utils, "SolidJobsSource", FakeSource)
    monkeypatch.setattr(utils, "MisagoPublisher", FakePublisher)

    result = utils.collect_jobs(published_job.published_at)

    assert result["skipped"] == 1
    assert result["created"] == 0
