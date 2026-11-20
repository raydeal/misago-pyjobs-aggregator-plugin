from datetime import datetime, timezone
from typing import Any, Iterator

from ..domain import JobAdvertisement
from .base import JobSource


class SolidJobsSource(JobSource):
    source_id = "solid_jobs"
    endpoint = "https://solid.jobs/public-api/offers"

    def __init__(self, campaign: str, division: str = "IT", page_size: int = 100, session=None):
        self.campaign = campaign
        self.division = division
        self.page_size = page_size
        if session is None:
            import requests

            session = requests.Session()
        self.session = session

    def fetch(self, published_from: datetime) -> Iterator[JobAdvertisement]:
        page = 0
        while True:
            response = self.session.get(
                f"{self.endpoint}/{self.division}",
                params={
                    "campaign": self.campaign,
                    "pageIndex": page,
                    "pageSize": self.page_size,
                },
                headers={"X-Api-Version": "1.0"},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
            jobs = payload.get("jobs", [])
            for raw in jobs:
                job = self._normalize(raw)
                if job.published_at and job.published_at >= published_from:
                    yield job
            if page + 1 >= payload.get("totalPages", page + 1) or not jobs:
                break
            page += 1

    @staticmethod
    def _date(value: Any) -> datetime | None:
        if not value:
            return None
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    @classmethod
    def _normalize(cls, raw: dict[str, Any]) -> JobAdvertisement:
        skills = tuple(item.get("name", "") if isinstance(item, dict) else str(item) for item in raw.get("skills", []))
        salary = raw.get("salary") or {}
        return JobAdvertisement(
            source_id=cls.source_id,
            job_id=str(raw["jobOfferKey"]),
            title=raw.get("title", ""),
            company=raw.get("company", ""),
            description=raw.get("description", ""),
            url=raw.get("url", ""),
            locations=tuple(raw.get("locations", [])),
            salary=salary,
            contract_time=raw.get("contractTime", ""),
            is_remote=bool(raw.get("isRemote", False)),
            is_hybrid=bool(raw.get("isHybrid", False)),
            skills=skills,
            benefits=tuple(raw.get("benefits", [])),
            experience_level=raw.get("experienceLevel", ""),
            published_at=cls._date(raw.get("validFrom")),
            updated_at=cls._date(raw.get("updatedAt")),
        )
