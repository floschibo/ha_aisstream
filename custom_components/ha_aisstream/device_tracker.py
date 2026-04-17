from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SHIP_NAMES


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN]["coordinator"]

    entities = []
    for mmsi in coordinator.mmsi_list:
        entities.append(AISDeviceTracker(hass, coordinator, mmsi))

    coordinator.entities.extend(entities)
    async_add_entities(entities)


class AISDeviceTracker(TrackerEntity):
    def __init__(self, hass, coordinator, mmsi):
        self.hass = hass
        self.coordinator = coordinator
        self.mmsi = mmsi
        name = SHIP_NAMES.get(mmsi, str(mmsi))
        self._attr_unique_id = f"aisstream_{mmsi}"
        self._attr_name = f"Kanalfähre {name}"

    @property
    def device_info(self):
        name = SHIP_NAMES.get(self.mmsi, str(self.mmsi))
        return {
            "identifiers": {("ha_aisstream", str(self.mmsi))},
            "name": f"Schiff {name}",
            "manufacturer": "AISStream",
            "model": "AIS Vessel",
        }

    @property
    def latitude(self):
        return self.coordinator.data.get(self.mmsi, {}).get("latitude")

    @property
    def longitude(self):
        return self.coordinator.data.get(self.mmsi, {}).get("longitude")

    @property
    def source_type(self):
        return "gps"

    @property
    def extra_state_attributes(self):
        d = self.coordinator.data.get(self.mmsi, {}) or {}
        return {
            "mmsi": self.mmsi,
            "timestamp": d.get("timestamp"),
            "sog": d.get("sog"),
            "cog": d.get("cog"),
            "heading": d.get("heading"),
            "nav_status": d.get("nav_status"),
        }
