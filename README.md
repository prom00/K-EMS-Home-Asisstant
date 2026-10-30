# K-EMS — Home Assistant integration

Simple outbound telemetry for K-EMS. Version 0.3.1 (experimental).

By default, every 60 seconds, Home Assistant sends its version and selected entity states as JSON to a configurable HTTP(S) endpoint. It also sends once when the integration starts and exposes the manual action `k_ems.send_data`.

## Install with HACS (custom repository)

1. Publish **the contents of this repository directory** to your GitHub repository root. Keep `hacs.json` and `custom_components/` at the root.
2. In Home Assistant, open HACS > three-dot menu > Custom repositories.
3. Enter your repository URL and select the **Integration** category.
4. Download **K-EMS** and restart Home Assistant.
5. Open **Settings > Devices & services > Add integration**, search for **K-EMS**.
6. Enter the Site ID, API URL, token and optional comma-separated entity IDs.

If HACS is not installed, copy `custom_components/k_ems/` into Home Assistant's `/config/custom_components/` directory and restart.

### Migrating from the YAML prototype

Remove the old `k_ems:` block from `configuration.yaml` before restarting. The new integration uses Home Assistant's UI configuration instead. Keep your previous site ID, URL and token ready for the setup dialog.

## Example configuration values

- Site ID: `klant0001`
- API URL: `http://192.168.1.106/api.php?test` (local testing only)
- API token: any secret that matches your receiver
- Entity IDs: `sensor.boiler_temperature, sensor.solar_power, sensor.grid_power`

Unknown entity IDs are sent with `null` values.

## Request format

`POST <your API URL>` with `Content-Type: application/json` and `Authorization: Bearer <token>`:

```json
{
  "site_id": "klant0001",
  "ha_version": "2026.10.4",
  "entities": {
    "sensor.boiler_temperature": "62.5",
    "sensor.solar_power": "4200",
    "sensor.grid_power": "-1800"
  }
}
```

A successful receiver should return an HTTP 2xx status (for example 200 with `{"success":true}`). Otherwise an error is logged in Home Assistant.

## Manual test

Open **Developer tools > Actions**, choose `k_ems.send_data` and execute it. Check Home Assistant logs or the receiver's access log.

## Notes / limitations

- To change API URL, token, entity IDs, or send interval, open **Settings > Devices & services > K-EMS > Configure**. Saving automatically reloads the connection. The site ID is fixed. The interval is between 10 and 86400 seconds.
- Currently supports one configuration entry per Home Assistant installation.
- No remote control or remote upgrade features.
- This prototype does **not** retry failed sends or queue data offline.
- Use HTTPS and distinct per-site tokens for real deployments. Treat the receiving API as untrusted and restrict access and token privileges.
- The integration has not been runtime-tested against every Home Assistant version. Check logs after installation.

## Upgrade from v0.2.0

Update the files from GitHub/HACS and restart Home Assistant. Your existing K-EMS configuration is retained. Open **Settings > Devices & services > K-EMS > Configure** to edit your settings. No need to remove/re-add the integration.


## Entity selection (v0.3.1)

When adding the integration or choosing **Configure**, choose one or more entities
using Home Assistant's searchable entity selector. Previously selected entities are
preselected when editing settings. Telemetry JSON remains unchanged.

## GitHub versioning and HACS updates

Version numbers follow semantic versioning (`MAJOR.MINOR.PATCH`). The version
in `custom_components/k_ems/manifest.json` must match the Git tag (with `v` prefix).
The bundled GitHub Actions workflow validates this and publishes a GitHub Release
whenever you push a matching version tag. **A tag alone is not a published release.**

For this release, upload/commit the changed repository contents first, then run:

```bash
git add .
git commit -m "Add entity selector and release automation v0.3.1"
git push origin main
git tag v0.3.1
git push origin v0.3.1
```

If `v0.3.1` already exists, choose a higher version in `manifest.json`
and use that version in your tag. Check **GitHub → Actions** and **Releases** after
pushing the tag. GitHub Actions must be enabled for your repository.
The workflow validates the manifest version and creates the GitHub Release. HACS
can then detect the published release and make the integration update available.

To prepare a later release, edit `manifest.json` to the next version, commit
and push, then create and push the corresponding Git tag. Do not push a tag
before the manifest is updated.
