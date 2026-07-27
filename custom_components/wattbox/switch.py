"""
Component for interacting with a WattBox(tm) (SnapAV) - brand
ip-controlled power strip.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/wattbox/
"""
import logging

from homeassistant.components.switch import SwitchEntity
from ..wattbox import WattBoxDevice, DEVICES

_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the wattbox power strip switches."""
    devs = []
    for (area_name, device, wattbox) in hass.data[DEVICES]['switch']:
        dev = WattBoxSwitch(area_name, device, wattbox)
        devs.append(dev)

    add_devices(devs, True)
    _LOGGER.debug("Added %s", devs)
    return True


class WattBoxSwitch(WattBoxDevice, SwitchEntity):
    """Representation of a WattBox outlet, just on and off."""

    def __init__(self, area_name, wattbox_switch, controller):
        """Initialize the light."""
        WattBoxDevice.__init__(self, area_name,
                               wattbox_switch.name,
                               wattbox_switch.outlet_num,
                               controller)
        self._wattbox_switch = wattbox_switch
        self._prev = None

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._wattbox_switch.set_state(True)
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the light off."""
        self._wattbox_switch.set_state(False)
        self.schedule_update_ha_state()

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._wattbox_switch.is_on

    def update(self):
        """Call when forcing a refresh of the device."""
        if self._wattbox_switch._update():
            self.schedule_update_has_state()

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attr = {}
        attr['Host'] = self._controller.host
        attr['Outlet'] = self.unique_id
        return attr
