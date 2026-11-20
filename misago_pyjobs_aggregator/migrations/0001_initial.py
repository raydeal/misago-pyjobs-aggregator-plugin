import django.core.validators
from django.db import migrations, models


def default_keywords():
    return ["Python"]


def default_sources():
    return ["solid_jobs"]


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="AggregatorConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("keywords", models.JSONField(default=default_keywords)),
                ("enabled_sources", models.JSONField(default=default_sources)),
                (
                    "target_category_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("bot_user_id", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "solid_campaign",
                    models.CharField(default="python-forum-pl", max_length=64),
                ),
                ("solid_division", models.CharField(default="IT", max_length=32)),
                (
                    "solid_page_size",
                    models.PositiveIntegerField(
                        default=100,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(500),
                        ],
                    ),
                ),
                ("collection_enabled", models.BooleanField(default=True)),
                ("overlap_seconds", models.PositiveIntegerField(default=60)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="ImportedJob",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("source_id", models.CharField(max_length=64)),
                ("job_id", models.CharField(max_length=255)),
                ("content_hash", models.CharField(max_length=64)),
                ("thread_id", models.PositiveIntegerField(blank=True, null=True)),
                ("last_seen_at", models.DateTimeField(blank=True, null=True)),
                ("last_published_at", models.DateTimeField(blank=True, null=True)),
                ("last_updated_at", models.DateTimeField(blank=True, null=True)),
                ("first_imported_at", models.DateTimeField(auto_now_add=True)),
                ("last_error", models.TextField(blank=True)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("source_id", "job_id"),
                        name="unique_imported_source_job",
                    )
                ],
                "indexes": [
                    models.Index(
                        fields=["source_id", "job_id"],
                        name="misago_pyjo_source__e1b5d3_idx",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="CollectionState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("singleton", models.BooleanField(default=True, unique=True)),
                ("last_successful_run_at", models.DateTimeField(blank=True, null=True)),
                ("last_started_at", models.DateTimeField(blank=True, null=True)),
                ("last_completed_at", models.DateTimeField(blank=True, null=True)),
                ("last_result", models.JSONField(default=dict)),
            ],
        ),
    ]
