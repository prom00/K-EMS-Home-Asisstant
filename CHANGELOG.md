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


## v0.3.3 - 2026-10-30

### Added
- Added K-EMS integration version to telemetry payload (`k_ems_version`).
- Added `sensor.k_ems_version` to display the installed K-EMS version in Home Assistant.
- Integration version is automatically retrieved from `manifest.json`.

### Improved
- Central monitoring can now identify installed K-EMS versions across customer installations.
- Version information is automatically included in every telemetry request.