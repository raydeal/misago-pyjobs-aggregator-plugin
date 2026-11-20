from __future__ import annotations

import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import AggregatorConfig, CollectionState, ImportedJob
from .publisher import MisagoPublisher, format_job
from .sources.solid_jobs import SolidJobsSource

logger = logging.getLogger(__name__)


def collect_jobs(now=None) -> dict[str, int]:
    now = now or timezone.now()
    config = AggregatorConfig.get_solo()
    if not config.collection_enabled:
        return {"skipped": 0, "created": 0, "updated": 0, "failed": 0}
    if "solid_jobs" not in config.enabled_sources:
        return {"skipped": 0, "created": 0, "updated": 0, "failed": 0}
    if not config.target_category_id or not config.bot_user_id:
        raise ValueError("target_category_id and bot_user_id must be configured")

    state = CollectionState.get_solo()
    state.last_started_at = now
    state.save(update_fields=["last_started_at"])
    boundary = now - timedelta(days=30)
    if state.last_successful_run_at:
        boundary = max(
            boundary,
            state.last_successful_run_at - timedelta(seconds=config.overlap_seconds),
        )

    source = SolidJobsSource(config.solid_campaign, config.solid_division, config.solid_page_size)
    publisher = MisagoPublisher(config.target_category_id, config.bot_user_id)
    result = {
        "fetched": 0,
        "matched": 0,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0,
    }
    try:
        for job in source.fetch(boundary):
            result["fetched"] += 1
            if not job.matches(config.keywords):
                continue
            result["matched"] += 1
            try:
                _process_job(job, publisher, now, result)
            except Exception as exc:  # one bad offer must not stop the batch
                result["failed"] += 1
                ImportedJob.objects.update_or_create(
                    source_id=job.source_id,
                    job_id=job.job_id,
                    defaults={"last_error": str(exc), "last_seen_at": now},
                )
                logger.exception("Failed to import %s/%s", job.source_id, job.job_id)
        state.last_successful_run_at = now
        state.last_completed_at = now
        state.last_result = result
        state.save(update_fields=["last_successful_run_at", "last_completed_at", "last_result"])
        return result
    except Exception:
        state.last_completed_at = now
        state.last_result = result | {"failed": result["failed"] + 1}
        state.save(update_fields=["last_completed_at", "last_result"])
        raise


@transaction.atomic
def _process_job(job, publisher, now, result):
    digest = job.content_hash()
    record = ImportedJob.objects.select_for_update().filter(source_id=job.source_id, job_id=job.job_id).first()
    if record is None:
        thread_id = publisher.create_thread(job.title, format_job(job))
        ImportedJob.objects.create(
            source_id=job.source_id,
            job_id=job.job_id,
            content_hash=digest,
            thread_id=thread_id,
            last_seen_at=now,
            last_published_at=now,
            last_updated_at=job.updated_at,
        )
        result["created"] += 1
        return
    if record.content_hash == digest:
        record.last_seen_at = now
        record.last_error = ""
        record.save(update_fields=["last_seen_at", "last_error"])
        result["skipped"] += 1
        return
    publisher.add_post(record.thread_id, format_job(job, updated=True))
    record.content_hash = digest
    record.last_seen_at = now
    record.last_published_at = now
    record.last_updated_at = job.updated_at
    record.last_error = ""
    record.save(
        update_fields=[
            "content_hash",
            "last_seen_at",
            "last_published_at",
            "last_updated_at",
            "last_error",
        ]
    )
    result["updated"] += 1
