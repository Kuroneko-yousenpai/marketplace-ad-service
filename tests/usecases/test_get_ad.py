import pytest

from src.application.exceptions import AdNotFoundError
from src.application.usecases.create_ad import CreateAd
from src.application.usecases.get_ad import GetAd
from tests.conftest import FakeUnitOfWork, FakeUserProfileService


@pytest.mark.asyncio
async def test_get_ad_returns_active(
    fake_uow: FakeUnitOfWork,
    fake_user_profile: FakeUserProfileService,
) -> None:
    create = CreateAd(fake_uow)
    created = await create.execute(
        user_id=1,
        title="T",
        description="d",
        price=100,
        category="c",
        city="x",
    )

    get = GetAd(fake_uow, fake_user_profile)
    view = await get.execute(created.id)

    assert view.ad.id == created.id
    assert view.ad.title == "T"
    assert view.user_name == "Alice"


@pytest.mark.asyncio
async def test_get_ad_not_found(
    fake_uow: FakeUnitOfWork,
    fake_user_profile: FakeUserProfileService,
) -> None:
    get = GetAd(fake_uow, fake_user_profile)

    with pytest.raises(AdNotFoundError):
        await get.execute(999)
