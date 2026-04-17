from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_API_KEY, CONF_MMSI, CONF_BOUNDING_BOX


class AISStreamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="AISStream", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_MMSI): str,
            vol.Optional(CONF_BOUNDING_BOX, default="[[[-90,-180],[90,180]]]"): str
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AISStreamOptionsFlow(config_entry)


class AISStreamOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_API_KEY, default=self.entry.data[CONF_API_KEY]): str,
            vol.Required(CONF_MMSI, default=self.entry.data[CONF_MMSI]): str,
            vol.Required(CONF_BOUNDING_BOX, default=self.entry.data[CONF_BOUNDING_BOX]): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
