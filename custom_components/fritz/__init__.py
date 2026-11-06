"""Support for AVM Fritz!Box functions."""
# Modified by bigurka from Home Assistant Core 2026.11.0: network device selection.

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_FEATURE_DEVICE_TRACKING,
    DEFAULT_CONF_FEATURE_DEVICE_TRACKING,
    DEFAULT_SSL,
    DOMAIN,
    FRITZ_AUTH_EXCEPTIONS,
    FRITZ_EXCEPTIONS,
    LOGGER,
    PLATFORMS,
)
from .coordinator import FRITZ_DATA_KEY, AvmWrapper, FritzConfigEntry, FritzData
from .services import async_setup_services

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up fritzboxtools integration."""
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: FritzConfigEntry) -> None:
    """Set up fritzboxtools from config entry."""
    LOGGER.debug("Setting up FRITZ!Box Tools component")

    avm_wrapper = AvmWrapper(
        hass=hass,
        config_entry=entry,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        use_tls=entry.data.get(CONF_SSL, DEFAULT_SSL),
        device_discovery_enabled=entry.options.get(
            CONF_FEATURE_DEVICE_TRACKING, DEFAULT_CONF_FEATURE_DEVICE_TRACKING
        ),
    )

    hass.data.setdefault(FRITZ_DATA_KEY, FritzData())

    try:
        await avm_wrapper.async_setup(entry.options)
    except FRITZ_AUTH_EXCEPTIONS as ex:
        raise ConfigEntryAuthFailed from ex
    except FRITZ_EXCEPTIONS as ex:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="error_connecting",
            translation_placeholders={"error": str(ex)},
        ) from ex

    if "X_AVM-DE_UPnP1" in avm_wrapper.connection.services and not (
        await avm_wrapper.async_get_upnp_configuration()
    ).get("NewEnable"):
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="error_upnp_disabled",
        )

    await avm_wrapper.async_config_entry_first_refresh()

    entry.runtime_data = avm_wrapper

    # Load the other platforms like switch
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)


async def async_unload_entry(hass: HomeAssistant, entry: FritzConfigEntry) -> None:
    """Unload FRITZ!Box Tools config entry."""
    avm_wrapper = entry.runtime_data

    fritz_data = hass.data[FRITZ_DATA_KEY]

    if avm_wrapper.unique_id in fritz_data.tracked:
        fritz_data.tracked.pop(avm_wrapper.unique_id)
        fritz_data.profile_switches.pop(avm_wrapper.unique_id)
        fritz_data.wol_buttons.pop(avm_wrapper.unique_id)

    if not bool(fritz_data.tracked):
        hass.data.pop(FRITZ_DATA_KEY)

    await hass.config_entries.async_unload_platforms_or_raise(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: FritzConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove a network device and exclude it from being added again."""
    avm_wrapper = entry.runtime_data

    # The FRITZ!Box itself can only be removed together with the integration
    if (DOMAIN, avm_wrapper.unique_id) in device_entry.identifiers:
        return False

    for connection_type, mac in device_entry.connections:
        if connection_type == dr.CONNECTION_NETWORK_MAC:
            LOGGER.debug("Exclude device %s [%s]", device_entry.name, mac)
            avm_wrapper.async_exclude_device(mac)

    return True
