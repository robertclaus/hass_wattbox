"""
Component for interacting with a WattBox(tm) (SnapAV) - brand
ip-controlled power strip.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/wattbox/
"""
import asyncio
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_HOST, CONF_USERNAME,
                                 CONF_PASSWORD, CONF_DEVICES)
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity

DOMAIN = 'wattbox'
DEVICES = 'wattbox_devices'

_LOGGER = logging.getLogger(__name__)

CONF_AREA = 'area'
CONF_SWITCH_NOOP = 'switch_noop'
CONF_EXCLUDE_NAME_SUBSTRING = 'exclude_name_substring'

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_AREA): cv.string,
    vol.Optional(CONF_SWITCH_NOOP): cv.boolean,
    vol.Optional(CONF_EXCLUDE_NAME_SUBSTRING): cv.string,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA])
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the WattBox component."""
    from pywattbox import WattBox

    wattboxes = []

    hass.data[DEVICES] = {'switch': [], 'sensor': []}

    for wb_config in config[DOMAIN][CONF_DEVICES]:
        host = wb_config.get(CONF_HOST)
        username = wb_config.get(CONF_USERNAME)
        password = wb_config.get(CONF_PASSWORD)
        area = wb_config.get(CONF_AREA)
        noop = wb_config.get(CONF_SWITCH_NOOP)
        exclude_name_substring = wb_config.get(CONF_EXCLUDE_NAME_SUBSTRING)
        set_exclude_name_substring = set()

        if exclude_name_substring:
            set_exclude_name_substring = set(exclude_name_substring.split(","))

        def is_excluded_name(entity):
            for ns in set_exclude_name_substring:
                if ns in entity.name:
                    _LOGGER.debug(
                        "skipping %s because exclude_name_substring has %s",
                        entity, ns)
                    return True
            return False

        try:
            wattbox = WattBox(host, username, password, area, noop)
            wattboxes.append(wattbox)
            wattbox.load_xml()
            _LOGGER.info("Loaded config from Wattbox at %s", host)
            for switch in wattbox.switches:
                if not is_excluded_name(switch):
                    _LOGGER.info("adding switch %s (%s)", switch, str(wattbox))
                    hass.data[DEVICES]['switch'].append(
                        (area, switch, wattbox))
            hass.data[DEVICES]['sensor'].append((area, wattbox))
        except Exception as e:
            _LOGGER.error("Could not setup wattbox at %s - %s", host, e)

    hass.data[DOMAIN] = wattboxes

    discovery.load_platform(hass, 'switch', DOMAIN, None, config)
    discovery.load_platform(hass, 'sensor', DOMAIN, None, config)

    return True


# The only device type now is a switch but we keep this here anyway
class WattBoxDevice(Entity):
    """Representation of a wattbox device entity."""

    # pylint: disable=protected-access
    def __init__(self, area_name, device_name, unique_name, controller):
        """Initialize the device."""
        self._area_name = area_name
        self._device_name = device_name
        self._controller = controller
        self._unique_id = 'wattbox-{}-{}'.format(controller._serial_number,
                                                 unique_name)

    def async_added_to_hass(self):
        """Register callbacks."""

    def _update_callback(self, _switch):
        """Run when invoked by pywattbox when the device state changes."""
        self.schedule_update_ha_state()

    @property
    def name(self):
        """Return the name of the device."""
        return "{} {}".format(self._area_name, self._device_name)

    @property
    def should_poll(self):
        """Polling is needed."""
        return True

    @property
    def unique_id(self):
        """Unique ID of wattbox device.
Uses serial number and outlet number."""
        return self._unique_id
