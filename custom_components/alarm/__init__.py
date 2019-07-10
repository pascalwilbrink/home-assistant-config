"""Alarm"""
import logging
import datetime

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    ATTR_ENTITY_ID, 
    ATTR_UNIT_OF_MEASUREMENT, 
    CONF_ICON, 
    CONF_NAME, 
    CONF_MODE
) 

from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'alarm'
ENTITY_ID_FORMAT = DOMAIN + '.{}'

CONF_MINUTE = 'minute'
CONF_HOUR = 'hour'
CONF_ENABLED = 'enabled'

ATTR_MINUTE = 'minute'
ATTR_HOUR = 'hour'
ATTR_ENABLED = 'enabled'

SERVICE_SET_VALUE = 'set_value'
SERVICE_TOGGLE = 'toggle'

SERVICE_SET_VALUE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required(ATTR_HOUR): vol.Coerce(float),
    vol.Required(ATTR_MINUTE): vol.Coerce(float)
})

SERVICE_TOGGLE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required(ATTR_ENABLED): vol.Coerce(bool)
})

def _cv_alarm(cfg):
    """Configure validation helper for Alarm (voluptuous)."""
    minute = cfg.get(CONF_MINUTE)
    hour = cfg.get(CONF_HOUR)

    if minute >= 60:
        raise vol.Invalid('Minute ({}) is greater than 59'.format(minute))

    if minute < 0:
        raise vol.Invalid('Minute ({}) is less than 0'.format(minute))
    
    if hour >= 24:
        raise vol.Invalid('Hour ({}) is greater than 23'.format(hour))
        
    if minute < 0:
        raise vol.Invalid('Hour ({}) is less than 0'.format(hour))

    return cfg

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: cv.schema_with_slug_keys(
        vol.All({
            vol.Optional(CONF_NAME): cv.string,
            vol.Required(CONF_MINUTE): vol.Coerce(float),
            vol.Required(CONF_HOUR): vol.Coerce(float),
            vol.Optional(CONF_ICON): cv.icon,
            vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        }, _cv_alarm)
    )
}, required=True, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Set up an alarm."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)

    entities = []

    for object_id, cfg in config[DOMAIN].items():

        name = cfg.get(CONF_NAME)
        minute = cfg.get(CONF_MINUTE)
        hour = cfg.get(CONF_HOUR)
        icon = cfg.get(CONF_ICON)
        enabled = cfg.get(CONF_ENABLED)
 
        entities.append(
            Alarm(
                object_id, 
                name, 
                minute, 
                hour, 
                icon,
                enabled
            )
        )

    if not entities:
        return False

    async def async_set_value_service(entity, call):
        """Handle set value call to the Alarm service."""
        hour = call.data.get(ATTR_HOUR)
        minute = call.data.get(ATTR_MINUTE)

        entity.async_set_value(hour, minute)

    async def async_toggle_service(entity, call):
        """Handle toggle call to the Alarm service."""
        enabled = call.data.get(ATTR_ENABLED)

        entity.async_toggle(enabled)

    component.async_register_entity_service(
        SERVICE_SET_VALUE, 
        SERVICE_SET_VALUE_SCHEMA,
        'async_set_value'
    )

    component.async_register_entity_service(
        SERVICE_TOGGLE,
        SERVICE_TOGGLE_SCHEMA,
        'async_toggle'
    )

    await component.async_add_entities(entities)

    return True

class Alarm(RestoreEntity):
    """Representation of an alarm."""

    def __init__(self, object_id, name, minute, hour, icon, enabled):
        """Initialize an alarm."""
        self.entity_id = ENTITY_ID_FORMAT.format(object_id)
        self._name = name
        self._minute = minute
        self._hour = hour
        self._icon = icon
        self._enabled = enabled
        self._ringing = False

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        return self._ringing

    @property
    def state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_MINUTE: self._minute,
            ATTR_HOUR: self._hour,
            ATTR_ENABLED: self._enabled
        }

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        if self._hour is not None:
            return

        if self._minute is not None:
            return

        state = await self.async_get_last_state()

        value_hour = state and float(state.state.hour)
        value_minute = state and float(state.state.minute)

        self._hour = value_hour
        self._minute = value_minute

    def update(self):
        now = datetime.datetime.now()

        current_hour = now.hour
        current_minute = now.minute

        if not self._enabled or self._ringing:
            return

        if current_hour == self._hour and current_minute == self._minute:
            self._ringing = True

    async def async_toggle(self, enabled):
        enabled_value = bool(enabled)
        
        if enabled_value is None:
            return

        self._enabled = enabled_value
        
        await self.async_update_ha_state()

    async def async_set_value(self, hour, minute):
        hour_num_value = float(hour)
        minute_num_value = float(minute)
        
        if hour_num_value and hour_num_value < 0 or hour_num_value >= 24:
            _LOGGER.warning("Invalid hour value: %s (range 0 - 23)", hour_num_value)
            
            return
        
        self._hour = hour_num_value

        if minute_num_value and minute_num_value < 0 or minute_num_value >= 60:
            _LOGGER.warning("Invalid minute value: %s (range 0 - 59", minute_num_value)
        
            return
        
        self._minute = minute_num_value
        
        await self.async_update_ha_state()

