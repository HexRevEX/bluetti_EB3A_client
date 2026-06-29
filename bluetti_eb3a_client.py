#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2026 HexRevEx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
from bleak import BleakClient
from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json
from datetime import datetime
import json
import os
import re
import struct
import sys

__version__ = "1.0.2"
__app_header__ = f"Bluetti EB3A Client v.{__version__}"

if sys.version_info < (3, 10):
    raise RuntimeError("This script requires Python 3.10 or higher")

@dataclass_json
@dataclass
class Settings:
    
    station_mac: str = field(default = "AA:BB:CC:DD:EE:FF")

    station_output_uuid:str = field(default = "0000ff01-0000-1000-8000-00805f9b34fb")
    station_input_uuid :str = field(default = "0000ff02-0000-1000-8000-00805f9b34fb") 
    
    enable_DC  	          : str = field(default = "01060bc000014a12")
    disable_DC            : str = field(default = "01060bc000008bd2")
    enable_AC             : str = field(default = "01060bbf00017bca")
    disable_AC            : str = field(default = "01060bbf0000ba0a")
    enable_Power_lifting  : str = field(default = "01060bfa00016a1f")
    disable_Power_lifting : str = field(default = "01060bfa0000abdf")
    enable_Eco_mode       : str = field(default = "01060bf70001fbdc")
    disable_Eco_mode      : str = field(default = "01060bf700003a1c")
    set_1h_Eco            : str = field(default = "01060bf80001cbdf")
    set_2h_Eco            : str = field(default = "01060bf800028bde")
    set_3h_Eco            : str = field(default = "01060bf800034a1e")
    set_4h_Eco            : str = field(default = "01060bf800040bdc")
    enable_lighting       : str = field(default = "01060bda00016bd5")
    enable_lighting_MAX   : str = field(default = "01060bda00022bd4")
    enable_lighting_SOS   : str = field(default = "01060bda0003ea14")
    disable_lighting      : str = field(default = "01060bda0004abd6")
    charging_mode_Standard: str = field(default = "01060bf900005bdf")
    charging_mode_Silent  : str = field(default = "01060bf900019a1f")
    charging_mode_Turbo   : str = field(default = "01060bf90002da1e")
    read_station_state    : str = field(default = "0103000a0035a5df")
    read_station_flags    : str = field(default = "01030bb80043863a")
    
    def saveSettings(self, file_path: str) -> None:
        with open(file_path, "w") as f:
            f.write(self.to_json(indent=4))

    @classmethod
    def loadSettings(cls, file_path: str) -> "Settings":
        with open(file_path, "r") as f:
            return cls.from_json(f.read())


class Bluetti_Client:
    
    def __init__(self):
        
        self.commands_queue = asyncio.Queue()
        
        self.MAC_REGEX = re.compile(r'^([0-9A-Fa-f]{2}([:])){5}[0-9A-Fa-f]{2}$')
        self.client: BleakClient = None
        self.settings = Settings()
        
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"settings.json")
        
        try:
            self.settings = Settings.loadSettings(settings_file)
        except Exception as e:
            print(e)
            self.settings.saveSettings(settings_file)

    async def commands_sender(self):

        while True:
            item = await self.commands_queue.get()
            self.commands_queue.task_done()
    
    def is_mac_address(self, s: str) -> bool:
        return bool(self.MAC_REGEX.match(s))

    async def connect(self):
        
        try:
            await self.client.connect()
            print(f"Client {self.client.address}, connected: {self.client.is_connected}")
        except Exception as e:
            print(f"Fail to connect {self.client.address} - {e}")
        
    async def disconnect(self):
        
        try:
            await self.stop_notify(self.settings.station_output_uuid)
            await self.client.disconnect()
        except Exception as e:
            print(f"Fail to connect {self.client.address} - {e}")

            
    async def read(self, uuid:str) -> bytes:
        
        value = await self.client.read_gatt_char(uuid)
        return value

    async def write(self, uuid:str, hex: str, time_delay:float = 0.5):
        
        try:
            await self.client.write_gatt_char(uuid, bytes.fromhex(hex), response=True)
            #print(f"{datetime.now().strftime('%Y.%m.%d %H:%M:%S')} : -> {hex}")
            await asyncio.sleep(time_delay)
        except Exception as e:
            print(f"Error {uuid} - {e}\n")

    def notification_handler(self, sender, data: bytearray):
        
        if len(data) == 111: # station values
            self.parse_station_state(data)
        #elif len(data) == 139: # station flags
        #    self.parse_station_flags(data)        
        #else:
        #    print(f"{datetime.now().strftime('%Y.%m.%d %H:%M:%S')} : <- {bytes(data).hex()}")

    async def start_notify(self, uuid:str):
        await self.client.start_notify(uuid, self.notification_handler)
        
    async def stop_notify(self, uuid:str):
        await self.client.stop_notify(uuid)

    async def switch_DC(self, on:bool = True):
        await self.write(self.settings.station_input_uuid, self.settings.enable_DC if on else self.settings.disable_DC)

    async def switch_AC(self, on:bool = True):
        await self.write(self.settings.station_input_uuid, self.settings.enable_AC if on else self.settings.disable_AC)
        
    async def switch_ECO_mode(self, on:bool = True):
        await self.write(self.settings.station_input_uuid, self.settings.enable_Eco_mode if on else self.settings.disable_Eco_mode)

    async def switch_lighting(self, on:bool = True):
        await self.write(self.settings.station_input_uuid, self.settings.enable_lighting if on else self.settings.disable_lighting)

    async def switch_lighting_max(self, on:bool = True):
        await self.write(self.settings.station_input_uuid, self.settings.enable_lighting_MAX if on else self.settings.disable_lighting)

    async def switch_lighting_sos(self, on:bool = True):
        await self.write(self.settings.station_input_uuid, self.settings.enable_lighting_SOS if on else self.settings.disable_lighting)

    async def switch_power_lifting(self, on:bool = True):
        await self.write(self.settings.station_input_uuid, self.settings.enable_Power_lifting if on else self.settings.disable_Power_lifting)

    async def set_charging_mode_standard(self):
        await self.write(self.settings.station_input_uuid, self.settings.charging_mode_Standard)
    
    async def set_charging_mode_turbo(self):
        await self.write(self.settings.station_input_uuid, self.settings.charging_mode_Turbo)

    async def set_charging_mode_silent(self):
        await self.write(self.settings.station_input_uuid, self.settings.charging_mode_Silent)

    async def set_eco_mode_1h(self):
        await self.write(self.settings.station_input_uuid, self.settings.set_1h_Eco)
    
    async def set_eco_mode_2h(self):
        await self.write(self.settings.station_input_uuid, self.settings.set_2h_Eco)
        
    async def set_eco_mode_3h(self):
        await self.write(self.settings.station_input_uuid, self.settings.set_3h_Eco)
    
    async def set_eco_mode_4h(self):
        await self.write(self.settings.station_input_uuid, self.settings.set_4h_Eco)
    
    async def read_station_state(self):
        await self.write(self.settings.station_input_uuid, self.settings.read_station_state)

    async def read_station_flags(self):
        await self.write(self.settings.station_input_uuid, self.settings.read_station_flags )        
    
    def parse_station_state(self, data: bytes):
        
        station_model  = data[3:15].decode().rstrip('\x00')
        
        station_PV    = struct.unpack(">H", data[55:57])[0]
        station_Grid  = struct.unpack(">H", data[57:59])[0]
        station_AC    = struct.unpack(">H", data[59:61])[0]
        station_DC    = struct.unpack(">H", data[61:63])[0]
        station_char_perc = struct.unpack(">H", data[69:71])[0]
        
        temperatureError = bool(data[104]) 
        
        is_Grid = bool(data[74]) 
        is_UPS  = bool(data[78])
        is_AC   = bool(data[80])
        is_DC   = bool(data[82])
        
        is_PV_enabled  = bool(data[72])
        is_PV_charging  = bool(data[76])
        
        print(f"MODEL: {station_model:>12}, {'PV' if is_PV_enabled else '   '} {'PV Charging' if is_PV_charging else '   '}"+\
              f"{'UPS' if is_UPS else '   '} PV in:{'+' if is_PV_charging else ' '}{station_PV:>5} W, Grid:{'+' if is_Grid else ' '}"+\
              f"{station_Grid:>5} W, AC:{'+' if is_AC else ' '}{station_AC:>5} W,  DC:{'+' if is_DC else ' '}{station_DC:>5} W, Electric charge:"+
              f" {station_char_perc:>5}%")
        
        if temperatureError:
            print("!!!!High temperature error!!!!")
    
    def parse_station_flags(self, data: bytes):
        
        isPowerLifting = data[136] != 0
        isEcoMode = data[130] != 0
        isStandardCharging = data[134] == 0
        isSilentCharging = data[134] == 1
        isTurboCharging = data[134] == 2
        isLight = data[72] == 1
        isLightMAX = data[72] == 2
        isLightSOS = data[72] == 3
        
        print(f"PowerLifting: {isPowerLifting:>6}, EcoMode: {isEcoMode:>6}, Silent: {isSilentCharging:>6}, Standard: {isStandardCharging:>6}, Turbo: {isTurboCharging:>6}, Light: {isLight:>6}, MAX: {isLightMAX:>6}, SOS: {isLightSOS:>6}")
    
    async def test(self):

        try:
            if self.is_mac_address(self.settings.station_mac):

                self.client = BleakClient(self.settings.station_mac)
                await self.connect()
                await self.start_notify(self.settings.station_output_uuid)
                
                await asyncio.sleep(2)
                print("switch_lighting ON")
                await self.switch_lighting(True)
                await self.read_station_state()
                await self.read_station_flags()
                
                await asyncio.sleep(2)
                print("switch_lighting OFF")
                await self.switch_lighting(False)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch_DC ON")
                await self.switch_DC(True)
                await self.read_station_state()
                await self.read_station_flags()
                
                await asyncio.sleep(2)
                print("switch_DC OFF")
                await self.switch_DC(False)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch_AC ON")
                await self.switch_AC(True)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch_AC OFF")
                await self.switch_AC(False)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch_ECO mode ON")
                await self.switch_ECO_mode(True)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch_ECO mode OFF")
                await self.switch_ECO_mode(False)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch power lifting ON")
                await self.switch_power_lifting(True)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch power lifting mode OFF")
                await self.switch_power_lifting(False)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch lighting max ON")
                await self.switch_lighting_max(True)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch lighting max OFF")
                await self.switch_lighting_max(False)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch lighting SOS ON")
                await self.switch_lighting_max(True)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("switch lighting SOS OFF")
                await self.switch_lighting_sos(False)
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("set_charging_mode_silent")
                await self.set_charging_mode_silent()
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("set_charging_mode_turbo")
                await self.set_charging_mode_turbo()
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("set_charging_mode_standard")
                await self.set_charging_mode_standard()
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("set_eco_mode_4h")
                await self.set_eco_mode_4h()
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("set_eco_mode_3h")
                await self.set_eco_mode_3h()
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("set_eco_mode_2h")
                await self.set_eco_mode_2h()
                await self.read_station_state()
                await self.read_station_flags()

                await asyncio.sleep(2)
                print("set_eco_mode_1h")
                await self.set_eco_mode_1h()
                await self.read_station_state()
                await self.read_station_flags()

        finally:
            await self.disconnect()

if __name__ == "__main__":
    print(__app_header__)
    ble_client = Bluetti_Client()
    asyncio.run(ble_client.test())
