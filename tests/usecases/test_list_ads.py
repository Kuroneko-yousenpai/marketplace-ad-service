import pytest

from src.application.usecases.create_ad import CreateAd
from src.application.usecases.list_ads import ListAds
from tests.conftest import FakeUnitOfWork, FakeUserProfileService


async def _seed(uow: FakeUnitOfWork) -> None:
    create = CreateAd(uow)
    await create.execute(
        user_id=1,
        title="A",
        description="d",
        price=100,
        category="Электроника",
        city="Москва",
    )
    await create.execute(
        user_id=1,
        title="B",
        description="d",
        price=300,
        category="Электроника",
        city="Питер",
    )
    await create.execute(
        user_id=2,
        title="C",
        description="d",
        price=200,
        category="Одежда",
        city="Москва",
    )


@pytest.mark.asyncio
async def test_list_ads_returns_all_active(
    fake_uow: FakeUnitOfWork,
    fake_user_profile: FakeUserProfileService,
) -> None:
    await _seed(fake_uow)

    usecase = ListAds(fake_uow, fake_user_profile)
    views, total = await usecase.execute(
        user_id=None,
        limit=20,
        offset=0,
    )

    assert total == 3
    assert len(views) == 3


@pytest.mark.asyncio
async def test_list_ads_pagination(
    fake_uow: FakeUnitOfWork,
    fake_user_profile: FakeUserProfileService,
) -> None:
    await _seed(fake_uow)

    usecase = ListAds(fake_uow, fake_user_profile)
    views, total = await usecase.execute(
        user_id=None,
        limit=2,
        offset=0,
    )

    assert total == 3
    assert len(views) == 2


@pytest.mark.asyncio
async def test_list_ads_filter_by_user(
    fake_uow: FakeUnitOfWork,
    fake_user_profile: FakeUserProfileService,
) -> None:
    await _seed(fake_uow)

    usecase = ListAds(fake_uow, fake_user_profile)
    views, total = await usecase.execute(
        user_id=1,
        limit=20,
        offset=0,
    )

    assert total == 2
    assert all(v.ad.user_id == 1 for v in views)
    assert all(v.user_name == "Alice" for v in views)
