'''
    discovery使用辅助函数
    增加led控制
    Li Jie 2024/07/30
    ---------------------------------
    增加了电源端口的控制代码
    Li Jie 2024/08/07
'''

import math
from pydwf import DwfLibrary, DwfDeviceParameter

#亮度从0到100, 只在digital discovery上有用，analog discovery上使用无效果
def led_brightness(device, brightness):
    device.paramSet(DwfDeviceParameter.LedBrightness, brightness)

def supply_set(device, channel, volt_or_curr, value):
    channel_dict = {'v+':0, 'v-':1}
    volt_or_curr_dict = {'volt':1, 'curr':2}
    device.analogIO.channelNodeSet(channel_dict[channel], volt_or_curr_dict[volt_or_curr], value)
    device.analogIO.channelNodeSet(channel_dict[channel], 0, 1)
    device.analogIO.enableSet(True)
    device.analogIO.configure()
    

    