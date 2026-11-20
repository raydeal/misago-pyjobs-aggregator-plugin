from datetime import datetime, timezone

import pytest

from misago_pyjobs_aggregator_plugin.domain import JobAdvertisement
from misago_pyjobs_aggregator_plugin.models import AggregatorConfig


@pytest.fixture
def aggregator_config(db):
    return AggregatorConfig.objects.create(
        target_category_id=10,
        bot_user_id=20,
    )


@pytest.fixture
def job():
    return JobAdvertisement(
        source_id="solid_jobs",
        job_id="offer-1",
        title="Python Developer",
        description="Build Python services",
        skills=("Python", "Django"),
        locations=("Warsaw",),
        published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def published_job():
    return JobAdvertisement(
        source_id="solid_jobs",
        job_id="offer-1",
        title="Python Developer",
        description="Build Python services",
        published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
