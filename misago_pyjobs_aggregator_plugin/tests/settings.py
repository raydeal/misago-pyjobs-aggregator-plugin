"""Minimal Django project used to test the reusable application."""

SECRET_KEY = "pytest-only-secret-key"
DEBUG = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "misago_pyjobs_aggregator_plugin.apps.JobsAggregatorConfig",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = []
ROOT_URLCONF = "misago_pyjobs_aggregator_plugin.tests.urls"
