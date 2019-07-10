"""Alarm platform."""
import logging
import datetime

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.binary_sensor import (
    BinarySensorDevice,
    PLATFORM_SCHEMA,
    DEVICE_CLASSES_SCHEMA
)

from homeassistant.const import CONF_NAME, CONF_DEVICE_CLASS

ATTR_HOUR = 'hour'
ATTR_MINUTE = 'minute'

CONF_HOUR = 'hour'
CONF_MINUTE = 'minute'
CONF_ENABLED = 'enabled'

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Alarm'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOUR, default=6): vol.Coerce(int),
    vol.Required(CONF_MINUTE, default=0): vol.Coerce(int),
    vol.Optional(CONF_ENABLED, default=True): vol.Coerce(bool)
})

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    hour = config.get(CONF_HOUR)
    minute = config.get(CONF_MINUTE)

    add_entities([
        Alarm(name, hour, minute)
    ])

class Alarm(BinarySensorDevice):
    """Representation of an alarm."""

    def __init__(self, name, hour, minute):
        """Initialize the alarm."""

        _LOGGER.info('Setting alarm at %s:%s', hour, minute)
        self._name = name
        self._state = False
        
        self._hour = hour
        self._minute = minute

        self._sensor_type = 'datetime'

    @property
    def device_class(self):
        """Returns the class of the alarm."""
        return self._sensor_type

    @property
    def name(self):
        """Returns the name of the alarm."""
        return self._name

    @property
    def is_on(self):
        """Returns true if the alarm is ringing."""
        return self._state

    @property
    def state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_MINUTE: self._minute,
            ATTR_HOUR: self._hour
        }

    async def async_update(self):
        """Check if alarm should ring."""
        now = datetime.datetime.now()

        current_hour = now.hour
        current_minute = now.minute

        _LOGGER.info('Checking current hour (%s) to alarm hour (%s) and current minute (%s) to alarm minute (%s)', current_hour, self._hour, current_minute, self._minute)
        
        if current_hour == self._hour and current_minute == self._minute:
            self._state = True
        else:
            self._state = False
