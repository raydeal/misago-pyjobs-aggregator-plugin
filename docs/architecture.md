# Python Jobs Aggregator plugin

This is a Django application packaged as a Misago plugin. Misago discovers a
plugin package containing `__init__.py` and `misago_plugin.py`; plugin-specific
dependencies are declared in this repository's `pyproject.toml`.

## Version 1

The first source is SOLID.Jobs. The adapter uses its public paginated offers
endpoint, with a configured campaign and division. Pracuj.pl and No Fluff Jobs
are future adapters and are deliberately not implemented yet.

The default keyword is `Python`. Keywords are configurable in Django admin and
are matched case-insensitively using OR semantics against the title,
description, and skills.

## Import flow

`collect_jobs` is intended to run from cron:

```cron
*/15 * * * * /path/to/manage.py collect_jobs >> /var/log/misago-jobs.log 2>&1
```

The first run fetches offers published in the previous 30 days. Subsequent
runs use `max(now - 30 days, last_successful_run_at - overlap)` as the
publication boundary. The overlap handles timestamp precision and retries;
source/job identity and content hashing keep the run idempotent.

Each job is identified by `(source_id, job_id)`. The Solid Jobs
`jobOfferKey` is the job ID. A canonical SHA-256 hash is generated from the
normalized title, company, description, URL, locations, salary, contract,
work mode, skills, benefits, experience, and publication date. Volatile import
timestamps are excluded.

An unseen job creates one thread in the configured category, authored by the
configured bot user. A seen job with the same hash is skipped. A seen job with
a different hash creates a new update post in the existing thread and stores
the new hash.

The successful-run watermark is advanced only after all fetched offers have
been processed. Individual offer failures are logged and do not stop other
offers. A source-level failure leaves the previous successful watermark in
place so the next run retries the window.

## Configuration

Configure the singleton `Jobs aggregator configuration` record in admin:

- keywords
- target Misago category ID
- bot user ID
- Solid Jobs campaign
- Solid Jobs division and page size
- collection enabled flag
- overlap seconds

Run migrations after installing the plugin:

```bash
python manage.py migrate misago_pyjobs_aggregator_plugin
python manage.py collect_jobs
```

## Future sources

New API, SDK, or scraper integrations should implement `JobSource.fetch()` and
return `JobAdvertisement` values. They must provide a stable source ID and
external job ID. Scrapers must respect each site's terms, robots guidance,
rate limits, and HTML changes; provider-specific parsing must remain outside
the normalized domain and publishing code.
