# Changelog

## 0.3.1

- Select multiple Home Assistant entities from searchable selectors during setup and in options.
- Preserve previously selected entities when editing integration settings.
- Add GitHub Actions release automation with tag/manifest-version validation.

## 0.3.0

- Editable connection settings and telemetry interval via OptionsFlowWithReload.

## v0.3.2 - 2026-10-30

### Fixed
- Fixed integration reload failure after changing settings.
- Removed incorrect ConfigEntry.async_unload() call.
- Entity selections now apply without restarting Home Assistant.