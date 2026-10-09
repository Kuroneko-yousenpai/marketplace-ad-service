import logging
from typing import Any

import pytest

from src.application.ports.message_broker import MessageBroker
from src.application.services.outbox_relay import OutboxRelay
from src.application.tracing import get_trace_id, trace_context
from src.infrastructure.logging_config import TraceIdFilter
from tests.conftest import FakeMessageBroker, FakeUnitOfWork


class RaisingBroker(MessageBroker):
    async def send(self, payload: dict[str, Any]) -> None:
        raise RuntimeError("kafka unavailable")


@pytest.mark.asyncio
async def test_relay_sends_and_marks_published(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    await fake_uow.outbox.add("ad.created", {"ad_id": 1})
    await fake_uow.outbox.add("ad.updated", {"ad_id": 1})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    processed = await relay._process_batch()

    assert processed == 2
    assert fake_broker.sent == [
        {"event": "ad.created", "payload": {"ad_id": 1}},
        {"event": "ad.updated", "payload": {"ad_id": 1}},
    ]
    assert fake_uow.committed
    assert fake_uow.outbox.messages == []


@pytest.mark.asyncio
async def test_relay_noop_when_outbox_empty(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    processed = await relay._process_batch()

    assert processed == 0
    assert fake_broker.sent == []
    assert not fake_uow.committed


@pytest.mark.asyncio
async def test_relay_rolls_back_and_leaves_messages_on_broker_failure(
    fake_uow: FakeUnitOfWork,
) -> None:
    await fake_uow.outbox.add("ad.created", {"ad_id": 1})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=RaisingBroker())

    with pytest.raises(RuntimeError):
        await relay._process_batch()

    assert not fake_uow.committed
    assert fake_uow.rolled_back
    assert len(fake_uow.outbox.messages) == 1


@pytest.mark.asyncio
async def test_relay_sends_each_message_under_its_own_trace_id(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    with trace_context("trace-a"):
        await fake_uow.outbox.add("ad.created", {"ad_id": 1})
    with trace_context("trace-b"):
        await fake_uow.outbox.add("ad.created", {"ad_id": 2})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    await relay._process_batch()

    assert fake_broker.trace_ids == ["trace-a", "trace-b"]
    assert get_trace_id() is None


@pytest.mark.asyncio
async def test_relay_generates_trace_id_for_rows_without_one(
    fake_uow: FakeUnitOfWork, fake_broker: FakeMessageBroker
) -> None:
    await fake_uow.outbox.add("ad.created", {"ad_id": 1})
    await fake_uow.outbox.add("ad.created", {"ad_id": 2})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    await relay._process_batch()

    first, second = fake_broker.trace_ids
    assert first and second and first != second


@pytest.mark.asyncio
async def test_relay_logs_carry_message_trace_id(
    fake_uow: FakeUnitOfWork,
    fake_broker: FakeMessageBroker,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.handler.addFilter(TraceIdFilter())
    with trace_context("trace-a"):
        await fake_uow.outbox.add("ad.created", {"ad_id": 1})

    relay = OutboxRelay(uow_factory=lambda: fake_uow, broker=fake_broker)
    with caplog.at_level(logging.INFO):
        await relay._process_batch()

    published = [r for r in caplog.records if r.getMessage().startswith("published")]
    assert [r.trace_id for r in published] == ["trace-a"]
