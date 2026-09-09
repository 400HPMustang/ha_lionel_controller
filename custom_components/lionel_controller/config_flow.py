"""Config flow for Lionel Train Controller integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_MAC_ADDRESS,
    CONF_TRAIN_MODEL,
    DEFAULT_NAME,
    DOMAIN,
    LIONCHIEF_SERVICE_UUID,
)
from .train_models import TRAIN_MODEL_OPTIONS

_LOGGER = logging.getLogger(__name__)

STEP_MANUAL_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC_ADDRESS): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)

MANUAL_ENTRY = "__manual_entry__"


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate a manually entered train address using Home Assistant Bluetooth."""
    mac_address = data[CONF_MAC_ADDRESS].upper()

    if not _is_valid_mac_address(mac_address):
        raise InvalidMacAddress

    # Do not start a second Bleak scanner. Home Assistant's Bluetooth integration
    # already maintains discovery data across local adapters and ESPHome proxies.
    ble_device = bluetooth.async_ble_device_from_address(
        hass, mac_address, connectable=True
    )
    if ble_device is None:
        raise CannotConnect

    return {
        "title": data[CONF_NAME],
        CONF_MAC_ADDRESS: mac_address,
    }


def _is_valid_mac_address(mac: str) -> bool:
    """Return True when the Bluetooth address is a colon-separated MAC."""
    parts = mac.split(":")
    if len(parts) != 6:
        return False

    for part in parts:
        if len(part) != 2:
            return False
        try:
            int(part, 16)
        except ValueError:
            return False

    return True


def _is_lionel_service_info(service_info: BluetoothServiceInfoBleak) -> bool:
    """Return True for a likely LionChief advertisement."""
    service_match = any(
        service_uuid.lower() == LIONCHIEF_SERVICE_UUID.lower()
        for service_uuid in service_info.service_uuids
    )
    name_match = (service_info.name or "").upper().startswith("LC")
    return service_match or name_match


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lionel Train Controller."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}
        self._scanned_devices: dict[str, dict[str, Any]] = {}
        self._pending_device: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select a train already known to HA Bluetooth or enter it manually."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected = user_input.get("device")

            if selected == MANUAL_ENTRY:
                return await self.async_step_manual()

            if selected and selected in self._scanned_devices:
                device_info = self._scanned_devices[selected]

                await self.async_set_unique_id(device_info[CONF_MAC_ADDRESS])
                self._abort_if_unique_id_configured()

                self._pending_device = {
                    CONF_MAC_ADDRESS: device_info[CONF_MAC_ADDRESS],
                    CONF_NAME: device_info[CONF_NAME],
                }
                return await self.async_step_train_model()

        if not self._scanned_devices:
            self._async_find_cached_trains()

        device_options = {
            mac: f"{info[CONF_NAME]} ({mac})"
            for mac, info in self._scanned_devices.items()
        }
        device_options[MANUAL_ENTRY] = "Enter MAC address manually..."

        if not self._scanned_devices:
            errors["base"] = "no_devices_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("device"): vol.In(device_options)}),
            errors=errors,
        )

    def _async_find_cached_trains(self) -> None:
        """Populate discovered trains from Home Assistant's Bluetooth cache."""
        self._scanned_devices = {}

        for service_info in bluetooth.async_discovered_service_info(
            self.hass, connectable=True
        ):
            if not _is_lionel_service_info(service_info):
                continue

            mac = service_info.address.upper()
            if self._is_already_configured(mac):
                continue

            device_name = service_info.name or f"Lionel Train {mac[-5:].replace(':', '')}"
            self._scanned_devices[mac] = {
                CONF_MAC_ADDRESS: mac,
                CONF_NAME: device_name,
            }
            _LOGGER.debug("Found Lionel train in HA Bluetooth cache: %s at %s", device_name, mac)

    def _is_already_configured(self, mac_address: str) -> bool:
        """Check if a device is already configured."""
        return any(
            entry.data.get(CONF_MAC_ADDRESS, "").upper() == mac_address.upper()
            for entry in self._async_current_entries()
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual MAC address entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidMacAddress:
                errors[CONF_MAC_ADDRESS] = "invalid_mac"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception validating Lionel train")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info[CONF_MAC_ADDRESS])
                self._abort_if_unique_id_configured()

                self._pending_device = {
                    CONF_MAC_ADDRESS: info[CONF_MAC_ADDRESS],
                    CONF_NAME: info["title"],
                }
                return await self.async_step_train_model()

        return self.async_show_form(
            step_id="manual",
            data_schema=STEP_MANUAL_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_train_model(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle train model selection."""
        if self._pending_device is None:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            train_model = user_input.get(CONF_TRAIN_MODEL, "Generic")
            return self.async_create_entry(
                title=self._pending_device[CONF_NAME],
                data={
                    **self._pending_device,
                    CONF_TRAIN_MODEL: train_model,
                },
            )

        model_options = {model: model for model in TRAIN_MODEL_OPTIONS}
        return self.async_show_form(
            step_id="train_model",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TRAIN_MODEL, default="Generic"): vol.In(
                        model_options
                    ),
                }
            ),
            description_placeholders={"name": self._pending_device[CONF_NAME]},
        )

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle Bluetooth discovery from the manifest matcher."""
        mac_address = discovery_info.address.upper()
        await self.async_set_unique_id(mac_address)
        self._abort_if_unique_id_configured()

        if not _is_lionel_service_info(discovery_info):
            return self.async_abort(reason="not_lionel_device")

        self._discovered_devices[mac_address] = discovery_info
        self.context["title_placeholders"] = {
            "name": discovery_info.name or f"Lionel Train ({mac_address[-5:]})"
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm a Bluetooth-discovered train."""
        discovery_info = self._discovered_devices[self.unique_id]
        mac_address = discovery_info.address.upper()
        device_name = discovery_info.name or f"Lionel Train {mac_address[-5:].replace(':', '')}"

        if user_input is not None:
            self._pending_device = {
                CONF_MAC_ADDRESS: mac_address,
                CONF_NAME: device_name,
            }
            return await self.async_step_train_model()

        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": device_name,
                "address": mac_address,
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate the train is not currently reachable."""


class InvalidMacAddress(HomeAssistantError):
    """Error to indicate an invalid MAC address."""
