from abc import ABC, abstractmethod
from typing import List

from src.domain.entities import Ad


class AdRepository(ABC):
    @abstractmethod
    async def create(
        self,
        user_id: int,
        title: str,
        description: str,
        price: int,
        category: str,
        city: str,
    ) -> Ad: ...

    @abstractmethod
    async def get_by_id(
        self,
        ad_id: int,
    ) -> Ad | None: ...

    @abstractmethod
    async def list(
        self,
        user_id: int | None,
        limit: int,
        offset: int,
    ) -> tuple[List[Ad], int]: ...

    @abstractmethod
    async def save(
        self,
        ad: Ad,
    ) -> None: ...
