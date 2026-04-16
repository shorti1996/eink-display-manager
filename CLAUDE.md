# eink_display_manager

Home Assistant custom integration — **dispatcher + editor** for passive e-ink displays. Does not talk BLE itself; delegates to a platform-specific `*.drawcustom` service (e.g. `wolink_esl.drawcustom`).

## What it does

- **Profile management**: many profiles per display entity; one active at a time (enforced via switch). Active profile map persisted to `.storage/eink_display_manager/_active_profiles.json`.
- **Payload editing**: WYSIWYG Lovelace card (`eink-editor-card`) with SVG preview, drag-to-move, property panel, code view, template resolution.
- **Template tracking**: Jinja2 templates auto-extracted from payload, tracked via `async_track_template_result`. Any state referenced becomes a refresh trigger.
- **Two-tier debounce** (T0→T1→T2→T3): source arbitration → per-entity BoundedDebouncer (trailing edge + max_wait starvation guard) → global leading-edge gate → resolve/hash/dispatch. Pipeline documented at top of `coordinator.py`.
- **Hash dedup**: SHA256 of resolved payload + settings. Skip service call if unchanged (unless `force=True`).
- **Retry**: on service error, retry up to `retry_count` times, spaced `retry_delay` minutes. New trigger supersedes pending retries.

## Architecture (v2: singleton + subentries)

- **Singleton parent entry**: `data={}`, no options. One per install.
- **Profile subentries** (`subentry_type="profile"`): hold cold config (entity_id, service, width, height, background, rotate, dither, compress, mirror, update_interval, trigger_entities, debounce_config, retry_*).
- **Hot payload**: `.storage/eink_display_manager/{subentry_id}.json` (element list). Not in subentry.data — saved/loaded by coordinator.
- **Migration v1→v2**: `_async_migrate_integration()` in `__init__.py` consolidates per-profile entries into singleton + subentries, remaps entity unique_ids from entry_id → subentry_id.

## Platforms (`const.py`: `PLATFORMS = ["sensor", "button", "switch"]`)

| File | Entities | Scope |
|------|----------|-------|
| `sensor.py` | `LastUpdateSensor`, `StatusSensor` (idle/updating/retrying/error) | **Device** (wolink_esl), not profile — see memory `feedback_device_level_tracking.md` |
| `button.py` | `RefreshButton` (force update), `StopButton` (cancel pending/retries) | Profile |
| `switch.py` | `ProfileEnabledSwitch` — enforces single-active-per-display | Profile |

## Services (`services.yaml`, registered in `__init__.py`)

- `eink_display_manager.refresh` — target: button entity. Force immediate update of one profile.
- `eink_display_manager.refresh_all` — force update all enabled profiles.

## WebSocket API (`__init__.py` `_register_websocket_commands`)

All use domain prefix `eink_display_manager/`:

| Endpoint | Purpose |
|----------|---------|
| `list_profiles` | Enumerate all profiles + active status |
| `get_payload` | Fetch payload + cold config for subentry |
| `update_payload` | Hot-save payload to `.storage`, reload template tracking |
| `update_profile_settings` | Hot-save dither/background/rotate/compress/mirror/debounce_config |
| `resolve_templates` | Render payload templates for preview (no dispatch) |
| `activate_profile` | Switch active profile; disables siblings targeting same display |
| `create_profile` | Auto-create if missing for entity |
| `get_tracked_entities` | Return entities this profile depends on + debounce config |

## Frontend card

- **Source**: `frontend/src/eink-editor-card.ts` (Lit, ES2021). Helpers: `svg-renderer.ts`, `types.ts`.
- **Build**: `cd frontend && npm run build` (rollup + terser → `../www/eink-editor-card.js`). `npm run watch` for dev.
- **Served**: via `/hacsfiles/eink_display_manager/` (URL_BASE in `const.py`). `JSModuleRegistration` registers Lovelace resource with `?v=X.Y.Z` cache-bust from `manifest.json` version.
- **Modes**: `preview` | `edit` | `code`. Edit mode renders property panel per selected element.
- **Runtime UI prefs** persisted in `localStorage` — card config-changed event only works in card editor (see memory `feedback_card_config_persistence.md`). Existing keys: `eink-editor-show-preview`, `eink-editor-render-templates`, `eink-editor-color-text-mode`.
- **Templates resolve in preview** via `resolve_templates` WS call when "Render Templates" button is on.
- **Color fields**: toggle between `ha-select` dropdown and `ha-textfield` (for raw hex or Jinja template). `_renderColorField(label, el, prop, withNone)` helper. `ha-select` rewritten in HA 2026.02+ — see memory `feedback_ha_select_2026.md`.

## Element types (`frontend/src/types.ts`)

`text`, `multiline`, `rectangle`, `line`, `icon` (MDI), `dlimg` (URL-fetched image), `circle`, `ellipse`, `qrcode`, `progress_bar`. Positioning mix of `{x,y}` anchor vs `{x_start,y_start,x_end,y_end}` bounds — see `getElementBounds` / `moveElement` in helper utils for normalization.

## Coordinator (`coordinator.py`) — log tiers

`ProfileCoordinator` — one per subentry. Log tags `T0`/`T1`/`T2`/`T3` correspond to debounce pipeline stages — see memory `project_eink_log_tiers.md`. Key methods:

- `async_start()` / `async_stop()` — subscribe/unsubscribe time interval, templates, manual trigger entities.
- `async_load_payload()` — read hot payload from `.storage` (executor).
- `update_payload()` — hot-update + re-extract templates.
- `async_trigger_update(reason, force=False)` — T3 entry: resolve → hash → dispatch → retry.
- `get_tracked_entities()` — union of template deps + explicit trigger_entities.
- `update_debounce_config()` — hot-reset BoundedDebouncer state.
- `cancel_pending()` — abort retries + in-flight calls.

Startup renders staggered by `_STARTUP_RENDER_DELAY + idx * _STARTUP_RENDER_STAGGER` to avoid BLE queue buildup. `EDM_SKIP_STARTUP_RENDER=1` env var bypasses.

## Service dispatch

Derived by `_derive_service(entity_id)` in `config_flow.py`: reads entity platform, appends `.drawcustom`. Fallback scans all services. Final fallback `wolink_esl.drawcustom`. Call shape:

```
hass.services.async_call(
    domain, service,
    {entity_id, payload (resolved), background, rotate, dither,
     compress, mirror, dry_run: False},
    blocking=True,  # 300s timeout
)
```

## Dev workflow

**Frontend iteration**:
```bash
cd custom_components/eink_display_manager/frontend
npm run watch    # rebuild on change → ../www/eink-editor-card.js
```
Then hard-refresh HA Lovelace (or bump `manifest.json` version for cache bust).

**Version bump**: edit `manifest.json` `version`. `const.py` `INTEGRATION_VERSION` loads from manifest at runtime.

**Release flow** (from recent commits): `bump: update version to X.Y.Z` commit touching `manifest.json` only. HACS distribution via `hacs.json` at repo root.

## Invariants / gotchas

- **Never add sensors at profile layer** for status/observability — belongs at device (wolink_esl) layer. Memory: `feedback_device_level_tracking.md`.
- **Don't `git add -A` / `.`** — user stages selectively. Memory: `feedback_no_git_add_all.md`.
- **`config-changed` event from card only fires in card editor context** — use localStorage for runtime UI prefs. Memory: `feedback_card_config_persistence.md`.
- **WOLINK BLE protocol** details (UUIDs, commands, status codes) in memory `project_wolink_protocol.md` — relevant when debugging the downstream `wolink_esl` integration, not this one.
- **Active profile switching is eager**: enabling a profile auto-disables siblings pointing at the same entity. Sync persists to `_active_profiles.json` before returning.
- **Hash dedup uses resolved payload**: same template → different state will trigger update (resolved output differs).
- **Template tracking first-change ignored** (initialization). Subsequent changes route to T1.

## Layout

```
custom_components/eink_display_manager/
├── __init__.py            setup, migration, WS/service registration
├── coordinator.py         ProfileCoordinator, debounce pipeline
├── config_flow.py         singleton + subentry flows, reconfigure
├── const.py               constants, config keys, version
├── manifest.json          domain, version, deps (frontend, http)
├── services.yaml
├── strings.json           HA UI strings (config flow)
├── sensor.py / button.py / switch.py
├── translations/en.json   config flow labels (NOT card labels — card is hardcoded)
├── fonts/                 TTFs served via /hacsfiles/
├── frontend/
│   ├── src/               eink-editor-card.ts, svg-renderer.ts, types.ts
│   ├── rollup.config.js
│   └── package.json       build / dev / watch scripts
└── www/
    └── eink-editor-card.js  compiled bundle (commit this for HACS)
```
