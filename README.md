# E-Ink Display Manager

Vendor-agnostic Home Assistant integration for managing e-ink display profiles. Provides a WYSIWYG editor card for designing label layouts, scheduled updates with Jinja2 template resolution, and multi-profile switching across e-ink devices.

E-Ink Display Manager does not render images or talk to hardware itself. It orchestrates a `drawcustom` service provided by a backend integration:

- [OpenEPaperLink](https://github.com/OpenEPaperLink/Home_Assistant_Integration) — `open_epaper_link.drawcustom`
- [Wolink BLE E-Paper Labels](https://github.com/shorti1996/zhsunyco-esl-wolink) — `wolink_esl.drawcustom`
- Any other integration exposing a compatible `drawcustom` service

The backend is auto-detected from the target image entity's platform, or can be set manually in the card editor.

## Features

- **WYSIWYG card editor** — drag-and-drop layout design with live preview
- **Scheduled rendering** — periodic + entity-triggered updates with debounce
- **Jinja2 templates** — dynamic content from any HA sensor/entity
- **Multi-profile** — multiple layouts per display, switch active profile at runtime

## Installation

Requires [HACS](https://hacs.xyz/docs/use/) (Home Assistant Community Store).

1. [Add this repository as a custom repository](https://hacs.xyz/docs/faq/custom_repositories/) in HACS (category: **Integration**).
2. Install **E-Ink Display Manager** from the HACS store.
3. Restart Home Assistant.

## Source

This repository is auto-published from the monorepo: [shorti1996/zhsunyco-eink](https://github.com/shorti1996/zhsunyco-eink)
