"""K-EMS telemetry integration."""

import asyncio
import logging
from datetime import timedelta

from aiohttp import ClientTimeout
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.loader import async_get_integration

from .const import DOMAIN, SEND_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the manual send action."""
    hass.data.setdefault(DOMAIN, {})

    async def handle_send_data(call: ServiceCall) -> None:
        """Send telemetry immediately for all configured K-EMS entries."""
        senders = list(hass.data[DOMAIN].values())
        if not senders:
            _LOGGER.warning("No K-EMS site is configured")
            return
        await asyncio.gather(*(sender() for sender in senders))

    hass.services.async_register(DOMAIN, "send_data", handle_send_data)
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Start telemetry for a configured site."""
    settings = {**entry.data, **entry.options}
    integration = await async_get_integration(hass, DOMAIN)
    k_ems_version = integration.version

    async def send_data() -> None:
        """POST current entity states to the central K-EMS endpoint."""
        states = {}
        for entity_id in settings.get("entities", []):
            state = hass.states.get(entity_id)
            states[entity_id] = state.state if state is not None else None

        payload = {
            "site_id": settings["site_id"],
            "ha_version": HA_VERSION,
            "k_ems_version": k_ems_version,
            "entities": states,
        }

        _LOGGER.warning("K-EMS outgoing payload: %s", payload)

        try:
            session = async_get_clientsession(hass)
            async with session.post(
                settings["url"],
                json=payload,
                headers={"Authorization": f"Bearer {settings['token']}"},
                timeout=ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()

            _LOGGER.info("K-EMS telemetry sent for %s", settings["site_id"])
        except Exception:
            _LOGGER.exception(
                "Failed to send K-EMS telemetry for %s", settings["site_id"]
            )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = send_data

    @callback
    def schedule_send_data(now) -> None:
        """Queue the next telemetry update."""
        entry.async_create_background_task(
            hass, send_data(), "k_ems_periodic_telemetry"
        )

    unsubscribe = async_track_time_interval(
        hass,
        schedule_send_data,
        timedelta(seconds=settings.get("send_interval", SEND_INTERVAL_SECONDS)),
    )
    entry.async_on_unload(unsubscribe)
    entry.async_create_background_task(hass, send_data(), "k_ems_initial_telemetry")
    return True


async def async_unload_entry(hass, entry):
    """Unload a K-EMS configuration entry."""

    entry.async_unload(hass)
    hass.data[DOMAIN].pop(entry.entry_id, None)

    return True
