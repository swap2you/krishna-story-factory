from __future__ import annotations

from abc import ABC, abstractmethod

from ..config import Settings
from ..models import PackagePaths, PlanRow, SendResult, StoryContent


class BaseSender(ABC):
    @abstractmethod
    def send(
        self,
        *,
        settings: Settings,
        paths: PackagePaths,
        mode: str,
        plan: PlanRow | None = None,
        content: StoryContent | None = None,
        package_link: str = "",
    ) -> SendResult:
        raise NotImplementedError
