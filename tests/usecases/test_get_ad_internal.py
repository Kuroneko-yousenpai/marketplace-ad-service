import pytest

from src.application.exceptions import AdNotFoundError
from src.application.usecases.create_ad import CreateAd
from src.application.usecases.delete_ad import DeleteAd
from src.application.usecases.get_ad_internal import GetAdInternal
from src.domain.entities import AdStatus
from tests.conftest import FakeUnitOfWork


@pytest.mark.asyncio
async def test_get_ad_internal_returns_active(fake_uow: FakeUnitOfWork) -> None:
    create = CreateAd(fake_uow)
    created = await create.execute(
        user_id=1,
        title="T",
        description="d",
        price=100,
        category="c",
        city="x",
    )

    usecase = GetAdInternal(fake_uow)
    ad = await usecase.execute(created.id)

    assert ad.id == created.id
    assert ad.status == AdStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_ad_internal_returns_archived(fake_uow: FakeUnitOfWork) -> None:
    create = CreateAd(fake_uow)
    created = await create.execute(
        user_id=1,
        title="T",
        description="d",
        price=100,
        category="c",
        city="x",
    )

    delete = DeleteAd(fake_uow)
    await delete.execute(ad_id=created.id, user_id=1)

    usecase = GetAdInternal(fake_uow)
    ad = await usecase.execute(created.id)

    assert ad.id == created.id
    assert ad.status == AdStatus.ARCHIVED


@pytest.mark.asyncio
async def test_get_ad_internal_not_found(fake_uow: FakeUnitOfWork) -> None:
    usecase = GetAdInternal(fake_uow)

    with pytest.raises(AdNotFoundError):
        await usecase.execute(999)
