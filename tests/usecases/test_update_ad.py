import pytest

from src.application.exceptions import AdNotFoundError, ForbiddenError
from src.application.usecases.create_ad import CreateAd
from src.application.usecases.update_ad import UpdateAd
from tests.conftest import FakeUnitOfWork


@pytest.mark.asyncio
async def test_update_ad_by_author(fake_uow: FakeUnitOfWork) -> None:
    create = CreateAd(fake_uow)
    created = await create.execute(
        user_id=1,
        title="Old",
        description="d",
        price=100,
        category="c",
        city="x",
    )

    update = UpdateAd(fake_uow)
    updated = await update.execute(
        ad_id=created.id,
        user_id=1,
        title="New",
        description=None,
        price=200,
        category=None,
        city=None,
    )

    assert updated.title == "New"
    assert updated.price == 200
    assert updated.description == "d"

    update_events = [
        m for m in fake_uow.outbox.messages if m.event_type == "ad.updated"
    ]
    assert len(update_events) == 1
    assert update_events[0].payload == {"ad_id": created.id}


@pytest.mark.asyncio
async def test_update_ad_not_found(fake_uow: FakeUnitOfWork) -> None:
    update = UpdateAd(fake_uow)

    with pytest.raises(AdNotFoundError):
        await update.execute(
            ad_id=999,
            user_id=1,
            title="x",
            description=None,
            price=None,
            category=None,
            city=None,
        )


@pytest.mark.asyncio
async def test_update_ad_by_other_user_forbidden(fake_uow: FakeUnitOfWork) -> None:
    create = CreateAd(fake_uow)
    created = await create.execute(
        user_id=1,
        title="T",
        description="d",
        price=100,
        category="c",
        city="x",
    )

    update = UpdateAd(fake_uow)

    with pytest.raises(ForbiddenError):
        await update.execute(
            ad_id=created.id,
            user_id=2,
            title="hijack",
            description=None,
            price=None,
            category=None,
            city=None,
        )

    assert all(m.event_type != "ad.updated" for m in fake_uow.outbox.messages)
