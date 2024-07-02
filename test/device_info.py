'''
    确认digital discovery是否连接上并打印初始设置和参数
    Li Jie 2024/06/18
'''

from pydwf import DwfLibrary
from pydwf.utilities import openDwfDevice

dwf = DwfLibrary()

with openDwfDevice(dwf) as device:

    # Get a reference to the device's DigitalIn instrument.
    digitalIn = device.digitalIn

    # Use the DigitalOut instrument.
    fclk = digitalIn.internalClockInfo()
    print('''---------------device Info----------------------''')
    print('clock is %.2fMHz' %(fclk/1e6))
    print('clock source: %s' % digitalIn.clockSourceInfo())
    print('max divider: %.0f' % digitalIn.dividerInfo())
    print('acquisitionMode: %s' % digitalIn.acquisitionModeInfo())
    print('total bits: %.0f' % digitalIn.bitsInfo())
    print('buffer size: %.0f' % digitalIn.bufferSizeInfo())
    print('sample mode: %s' % digitalIn.sampleModeInfo())
    print('trigger source: %s' % digitalIn.triggerSourceInfo())
    print('max number of sample after sample: %s' % digitalIn.triggerPositionInfo())
    print('trigger auto time out: range [%.4f, %.4f]; number of step %.0f' % digitalIn.triggerAutoTimeoutInfo() )
    print('trigger info: low %.0f, high %.0f, rising %.0f, falling %.0f' % digitalIn.triggerInfo() )
    print('counter info: [%.0f, %.0f]' % digitalIn.counterInfo() )
    print('''-------------------end--------------------------''')
