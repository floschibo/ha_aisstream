from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import AISStreamCoordinator

PLATFORMS = ["device_tracker"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = AISStreamCoordinator(hass, entry.data)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["coordinator"] = coordinator

    hass.loop.create_task(coordinator.start())

    async def handle_export_heatmap(call):
        mmsi = int(call.data["mmsi"])
        hours = int(call.data.get("hours", 24))
        data = await coordinator.async_export_heatmap(mmsi, hours)
        hass.logger.info("Heatmap export for %s (%sh): %s", mmsi, hours, data)

    hass.services.async_register(
        DOMAIN,
        "export_heatmap",
        handle_export_heatmap,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
