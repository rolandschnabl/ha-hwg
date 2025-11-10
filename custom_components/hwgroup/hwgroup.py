"""HW Group API Client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from xml.etree import ElementTree

import aiohttp

_LOGGER = logging.getLogger(__name__)


class HWGroupError(Exception):
    """Base exception for HW Group errors."""


class HWGroupConnectionError(HWGroupError):
    """Exception for connection errors."""


class HWGroupAuthError(HWGroupError):
    """Exception for authentication errors."""


class HWGroupAPI:
    """API client for HW Group devices."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        username: str | None = None,
        password: str | None = None,
        port: int = 80,
        timeout: int = 10,
    ) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.session = session
        self.username = username
        self.password = password
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._auth = None
        if username and password:
            self._auth = aiohttp.BasicAuth(username, password)

    @property
    def base_url(self) -> str:
        """Return the base URL for the device."""
        return f"http://{self.host}:{self.port}"

    async def async_get_data(self) -> dict[str, Any]:
        """Get data from the device."""
        try:
            # HW Group devices typically use XML API
            async with self.session.get(
                f"{self.base_url}/values.xml",
                auth=self._auth,
                timeout=self.timeout,
            ) as response:
                if response.status == 401:
                    raise HWGroupAuthError("Authentication failed")
                if response.status != 200:
                    raise HWGroupConnectionError(
                        f"HTTP error {response.status}"
                    )
                
                xml_data = await response.text()
                return self._parse_xml_data(xml_data)
        except aiohttp.ClientError as err:
            raise HWGroupConnectionError(f"Connection error: {err}") from err
        except asyncio.TimeoutError as err:
            raise HWGroupConnectionError("Connection timeout") from err

    def _parse_xml_data(self, xml_data: str) -> dict[str, Any]:
        """Parse XML data from the device."""
        try:
            _LOGGER.debug("Parsing XML data: %s", xml_data[:500])  # Log first 500 chars
            root = ElementTree.fromstring(xml_data)
            data = {
                "device_info": {},
                "sensors": [],
                "binary_sensors": [],
                "switches": [],
            }

            # Parse device information
            agent = root.find(".//agent")
            if agent is not None:
                model = agent.get("model", "Unknown")
                data["device_info"] = {
                    "name": agent.get("name", "HW Group Device"),
                    "version": agent.get("version", "Unknown"),
                    "model": model,
                    "serial": agent.get("serialNumber", "Unknown"),
                    "device_type": self._detect_device_type(model),
                }
            _LOGGER.debug("Device info: %s", data["device_info"])

            # Parse sensors (temperature, humidity, etc.)
            for sensor in root.findall(".//entry"):
                sensor_data = self._parse_sensor(sensor)
                if sensor_data:
                    _LOGGER.debug("Found sensor: %s", sensor_data)
                    data["sensors"].append(sensor_data)

            # Parse binary inputs (contacts, alarms)
            for binary in root.findall(".//input"):
                binary_data = self._parse_binary_sensor(binary)
                if binary_data:
                    _LOGGER.debug("Found binary sensor: %s", binary_data)
                    data["binary_sensors"].append(binary_data)

            # Parse outputs/relays
            for output in root.findall(".//output"):
                output_data = self._parse_output(output)
                if output_data:
                    _LOGGER.debug("Found switch: %s", output_data)
                    data["switches"].append(output_data)

            _LOGGER.info("Parsed data: %d sensors, %d binary_sensors, %d switches", 
                        len(data["sensors"]), len(data["binary_sensors"]), len(data["switches"]))
            return data

        except ElementTree.ParseError as err:
            raise HWGroupError(f"Failed to parse XML data: {err}") from err

    def _parse_sensor(self, sensor: ElementTree.Element) -> dict[str, Any] | None:
        """Parse a sensor element."""
        try:
            sensor_id = sensor.get("id")
            name = sensor.get("name", f"Sensor {sensor_id}")
            value = sensor.find("value")
            unit = sensor.find("unit")
            state = sensor.find("state")

            if value is None:
                return None

            # Get the value and handle different formats
            sensor_value = value.text
            if sensor_value:
                try:
                    sensor_value = float(sensor_value)
                except ValueError:
                    pass

            return {
                "id": sensor_id,
                "name": name,
                "value": sensor_value,
                "unit": unit.text if unit is not None else None,
                "state": state.text if state is not None else "ok",
                "type": self._determine_sensor_type(unit.text if unit is not None else ""),
            }
        except (AttributeError, ValueError) as err:
            _LOGGER.debug("Failed to parse sensor: %s", err)
            return None

    def _parse_binary_sensor(self, binary: ElementTree.Element) -> dict[str, Any] | None:
        """Parse a binary sensor element."""
        try:
            binary_id = binary.get("id")
            name = binary.get("name", f"Input {binary_id}")
            state = binary.find("state")

            if state is None:
                return None

            return {
                "id": binary_id,
                "name": name,
                "state": state.text.lower() in ("1", "true", "on", "active"),
                "type": "contact",
            }
        except (AttributeError, ValueError) as err:
            _LOGGER.debug("Failed to parse binary sensor: %s", err)
            return None

    def _parse_output(self, output: ElementTree.Element) -> dict[str, Any] | None:
        """Parse an output/relay element."""
        try:
            output_id = output.get("id")
            name = output.get("name", f"Output {output_id}")
            state = output.find("state")

            if state is None:
                return None

            return {
                "id": output_id,
                "name": name,
                "state": state.text.lower() in ("1", "true", "on", "active"),
            }
        except (AttributeError, ValueError) as err:
            _LOGGER.debug("Failed to parse output: %s", err)
            return None

    def _determine_sensor_type(self, unit: str) -> str:
        """Determine sensor type from unit."""
        unit_lower = unit.lower()
        if "°c" in unit_lower or "celsius" in unit_lower or "°f" in unit_lower:
            return "temperature"
        if "%" in unit_lower or "rh" in unit_lower:
            return "humidity"
        if "v" == unit_lower or "volt" in unit_lower:
            return "voltage"
        if "a" == unit_lower or "amp" in unit_lower:
            return "current"
        return "generic"

    def _detect_device_type(self, model: str) -> str:
        """Detect device type from model string."""
        from .const import (
            DEVICE_TYPE_POSEIDON_3268,
            DEVICE_TYPE_POSEIDON_3266,
            DEVICE_TYPE_SMS_GATEWAY,
        )
        
        model_lower = model.lower()
        
        # Check for Poseidon 3268
        if "3268" in model_lower or "poseidon2 3268" in model_lower:
            return DEVICE_TYPE_POSEIDON_3268
        
        # Check for Poseidon 3266
        if "3266" in model_lower or "poseidon2 3266" in model_lower:
            return DEVICE_TYPE_POSEIDON_3266
        
        # Check for SMS Gateway
        if "sms" in model_lower or "gateway" in model_lower:
            return DEVICE_TYPE_SMS_GATEWAY
        
        # Default to 3268 if unknown
        _LOGGER.warning("Unknown device model '%s', defaulting to Poseidon 3268", model)
        return DEVICE_TYPE_POSEIDON_3268

    async def async_test_connection(self) -> bool:
        """Test the connection to the device."""
        try:
            await self.async_get_data()
            return True
        except HWGroupError:
            return False

    async def async_set_output(self, output_id: str, state: bool) -> bool:
        """Set the state of an output/relay."""
        try:
            # Command to set output state
            state_value = "1" if state else "0"
            async with self.session.get(
                f"{self.base_url}/output.xml?id={output_id}&state={state_value}",
                auth=self._auth,
                timeout=self.timeout,
            ) as response:
                return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Failed to set output state: %s", err)
            return False
