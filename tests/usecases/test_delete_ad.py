import pytest

from src.application.exceptions import AdNotFoundError, ForbiddenError
from src.application.usecases.create_ad import CreateAd
from src.application.usecases.delete_ad import DeleteAd
from src.domain.entities import AdStatus
from tests.conftest import FakeUnitOfWork


@pytest.mark.asyncio
async def test_delete_ad_by_author(fake_uow: FakeUnitOfWork) -> None:
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

    archived = await fake_uow.ads.get_by_id(created.id)
    assert archived is not None
    assert archived.status == AdStatus.ARCHIVED

    delete_events = [
        m for m in fake_uow.outbox.messages if m.event_type == "ad.deleted"
    ]
    assert len(delete_events) == 1
    assert delete_events[0].payload == {"ad_id": created.id}


@pytest.mark.asyncio
async def test_delete_ad_already_archived(fake_uow: FakeUnitOfWork) -> None:
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

    with pytest.raises(AdNotFoundError):
        await delete.execute(ad_id=created.id, user_id=1)

    delete_events = [
        m for m in fake_uow.outbox.messages if m.event_type == "ad.deleted"
    ]
    assert len(delete_events) == 1


@pytest.mark.asyncio
async def test_delete_ad_not_found(fake_uow: FakeUnitOfWork) -> None:
    delete = DeleteAd(fake_uow)

    with pytest.raises(AdNotFoundError):
        await delete.execute(ad_id=999, user_id=1)


@pytest.mark.asyncio
async def test_delete_ad_by_other_user_forbidden(fake_uow: FakeUnitOfWork) -> None:
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

    with pytest.raises(ForbiddenError):
        await delete.execute(ad_id=created.id, user_id=2)

    still_active = await fake_uow.ads.get_by_id(created.id)
    assert still_active is not None
    assert still_active.status == AdStatus.ACTIVE
    assert all(m.event_type != "ad.deleted" for m in fake_uow.outbox.messages)
