import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


@dataclass(frozen=True)
class JobAdvertisement:
    source_id: str
    job_id: str
    title: str
    company: str = ""
    description: str = ""
    url: str = ""
    locations: tuple[str, ...] = field(default_factory=tuple)
    salary: dict[str, Any] = field(default_factory=dict)
    contract_time: str = ""
    is_remote: bool = False
    is_hybrid: bool = False
    skills: tuple[str, ...] = field(default_factory=tuple)
    benefits: tuple[str, ...] = field(default_factory=tuple)
    experience_level: str = ""
    published_at: datetime | None = None
    updated_at: datetime | None = None

    def searchable_text(self) -> str:
        return " ".join([self.title, self.description, *self.skills]).casefold()

    def matches(self, keywords: list[str]) -> bool:
        haystack = self.searchable_text()
        return any(clean(keyword).casefold() in haystack for keyword in keywords if clean(keyword))

    def hash_payload(self) -> dict[str, Any]:
        return {
            "title": clean(self.title),
            "company": clean(self.company),
            "description": clean(self.description),
            "url": clean(self.url),
            "locations": sorted(clean(item) for item in self.locations),
            "salary": self.salary,
            "contract_time": clean(self.contract_time),
            "is_remote": self.is_remote,
            "is_hybrid": self.is_hybrid,
            "skills": sorted(clean(item) for item in self.skills),
            "benefits": sorted(clean(item) for item in self.benefits),
            "experience_level": clean(self.experience_level),
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }

    def content_hash(self) -> str:
        encoded = json.dumps(self.hash_payload(), sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
