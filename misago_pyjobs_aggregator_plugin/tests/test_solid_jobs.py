from datetime import datetime, timezone

from misago_pyjobs_aggregator_plugin.sources.solid_jobs import SolidJobsSource


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        page = kwargs["params"]["pageIndex"]
        if page == 0:
            return FakeResponse(
                {
                    "totalPages": 2,
                    "jobs": [
                        {
                            "jobOfferKey": "one",
                            "title": "Python developer",
                            "validFrom": "2026-01-01T00:00:00+00:00",
                            "skills": [],
                        }
                    ],
                }
            )
        return FakeResponse(
            {
                "totalPages": 2,
                "jobs": [
                    {
                        "jobOfferKey": "two",
                        "title": "Old Python job",
                        "validFrom": "2025-01-01T00:00:00+00:00",
                        "skills": [],
                    }
                ],
            }
        )


def test_fetches_pages_and_applies_publication_boundary():
    session = FakeSession()
    source = SolidJobsSource("campaign", session=session)
    jobs = list(source.fetch(datetime(2025, 12, 1, tzinfo=timezone.utc)))
    assert [job.job_id for job in jobs] == ["one"]
    assert len(session.calls) == 2
    assert session.calls[0][1]["params"]["campaign"] == "campaign"
