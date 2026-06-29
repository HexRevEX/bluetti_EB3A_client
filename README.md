# Bluetti EB3A Status Monitor/State Changer

A simple Python script for monitoring the status of a **Bluetti EB3A** power station over Bluetooth Low Energy (BLE).

## Features

- Read the current status of the Bluetti EB3A
- Connect to the power station via BLE
- Easy configuration using a JSON file

## Configuration

All application settings are stored in the `settings.json` file.

### Settings

| Parameter | Description |
|-----------|-------------|
| `station_mac` | BLE MAC address of your Bluetti EB3A power station. Replace this value with the MAC address of your own device. |

Example:

```json
{
    "station_mac": "AA:BB:CC:DD:EE:FF"
    "station_output_uuid": "0000ff01-0000-1000-8000-00805f9b34fb",
    "station_input_uuid": "0000ff02-0000-1000-8000-00805f9b34fb",
    "enable_DC": "01060bc000014a12",
    "disable_DC": "01060bc000008bd2",
    "enable_AC": "01060bbf00017bca",
    "disable_AC": "01060bbf0000ba0a",
    "enable_Power_lifting": "01060bfa00016a1f",
    "disable_Power_lifting": "01060bfa0000abdf",
    "enable_Eco_mode": "01060bf70001fbdc",
    "disable_Eco_mode": "01060bf700003a1c",
    "set_1h_Eco": "01060bf80001cbdf",
    "set_2h_Eco": "01060bf800028bde",
    "set_3h_Eco": "01060bf800034a1e",
    "set_4h_Eco": "01060bf800040bdc",
    "enable_lighting": "01060bda00016bd5",
    "enable_lighting_MAX": "01060bda00022bd4",
    "enable_lighting_SOS": "01060bda0003ea14",
    "disable_lighting": "01060bda0004abd6",
    "charging_mode_Standard": "01060bf900005bdf",
    "charging_mode_Silent": "01060bf900019a1f",
    "charging_mode_Turbo": "01060bf90002da1e",
    "read_station_state": "0103000a0035a5df",
    "read_station_flags": "01030bb80043863a"
}
````

## Requirements

* Python 3.10+
* Bluetooth Low Energy (BLE) support
* Bluetti EB3A power station

## ❤️ Support

This project is developed in my free time.

If it saves you time or helps your work or if you want to add new ipc support, you can support further development with a donation

### Cryptocurrency

- **USDT (TRC20)** TUUZ8joXMZffHJ8nzDjVXNschHVcra5b2n
- **Ethereum / ERC-20:** 0xC0C5d618A19042440B032e374FfFfAfF5328C9C3
- **Bitcoin (BTC):** bc1q0ckgp3mpddkl2077s3w0kjgkdlj9eyr9dfq5k7

Every contribution helps improve the project. Thank you!
```
```
