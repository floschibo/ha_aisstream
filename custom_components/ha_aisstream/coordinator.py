import asyncio
import json
import logging
from datetime import datetime

import websockets
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MMSI,
    CONF_BOUNDING_BOX,
)

_LOGGER = logging.getLogger(__name__)


class AISStreamCoordinator:
    def __init__(self, hass: HomeAssistant, config):
        self.hass = hass
        self.api_key = config[CONF_API_KEY]
        self.mmsi_list = [int(x.strip()) for x in config[CONF_MMSI].split(",")]
        self.bounding_box = json.loads(config[CONF_BOUNDING_BOX])
        self.data = {}
        self.entities = []
        self.heatmap = {}

    async def start(self):
        delay = 5

        while True:
            try:
                async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
                    subscribe = {
                        "APIKey": self.api_key,
                        "BoundingBoxes": self.bounding_box,
                        "FiltersShipMMSI": [str(m) for m in self.mmsi_list],
                        "FilterMessageTypes": ["PositionReport"]
                    }

                    await ws.send(json.dumps(subscribe))
                    _LOGGER.info("AISStream subscribed")
                    delay = 5

                    async for msg in ws:
                        try:
                            message = json.loads(msg)
                            ais = message["Message"]["PositionReport"]
                            mmsi = ais["UserID"]

                            self.data[mmsi] = {
                                "latitude": ais.get("Latitude"),
                                "longitude": ais.get("Longitude"),
                                "timestamp": datetime.now().isoformat(),
                                "sog": ais.get("Sog"),
                                "cog": ais.get("Cog"),
                                "heading": ais.get("Heading"),
                                "nav_status": ais.get("NavStatus"),
                            }

                            if mmsi not in self.heatmap:
                                self.heatmap[mmsi] = []

                            self.heatmap[mmsi].append({
                                "lat": self.data[mmsi]["latitude"],
                                "lon": self.data[mmsi]["longitude"],
                                "sog": self.data[mmsi]["sog"],
                                "timestamp": self.data[mmsi]["timestamp"],
                            })

                            for entity in self.entities:
                                entity.async_write_ha_state()

                        except Exception as e:
                            _LOGGER.warning("Fehler beim Lesen: %s", e)

            except Exception as e:
                _LOGGER.warning("WebSocket Fehler: %s – Reconnect in %ss", e, delay)
                await asyncio.sleep(delay)
                delay = min(delay * 2, 300)

    async def async_export_heatmap(self, mmsi: int, hours: int):
        cutoff = datetime.now().timestamp() - hours * 3600
        return [
            p for p in self.heatmap.get(mmsi, [])
            if datetime.fromisoformat(p["timestamp"]).timestamp() >= cutoff
        ]
