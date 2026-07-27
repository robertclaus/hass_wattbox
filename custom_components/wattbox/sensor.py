"""
Component for interacting with a WattBox(tm) (SnapAV) - brand
ip-controlled power strip.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/wattbox/
"""
import logging

from homeassistant.helpers.entity import Entity
from ..wattbox import WattBoxDevice, DEVICES

_LOGGER = logging.getLogger(__name__)

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the wattbox power strip sensors."""
    devs = []
    for (area_name, wb) in hass.data[DEVICES]['sensor']:
        devs.append(WattBoxSensor(wb, area_name,
                                  "power", lambda c: c.power))
        devs.append(WattBoxSensor(wb, area_name,
                                  "current", lambda c: c.current))
        devs.append(WattBoxSensor(wb, area_name,
                                  "voltage", lambda c: c.voltage))

    add_devices(devs, True)
    _LOGGER.debug("Added wattbox sensors %s", devs)
    return True


class WattBoxSensor(WattBoxDevice, Entity):
    """Representation of a WattBox outlet, just on and off."""

    def __init__(self, controller, area_name, sensor_name, getter):
        """Initialize the light."""
        WattBoxDevice.__init__(self, area_name,
                               sensor_name,
                               sensor_name,
                               controller)
        self._prev = None
        self._getter = getter
        if sensor_name == 'power':
            self._unit_of_measurement = 'watt'
            self._device_class = 'power'
        elif sensor_name == 'current':
            self._unit_of_measurement = 'amp'
            self._device_class = 'power'
        elif sensor_name == 'voltage':
            self._unit_of_measurement = 'volt'
            self._device_class = 'voltage'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._getter(self._controller)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement for this sensor."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class for this sensor."""
        return self._device_class

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attr = {}
        attr['Host'] = self._controller.host
        return attr
