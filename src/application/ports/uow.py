from abc import ABC, abstractmethod
from types import TracebackType

from src.application.ports.outbox import OutboxRepository
from src.application.ports.repositories import AdRepository


class UnitOfWork(ABC):
    ads: AdRepository
    outbox: OutboxRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork": ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
