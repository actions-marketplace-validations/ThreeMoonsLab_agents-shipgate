from __future__ import annotations

from agents_shipgate.checks import registry


def test_plugin_checks_disabled_by_default(monkeypatch):
    loaded = {"called": False}

    class FakeEntryPoint:
        value = "acme_shipgate_checks:run"

        def load(self):
            loaded["called"] = True
            return lambda context: []

    monkeypatch.delenv("AGENTS_SHIPGATE_ENABLE_PLUGINS", raising=False)
    monkeypatch.setattr(
        registry,
        "entry_points",
        lambda group: [FakeEntryPoint()],
    )

    assert registry._plugin_checks() == []
    assert loaded["called"] is False


def test_plugin_checks_load_only_when_enabled(monkeypatch):
    def plugin(context):
        return []

    metadata = {
        "id": "ACME-CHECK",
        "category": "custom",
        "default_severity": "medium",
        "description": "Custom plugin check.",
    }
    plugin.AGENTS_SHIPGATE_METADATA = metadata

    class FakeEntryPoint:
        value = "acme_shipgate_checks:run"

        def load(self):
            return plugin

    monkeypatch.setenv("AGENTS_SHIPGATE_ENABLE_PLUGINS", "1")
    monkeypatch.setattr(
        registry,
        "entry_points",
        lambda group: [FakeEntryPoint()],
    )

    assert registry._plugin_checks() == [plugin]
    catalog = registry.check_catalog()
    assert any(check.id == "ACME-CHECK" for check in catalog)
