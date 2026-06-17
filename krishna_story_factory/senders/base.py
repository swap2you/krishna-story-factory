from __future__ import annotations

from abc import ABC, abstractmethod

from ..config import Settings
from ..models import PackagePaths, SendResult


class BaseSender(ABC):
    @abstractmethod
    def send(self, *, settings: Settings, paths: PackagePaths, mode: str) -> SendResult:
        raise NotImplementedError
