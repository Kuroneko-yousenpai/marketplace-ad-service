from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class UserInfo:
    id: int
    name: str


class UserProfileService(ABC):
    @abstractmethod
    async def user(
        self,
        user_id: int,
    ) -> UserInfo | None: ...
