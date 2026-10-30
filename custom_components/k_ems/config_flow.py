"""Configuration flow for K-EMS."""

from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN


class KEMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a K-EMS configuration flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Collect the site connection and entity IDs."""
        errors = {}

        if user_input is not None:
            site_id = user_input["site_id"].strip()
            url = user_input["url"].strip()
            token = user_input["token"].strip()
            parsed_url = urlparse(url)

            if (
                parsed_url.scheme not in ("http", "https")
                or not parsed_url.hostname
                or parsed_url.username is not None
                or parsed_url.password is not None
            ):
                errors["base"] = "invalid_url"
            elif not site_id or not token:
                errors["base"] = "invalid_input"
            else:
                entities = list(dict.fromkeys(
                    item.strip()
                    for item in user_input.get("entities", "").split(",")
                    if item.strip()
                ))

                await self.async_set_unique_id(site_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"K-EMS {site_id}",
                    data={
                        "site_id": site_id,
                        "url": url,
                        "token": token,
                        "entities": entities,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("site_id", default="klant0001"): str,
                vol.Required("url", default="https://api.k-ems.eu/api/telemetry"): str,
                vol.Required("token"): str,
                vol.Optional("entities", default=""): str,
            }),
            errors=errors,
        )
