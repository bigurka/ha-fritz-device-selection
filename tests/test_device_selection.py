"""Tests for the network device selection of FRITZ!Box Tools."""

from freezegun.api import FrozenDateTimeFactory
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.fritz import async_remove_config_entry_device
from custom_components.fritz.const import (
    CONF_ADD_NEW_DEVICES,
    CONF_DESELECT_ALL,
    CONF_IGNORED_DEVICES,
    CONF_OLD_DISCOVERY,
    CONF_SELECT_ALL,
    CONF_TRACKED_DEVICES,
    DOMAIN,
    SCAN_INTERVAL,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import MOCK_USER_DATA

PRINTER_MAC = "AA:BB:CC:00:11:22"
SERVER_MAC = "AA:BB:CC:33:44:55"


def _tracker(entity_registry: er.EntityRegistry, mac: str) -> str | None:
    return entity_registry.async_get_entity_id(
        Platform.DEVICE_TRACKER, DOMAIN, f"{mac}_tracker"
    )


def _device(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry, mac: str
) -> dr.DeviceEntry | None:
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    return device_registry.async_get_device_by_connection(
        (dr.CONNECTION_NETWORK_MAC, dr.format_mac(mac)), entry.entry_id
    )


async def _setup(hass: HomeAssistant, options: dict | None = None) -> MockConfigEntry:
    # The flat hosts discovery lists both the printer and the server
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_USER_DATA,
        options={CONF_OLD_DISCOVERY: True, **(options or {})},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    return entry


async def test_default_tracks_all(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    fc_class_mock,
    fh_class_mock,
    fs_class_mock,
) -> None:
    """Without new options every device is tracked, as the original."""
    await _setup(hass)
    assert _tracker(entity_registry, PRINTER_MAC)
    assert _tracker(entity_registry, SERVER_MAC)


async def test_only_selected_devices(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    fc_class_mock,
    fh_class_mock,
    fs_class_mock,
) -> None:
    """With new devices disabled only the selected ones are tracked."""
    await _setup(
        hass,
        {
            CONF_ADD_NEW_DEVICES: False,
            CONF_TRACKED_DEVICES: [dr.format_mac(PRINTER_MAC)],
        },
    )
    assert _tracker(entity_registry, PRINTER_MAC)
    assert _device(hass, device_registry, PRINTER_MAC)
    assert _tracker(entity_registry, SERVER_MAC) is None
    assert _device(hass, device_registry, SERVER_MAC) is None


async def test_options_flow_deselect_removes_device(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    freezer: FrozenDateTimeFactory,
    fc_class_mock,
    fh_class_mock,
    fs_class_mock,
) -> None:
    """Deselecting a device in the options removes it with its entities."""
    entry = await _setup(hass)
    assert _tracker(entity_registry, SERVER_MAC)
    assert _device(hass, device_registry, SERVER_MAC)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    schema_keys = {str(key): key for key in result["data_schema"].schema}
    assert CONF_TRACKED_DEVICES in schema_keys
    offered = [
        option["value"]
        for option in result["data_schema"].schema[schema_keys[CONF_TRACKED_DEVICES]]
        .config["options"]
    ]
    assert dr.format_mac(PRINTER_MAC) in offered
    assert dr.format_mac(SERVER_MAC) in offered

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_TRACKED_DEVICES: [dr.format_mac(PRINTER_MAC)]},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert dr.format_mac(SERVER_MAC) in entry.options[CONF_IGNORED_DEVICES]
    assert dr.format_mac(PRINTER_MAC) in entry.options[CONF_TRACKED_DEVICES]

    freezer.tick(SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done(wait_background_tasks=True)

    assert _tracker(entity_registry, SERVER_MAC) is None
    assert _device(hass, device_registry, SERVER_MAC) is None
    assert _tracker(entity_registry, PRINTER_MAC)
    assert _device(hass, device_registry, PRINTER_MAC)


async def test_remove_device_from_ui(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    freezer: FrozenDateTimeFactory,
    fc_class_mock,
    fh_class_mock,
    fs_class_mock,
) -> None:
    """A device removed from the UI is excluded and not created again."""
    entry = await _setup(hass)
    server = _device(hass, device_registry, SERVER_MAC)
    assert server

    fritzbox = device_registry.async_get_device_by_identifier(
        (DOMAIN, entry.runtime_data.unique_id), entry.entry_id
    )
    assert fritzbox
    assert not await async_remove_config_entry_device(hass, entry, fritzbox)

    assert await async_remove_config_entry_device(hass, entry, server)
    device_registry.async_remove_device(server.id)
    await hass.async_block_till_done()
    assert dr.format_mac(SERVER_MAC) in entry.options[CONF_IGNORED_DEVICES]

    for _ in range(2):
        freezer.tick(SCAN_INTERVAL)
        async_fire_time_changed(hass)
        await hass.async_block_till_done(wait_background_tasks=True)

    assert _tracker(entity_registry, SERVER_MAC) is None
    assert _device(hass, device_registry, SERVER_MAC) is None
    assert _tracker(entity_registry, PRINTER_MAC)


async def test_options_no_list_without_devices(
    hass: HomeAssistant, fc_class_mock
) -> None:
    """Without a device list (entry not loaded) the form has no list."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_USER_DATA)
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
    schema_keys = {str(key) for key in result["data_schema"].schema}
    assert CONF_TRACKED_DEVICES not in schema_keys


async def test_options_flow_deselect_all(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    freezer: FrozenDateTimeFactory,
    fc_class_mock,
    fh_class_mock,
    fs_class_mock,
) -> None:
    """The deselect all box shows the list unticked without saving anything."""
    entry = await _setup(hass)
    options_before = dict(entry.options)
    printer, server = dr.format_mac(PRINTER_MAC), dr.format_mac(SERVER_MAC)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_DESELECT_ALL: True,
            CONF_ADD_NEW_DEVICES: False,
            CONF_TRACKED_DEVICES: [printer, server],
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert dict(entry.options) == options_before
    keys = {str(key): key for key in result["data_schema"].schema}
    assert keys[CONF_TRACKED_DEVICES].default() == []
    assert keys[CONF_DESELECT_ALL].default() is False
    assert keys[CONF_ADD_NEW_DEVICES].default() is False

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_ADD_NEW_DEVICES: False, CONF_TRACKED_DEVICES: [printer]},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert CONF_DESELECT_ALL not in entry.options
    assert entry.options[CONF_TRACKED_DEVICES] == [printer]
    assert entry.options[CONF_IGNORED_DEVICES] == [server]

    freezer.tick(SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done(wait_background_tasks=True)
    assert _tracker(entity_registry, SERVER_MAC) is None
    assert _tracker(entity_registry, PRINTER_MAC)


async def test_options_flow_select_all(
    hass: HomeAssistant,
    fc_class_mock,
    fh_class_mock,
    fs_class_mock,
) -> None:
    """The select all box shows the list ticked without saving anything."""
    printer, server = dr.format_mac(PRINTER_MAC), dr.format_mac(SERVER_MAC)
    entry = await _setup(
        hass, {CONF_ADD_NEW_DEVICES: False, CONF_TRACKED_DEVICES: [printer]}
    )
    options_before = dict(entry.options)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_SELECT_ALL: True, CONF_TRACKED_DEVICES: [printer]},
    )
    assert result["type"] is FlowResultType.FORM
    assert dict(entry.options) == options_before
    keys = {str(key): key for key in result["data_schema"].schema}
    assert set(keys[CONF_TRACKED_DEVICES].default()) == {printer, server}
    assert keys[CONF_SELECT_ALL].default() is False

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_TRACKED_DEVICES: [printer, server]},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert CONF_SELECT_ALL not in entry.options
    assert entry.options[CONF_TRACKED_DEVICES] == [printer, server]
    assert entry.options[CONF_IGNORED_DEVICES] == []


async def test_options_flow_deselect_wins_over_select_all(
    hass: HomeAssistant,
    fc_class_mock,
    fh_class_mock,
    fs_class_mock,
) -> None:
    """With both boxes ticked the list is shown unticked."""
    entry = await _setup(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_DESELECT_ALL: True, CONF_SELECT_ALL: True},
    )
    assert result["type"] is FlowResultType.FORM
    keys = {str(key): key for key in result["data_schema"].schema}
    assert keys[CONF_TRACKED_DEVICES].default() == []
