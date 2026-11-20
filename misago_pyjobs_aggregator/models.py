from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def default_keywords():
    return ["Python"]


def default_sources():
    return ["solid_jobs"]


class AggregatorConfig(models.Model):
    """Singleton operational configuration for the importer."""

    keywords = models.JSONField(default=default_keywords)
    enabled_sources = models.JSONField(default=default_sources)
    target_category_id = models.PositiveIntegerField(null=True, blank=True)
    bot_user_id = models.PositiveIntegerField(null=True, blank=True)
    solid_campaign = models.CharField(max_length=64, default="python-forum-pl")
    solid_division = models.CharField(max_length=32, default="IT")
    solid_page_size = models.PositiveIntegerField(
        default=100, validators=[MinValueValidator(1), MaxValueValidator(500)]
    )
    collection_enabled = models.BooleanField(default=True)
    overlap_seconds = models.PositiveIntegerField(default=60)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Jobs aggregator configuration"
        verbose_name_plural = "Jobs aggregator configuration"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        return cls.objects.get_or_create(pk=1)[0]


class ImportedJob(models.Model):
    source_id = models.CharField(max_length=64)
    job_id = models.CharField(max_length=255)
    content_hash = models.CharField(max_length=64)
    thread_id = models.PositiveIntegerField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_published_at = models.DateTimeField(null=True, blank=True)
    last_updated_at = models.DateTimeField(null=True, blank=True)
    first_imported_at = models.DateTimeField(auto_now_add=True)
    last_error = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source_id", "job_id"], name="unique_imported_source_job"
            )
        ]
        indexes = [models.Index(fields=["source_id", "job_id"])]


class CollectionState(models.Model):
    singleton = models.BooleanField(default=True, unique=True)
    last_successful_run_at = models.DateTimeField(null=True, blank=True)
    last_started_at = models.DateTimeField(null=True, blank=True)
    last_completed_at = models.DateTimeField(null=True, blank=True)
    last_result = models.JSONField(default=dict)

    @classmethod
    def get_solo(cls):
        return cls.objects.get_or_create(singleton=True)[0]
