from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Evidence:
    source_name: str
    source_url: str | None
    summary: str
    confidence: str


class SourceAdapter(ABC):
    name: str

    @abstractmethod
    async def search(self, keyword: str, category: str | None = None) -> dict:
        raise NotImplementedError
