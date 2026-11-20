from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator

from ..domain import JobAdvertisement


class JobSource(ABC):
    source_id: str

    @abstractmethod
    def fetch(self, published_from: datetime) -> Iterator[JobAdvertisement]:
        raise NotImplementedError
