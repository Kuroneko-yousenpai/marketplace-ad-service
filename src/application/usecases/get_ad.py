from src.application.exceptions import AdNotFoundError
from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import AdView, GetAdPort
from src.application.ports.user_profile import UserProfileService
from src.domain.entities import AdStatus


class GetAd(GetAdPort):
    def __init__(self, uow: UnitOfWork, user_profile: UserProfileService) -> None:
        self._uow = uow
        self._user_profile = user_profile

    async def execute(self, ad_id: int) -> AdView:
        async with self._uow:
            ad = await self._uow.ads.get_by_id(ad_id)
            if ad is None or ad.status == AdStatus.ARCHIVED:
                raise AdNotFoundError
        user = await self._user_profile.user(ad.user_id)
        return AdView(ad=ad, user_name=user.name if user else None)
