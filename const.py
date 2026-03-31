"""Constants for E-Ink Display Manager."""

import json
from pathlib import Path
from typing import Final

DOMAIN: Final[str] = "eink_display_manager"

_MANIFEST_PATH = Path(__file__).parent / "manifest.json"
with open(_MANIFEST_PATH, encoding="utf-8") as _f:
    INTEGRATION_VERSION: Final[str] = json.load(_f).get("version", "0.0.0")

URL_BASE: Final[str] = "/eink_display_manager"

JSMODULES: Final[list[dict[str, str]]] = [
    {
        "name": "E-Ink Editor Card",
        "filename": "eink-editor-card.js",
        "version": INTEGRATION_VERSION,
    },
]

CONF_NAME = "name"
CONF_SERVICE = "service"
CONF_ENTITY_ID = "entity_id"
CONF_PAYLOAD_JSON = "payload_json"
CONF_BACKGROUND = "background"
CONF_ROTATE = "rotate"
CONF_DITHER = "dither"
CONF_WIDTH = "width"
CONF_HEIGHT = "height"
CONF_UPDATE_INTERVAL = "update_interval_minutes"
CONF_TRIGGER_ENTITIES = "trigger_entities"
CONF_DEBOUNCE = "trigger_debounce_seconds"
CONF_ENABLED = "enabled"
CONF_RETRY_DELAY = "retry_delay"
CONF_RETRY_COUNT = "retry_count"

PLATFORMS = ["sensor", "button", "switch"]
