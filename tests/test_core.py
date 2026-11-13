import json
from types import SimpleNamespace

import pytest

from ticket_triage.core import classify_ticket, parse_classification, process_tickets
from ticket_triage.validate import validate


@pytest.mark.parametrize("raw", [
    '{"category":"technical","priority":"high"}',
    '```json\n{"category":"technical","priority":"high"}\n```',
])
def test_valid_json(raw):
    assert parse_classification(raw) == {"category": "technical", "priority": "high"}


@pytest.mark.parametrize("raw", [
    'not json', '[]', '{"category":"wrong","priority":"low"}',
    '{"category":"other"}', '{"category":"other","priority":"low","extra":1}',
])
def test_invalid_json(raw):
    with pytest.raises((ValueError, json.JSONDecodeError)):
        parse_classification(raw)


class FakeClient:
    def __init__(self, content):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )))


def test_classification():
    assert classify_ticket(FakeClient('{"category":"billing","priority":"medium"}'), "test-model", "Refund") == {
        "category": "billing", "priority": "medium"
    }


def test_process_and_validate(tmp_path):
    inputs, outputs = tmp_path / "tickets", tmp_path / "triaged"
    inputs.mkdir()
    (inputs / "refund.txt").write_text("Please refund me", encoding="utf-8")
    assert process_tickets(FakeClient('{"category":"billing","priority":"medium"}'), "test-model", inputs, outputs) == (1, 0)
    assert validate(inputs, outputs)
