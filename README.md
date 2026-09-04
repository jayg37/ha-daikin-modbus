# Daikin Modbus Home Assistant integration

Home Assistant integration for Daikin/Airzone Aidoo Modbus devices using the shared `modbus_connection` infrastructure.

This repository is maintained as the proposed Home Assistant core integration. The device-specific protocol implementation lives in the separate `daikin-modbus` Python package.

## Architecture

```text
Home Assistant
      │
      │ shared modbus_connection
      ▼
Daikin integration
      │
      ▼
daikin-modbus device model
      │
      ▼
EW11 / Modbus TCP → RTU gateway
      │
      ▼
Airzone Aidoo
      │
      ▼
Daikin
```

The integration does not create its own Modbus client. It selects a `modbus_connection` entry and borrows the requested unit, following the current Home Assistant Modbus integration pattern.

## Setup

1. Configure the Modbus TCP connection in Home Assistant using the `modbus_connection` integration.
2. Add **Daikin Modbus** from Devices & services.
3. Select the shared Modbus connection.
4. Enter the Aidoo unit ID (default `1`).

## Entity scope

The first implementation provides a climate entity for the verified controls: power, setpoint, HVAC mode, and numeric fan speed. Additional registers are present in the device library and are exposed as read-only diagnostic sensors only where useful. Unverified registers are never written by this integration.

Temperatures are represented in Fahrenheit to match the tested installation and the standalone device model.

## Development

This repository mirrors the structure and conventions of the Trovis Modbus integration example used by Home Assistant's new Modbus architecture. It is intended to become a contribution to Home Assistant core rather than a forever-independent custom integration.

## Dependency

The integration requires the released `daikin-modbus` package. Until that package is published, development can use a local editable dependency or the vendorized HACS repository.
