#! /usr/bin/env python3

'''
    测试同时控制两台设备
    Li Jie 2024/07/30
'''

from pydwf import DwfLibrary, PyDwfError
from test_lib import discovery_assit

def main():
    try:
        dwf = DwfLibrary()
        device_count = dwf.deviceEnum.enumerateDevices()
        if device_count < 2:
            print("至少需要两台设备")

        # 打开两台仪器
        device1 = dwf.deviceControl.open(-1)  # 打开第一个设备
        device2 = dwf.deviceControl.open(-1)  # 打开第二个设备
        discovery_assit.led_brightness(device1, 100)
        discovery_assit.led_brightness(device2, 20)
        print(device1.digitalIn.triggerSourceGet())
        print(device2.digitalIn.triggerSourceGet())
        print(device1.digitalIn.triggerSourceInfo())
        print(device2.digitalIn.triggerSourceInfo())
        device1.__exit__()
        device2.__exit__()
    except PyDwfError as exception:
        print("PyDwfError:", exception)
        device1.__exit__()
        device2.__exit__()
    except KeyboardInterrupt:
        print("keyboard interrupt, ending test.")
        device1.__exit__()
        device2.__exit__()

if __name__ == "__main__":
    main()