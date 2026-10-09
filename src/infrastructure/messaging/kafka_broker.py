import json
import typing

from aiokafka import AIOKafkaProducer

from src.application.ports.message_broker import MessageBroker
from src.application.tracing import KAFKA_TRACE_ID_HEADER, get_trace_id


class KafkaMessageBroker(MessageBroker):
    def __init__(self, producer: AIOKafkaProducer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    async def send(self, payload: dict[str, typing.Any]) -> None:
        trace_id = get_trace_id()
        headers = [(KAFKA_TRACE_ID_HEADER, trace_id.encode())] if trace_id else None
        await self._producer.send_and_wait(self._topic, payload, headers=headers)


def serialize(value: dict[str, typing.Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")
