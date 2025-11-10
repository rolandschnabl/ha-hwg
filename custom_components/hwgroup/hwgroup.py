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
                data = self._parse_xml_data(xml_data)
                
                # For SMS Gateway, also fetch status.xml for additional sensors
                if data["device_info"].get("device_type") == "sms_gateway":
                    try:
                        async with self.session.get(
                            f"{self.base_url}/status.xml",
                            auth=self._auth,
                            timeout=self.timeout,
                        ) as status_response:
                            if status_response.status == 200:
                                status_xml = await status_response.text()
                                self._parse_sms_gateway_status(status_xml, data)
                    except Exception as err:
                        _LOGGER.debug("Could not fetch SMS Gateway status: %s", err)
                
                _LOGGER.info("Parsed data: %d sensors, %d binary_sensors, %d switches", 
                            len(data["sensors"]), len(data["binary_sensors"]), len(data["switches"]))
                return data
        except aiohttp.ClientError as err:
            raise HWGroupConnectionError(f"Connection error: {err}") from err
        except asyncio.TimeoutError as err:
            raise HWGroupConnectionError("Connection timeout") from err

    def _parse_xml_data(self, xml_data: str) -> dict[str, Any]:
        """Parse XML data from the device."""
        try:
            _LOGGER.debug("Parsing XML data: %s", xml_data[:500])  # Log first 500 chars
            root = ElementTree.fromstring(xml_data)
            
            # Handle XML namespace (Poseidon devices)
            namespace = {"val": "http://www.etech.cz/XMLSchema/poseidon/values.xsd"}
            
            data = {
                "device_info": {},
                "sensors": [],
                "binary_sensors": [],
                "switches": [],
            }

            # Parse device information from Agent element
            # Poseidon devices use different structure than SMS Gateway
            agent = root.find(".//Agent") or root.find(".//val:Agent", namespace)
            if agent is not None:
                device_name = agent.find("DeviceName")
                version = agent.find("Version")
                title = agent.find("Title")
                product_name = agent.find("ProductName")
                serial = agent.find("SerialNumber")
                model = agent.find("Model")
                
                # Handle both Poseidon (uses Title) and SMS Gateway (uses ProductName)
                if title is not None:
                    model_text = title.text
                elif product_name is not None:
                    model_text = product_name.text
                else:
                    model_text = "Unknown"
                
                data["device_info"] = {
                    "name": device_name.text if device_name is not None else (model_text if product_name is not None else "HW Group Device"),
                    "version": version.text if version is not None else "Unknown",
                    "model": model_text,
                    "serial": serial.text if serial is not None else "Unknown",
                    "device_type": self._detect_device_type(model_text),
                }
            _LOGGER.debug("Device info: %s", data["device_info"])

            # Parse sensors from SenSet (temperature, humidity, etc.)
            senset = root.find(".//SenSet") or root.find(".//val:SenSet", namespace)
            if senset is not None:
                for sensor in senset.findall("Entry"):
                    sensor_data = self._parse_sensor(sensor)
                    if sensor_data:
                        _LOGGER.debug("Found sensor: %s", sensor_data)
                        data["sensors"].append(sensor_data)

            # Parse binary inputs from BinaryInSet (contacts, alarms)
            binaryset = root.find(".//BinaryInSet") or root.find(".//val:BinaryInSet", namespace)
            if binaryset is not None:
                for binary in binaryset.findall("Entry"):
                    binary_data = self._parse_binary_sensor(binary)
                    if binary_data:
                        _LOGGER.debug("Found binary sensor: %s", binary_data)
                        data["binary_sensors"].append(binary_data)

            # Parse outputs/relays (if device has them)
            outputset = root.find(".//OutputSet") or root.find(".//val:OutputSet", namespace)
            if outputset is not None:
                for output in outputset.findall("Entry"):
                    output_data = self._parse_output(output)
                    if output_data:
                        _LOGGER.debug("Found switch: %s", output_data)
                        data["switches"].append(output_data)

            return data

        except ElementTree.ParseError as err:
            raise HWGroupError(f"Failed to parse XML data: {err}") from err

    def _parse_sensor(self, sensor: ElementTree.Element) -> dict[str, Any] | None:
        """Parse a sensor element from Entry."""
        try:
            id_elem = sensor.find("ID")
            name_elem = sensor.find("Name")
            value_elem = sensor.find("Value")
            unit_elem = sensor.find("Units")
            state_elem = sensor.find("State")

            if id_elem is None or value_elem is None:
                return None

            sensor_id = id_elem.text
            name = name_elem.text if name_elem is not None else f"Sensor {sensor_id}"
            
            # Get the value and handle different formats
            sensor_value = value_elem.text
            if sensor_value:
                try:
                    sensor_value = float(sensor_value)
                except ValueError:
                    pass

            unit_text = unit_elem.text if unit_elem is not None else ""
            
            return {
                "id": sensor_id,
                "name": name,
                "value": sensor_value,
                "unit": unit_text,
                "state": state_elem.text if state_elem is not None else "0",
                "type": self._determine_sensor_type(unit_text),
            }
        except (AttributeError, ValueError) as err:
            _LOGGER.debug("Failed to parse sensor: %s", err)
            return None

    def _parse_binary_sensor(self, binary: ElementTree.Element) -> dict[str, Any] | None:
        """Parse a binary sensor element from Entry."""
        try:
            id_elem = binary.find("ID")
            name_elem = binary.find("Name")
            value_elem = binary.find("Value")
            state_elem = binary.find("State")

            if id_elem is None or value_elem is None:
                return None

            binary_id = id_elem.text
            name = name_elem.text if name_elem is not None else f"Input {binary_id}"
            
            # Value indicates the current state (0/1)
            value_text = value_elem.text
            is_on = value_text == "1" if value_text else False

            return {
                "id": binary_id,
                "name": name,
                "state": is_on,
                "alarm_state": state_elem.text if state_elem is not None else "0",
                "type": "contact",
            }
        except (AttributeError, ValueError) as err:
            _LOGGER.debug("Failed to parse binary sensor: %s", err)
            return None

    def _parse_output(self, output: ElementTree.Element) -> dict[str, Any] | None:
        """Parse an output/relay element from Entry."""
        try:
            id_elem = output.find("ID")
            name_elem = output.find("Name")
            value_elem = output.find("Value")

            if id_elem is None or value_elem is None:
                return None

            output_id = id_elem.text
            name = name_elem.text if name_elem is not None else f"Output {output_id}"
            
            # Value indicates the current state (0/1)
            value_text = value_elem.text
            is_on = value_text == "1" if value_text else False

            return {
                "id": output_id,
                "name": name,
                "state": is_on,
            }
        except (AttributeError, ValueError) as err:
            _LOGGER.debug("Failed to parse output: %s", err)
            return None

    def _determine_sensor_type(self, unit: str) -> str:
        """Determine sensor type from unit."""
        unit_lower = unit.lower()
        if "c" == unit_lower or "°c" in unit_lower or "celsius" in unit_lower or "°f" in unit_lower or "f" == unit_lower:
            return "temperature"
        if "%" in unit_lower or "rh" in unit_lower:
            return "humidity"
        if "v" == unit_lower or "volt" in unit_lower:
            return "voltage"
        if "a" == unit_lower or "amp" in unit_lower or "ma" in unit_lower:
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
        
        # Check for SMS Gateway first (most specific)
        if "sms" in model_lower or "hwg-sms" in model_lower:
            return DEVICE_TYPE_SMS_GATEWAY
        
        # Check for Poseidon 3268
        if "3268" in model_lower or "poseidon2 3268" in model_lower:
            return DEVICE_TYPE_POSEIDON_3268
        
        # Check for Poseidon 3266
        if "3266" in model_lower or "poseidon2 3266" in model_lower or "poseidon2 model 3266" in model_lower:
            return DEVICE_TYPE_POSEIDON_3266
        
        # Default to 3268 if unknown
        _LOGGER.warning("Unknown device model '%s', defaulting to Poseidon 3268", model)
        return DEVICE_TYPE_POSEIDON_3268

    def _parse_sms_gateway_status(self, status_xml: str, data: dict[str, Any]) -> None:
        """Parse SMS Gateway status.xml and add sensors to data."""
        try:
            root = ElementTree.fromstring(status_xml)
            
            # Parse signal quality
            signal_dbm = root.find("ModemSigQ")
            if signal_dbm is not None and signal_dbm.text:
                # Extract numeric value from "-75 dBm (61 %)" format
                dbm_text = signal_dbm.text
                if "dBm" in dbm_text:
                    dbm_value = dbm_text.split("dBm")[0].strip()
                    try:
                        data["sensors"].append({
                            "id": "signal_strength",
                            "name": "Signal Strength",
                            "value": float(dbm_value),
                            "unit": "dBm",
                            "state": "0",
                            "type": "signal_strength",
                        })
                    except ValueError:
                        pass
                    
                    # Also extract percentage
                    if "(" in dbm_text and "%" in dbm_text:
                        percent_text = dbm_text.split("(")[1].split("%")[0].strip()
                        try:
                            data["sensors"].append({
                                "id": "signal_quality",
                                "name": "Signal Quality",
                                "value": float(percent_text),
                                "unit": "%",
                                "state": "0",
                                "type": "generic",
                            })
                        except ValueError:
                            pass
            
            # Parse network operator
            net_op = root.find("ModemNetOp")
            if net_op is not None and net_op.text and net_op.text.strip():
                data["sensors"].append({
                    "id": "network_operator",
                    "name": "Network Operator",
                    "value": net_op.text.strip(),
                    "unit": "",
                    "state": "0",
                    "type": "generic",
                })
            
            # Parse network registration status
            net_reg = root.find("ModemNetReg")
            if net_reg is not None and net_reg.text and net_reg.text.strip():
                data["sensors"].append({
                    "id": "network_status",
                    "name": "Network Status",
                    "value": net_reg.text.strip(),
                    "unit": "",
                    "state": "0",
                    "type": "generic",
                })
            
            # Parse SMS statistics
            sms_ok = root.find("CntSmsOK")
            if sms_ok is not None and sms_ok.text:
                try:
                    data["sensors"].append({
                        "id": "sms_sent",
                        "name": "SMS Sent",
                        "value": int(sms_ok.text),
                        "unit": "",
                        "state": "0",
                        "type": "generic",
                    })
                except ValueError:
                    pass
            
            sms_error = root.find("CntSmsError")
            if sms_error is not None and sms_error.text:
                try:
                    data["sensors"].append({
                        "id": "sms_errors",
                        "name": "SMS Errors",
                        "value": int(sms_error.text),
                        "unit": "",
                        "state": "0",
                        "type": "generic",
                    })
                except ValueError:
                    pass
            
            _LOGGER.debug("Added SMS Gateway status sensors: %d total sensors", len(data["sensors"]))
            
        except ElementTree.ParseError as err:
            _LOGGER.debug("Failed to parse SMS Gateway status XML: %s", err)

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

    async def async_send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS via SMS Gateway using HTTP GET method."""
        try:
            # URL encode the message text
            import urllib.parse
            encoded_text = urllib.parse.quote(message)
            
            # Send SMS using HTTP GET
            url = f"{self.base_url}/values.xml?Cmd=SMS&Nmr={phone_number}&Text={encoded_text}"
            
            async with self.session.get(
                url,
                auth=self._auth,
                timeout=self.timeout,
            ) as response:
                if response.status == 200:
                    xml_response = await response.text()
                    # Check if SMS was queued successfully
                    # Response should contain <Rslt>1</Rslt>
                    if "<Rslt>1</Rslt>" in xml_response:
                        _LOGGER.info("SMS sent successfully to %s", phone_number)
                        return True
                    else:
                        _LOGGER.error("SMS failed: %s", xml_response)
                        return False
                else:
                    _LOGGER.error("HTTP error %s when sending SMS", response.status)
                    return False
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Failed to send SMS: %s", err)
            return False

    async def async_call_number(self, phone_number: str) -> bool:
        """Ring a phone number via SMS Gateway using HTTP GET method."""
        try:
            # Ring using HTTP GET
            url = f"{self.base_url}/values.xml?Cmd=Call&Nmr={phone_number}"
            
            async with self.session.get(
                url,
                auth=self._auth,
                timeout=self.timeout,
            ) as response:
                if response.status == 200:
                    xml_response = await response.text()
                    # Check if call was queued successfully
                    if "<Rslt>1</Rslt>" in xml_response:
                        _LOGGER.info("Call initiated successfully to %s", phone_number)
                        return True
                    else:
                        _LOGGER.error("Call failed: %s", xml_response)
                        return False
                else:
                    _LOGGER.error("HTTP error %s when calling number", response.status)
                    return False
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Failed to call number: %s", err)
            return False
