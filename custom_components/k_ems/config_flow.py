"""Configuration and options flows for K-EMS."""

from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN, SEND_INTERVAL_SECONDS


def is_valid_url(url):
    """Check whether the server URL can be used."""
    parsed = urlparse(url)
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
    )




class KEMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a K-EMS telemetry connection."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Collect initial configuration."""
        errors = {}
        if user_input is not None:
            site_id = user_input["site_id"].strip()
            url = user_input["url"].strip()
            token = user_input["token"].strip()

            if not is_valid_url(url):
                errors["base"] = "invalid_url"
            elif not site_id or not token:
                errors["base"] = "invalid_input"
            else:
                await self.async_set_unique_id(site_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"K-EMS {site_id}",
                    data={
                        "site_id": site_id,
                        "url": url,
                        "token": token,
                        "entities": user_input.get("entities", []),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("site_id", default="klant0001"): str,
                vol.Required("url", default="https://api.k-ems.eu/api/telemetry"): str,
                vol.Required("token"): str,
                vol.Optional("entities", default=[]): selector.EntitySelector(
                    selector.EntitySelectorConfig(multiple=True)
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the editable options form."""
        return KEMSOptionsFlow()


class KEMSOptionsFlow(config_entries.OptionsFlowWithReload):
    """Edit connection settings and reload the integration automatically."""

    async def async_step_init(self, user_input=None):
        """Show and save editable integration settings."""
        settings = {**self.config_entry.data, **self.config_entry.options}
        errors = {}

        if user_input is not None:
            url = user_input["url"].strip()
            token = user_input["token"].strip()
            if not is_valid_url(url):
                errors["base"] = "invalid_url"
            elif not token:
                errors["base"] = "invalid_input"
            else:
                return self.async_create_entry(
                    data={
                        "url": url,
                        "token": token,
                        "entities": user_input.get("entities", []),
                        "send_interval": user_input["send_interval"],
                    }
                )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("url", default=settings["url"]): str,
                vol.Required("token", default=settings["token"]): str,
                vol.Optional(
                    "entities",
                    default=settings.get("entities", []),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(multiple=True)
                ),
                vol.Required(
                    "send_interval",
                    default=settings.get("send_interval", SEND_INTERVAL_SECONDS),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=86400)),
            }),
            errors=errors,
        )
