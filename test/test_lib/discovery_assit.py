'''
    discovery使用辅助函数
    增加led控制
    Li Jie 2024/07/30
    ---------------------------------
    增加了电源端口的控制代码
    Li Jie 2024/08/07
'''

import math
from pydwf import DwfDeviceParameter, DwfTriggerSource, DwfTriggerSlope, DwfDigitalOutOutput, DwfDigitalOutType, DwfDigitalOutIdle

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

def scan_chain(device, repetition, frequency, clock_channel, data_channel):
    device.digitalOut.reset()
    device.digitalOut.triggerSourceSet(DwfTriggerSource.PC)
    device.digitalOut.runSet(0)
    device.digitalOut.repeatSet(repetition)
    device.digitalOut.triggerSlopeSet(DwfTriggerSlope.Rise)
    device.digitalOut.repeatTriggerSet(False)

    divide1 = device.digitalOut.internalClockInfo()/frequency/10

    device.digitalOut.enableSet(clock_channel, True)
    device.digitalOut.outputSet(clock_channel, DwfDigitalOutOutput.PushPull)
    device.digitalOut.typeSet(clock_channel, DwfDigitalOutType.Pulse)
    device.digitalOut.idleSet(clock_channel, DwfDigitalOutIdle.Low)
    device.digitalOut.dividerInitSet(clock_channel, 0)
    device.digitalOut.dividerSet(clock_channel, frequency)
    device.digitalOut.counterInitSet(clock_channel, False, 0)
    device.digitalOut.counterSet(clock_channel, 5, 5)

    device.digitalOut.enableSet(data_channel, True)
    device.digitalOut.outputSet(data_channel, DwfDigitalOutOutput.PushPull)
    device.digitalOut.typeSet(data_channel, DwfDigitalOutType.Custom)
    device.digitalOut.idleSet(data_channel, DwfDigitalOutIdle.Low)
    device.digitalOut.dividerInitSet(data_channel, 0)
    device.digitalOut.dividerSet(data_channel, 100000)
    device.digitalOut.dataSet(data_channel, '0100101111', False)

    device.digitalOut.configure(True)
    device.digitalOut.device.triggerPC()
    device.digitalOut.configure(False)
    

    