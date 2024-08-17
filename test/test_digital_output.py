'''
    实时SNDR 6bit版本
    Li Jie 2024/06/27
'''

import time
import numpy as np
import matplotlib.pyplot as plt
import math
import pyvisa
from pydwf import DwfLibrary, DwfDigitalOutOutput, DwfDigitalOutType, DwfDigitalOutIdle, DwfTriggerSource, DwfTriggerSlope
from pydwf.utilities import openDwfDevice
from matplotlib.animation import FuncAnimation
from collections import deque
from test_lib import FFT_try #from [你的文件夹名字] import FFT_try
from test_lib import voltage_initial #需要修改初始化电压电流的话请去voltage_initial修改


# -----------------------------下面需要修改--------------------------------
dwf = DwfLibrary()
with openDwfDevice(dwf) as device:
    device.digitalOut.reset()
    device.digitalOut.triggerSourceSet(DwfTriggerSource.PC)
    device.digitalOut.runSet(0)
    device.digitalOut.repeatSet(0)
    device.digitalOut.triggerSlopeSet(DwfTriggerSlope.Rise)
    device.digitalOut.repeatTriggerSet(False)

    device.digitalOut.enableSet(0, True)
    device.digitalOut.outputSet(0, DwfDigitalOutOutput.PushPull)
    device.digitalOut.typeSet(0, DwfDigitalOutType.Pulse)
    device.digitalOut.idleSet(0, DwfDigitalOutIdle.Low)
    device.digitalOut.dividerInitSet(0, 0)
    device.digitalOut.dividerSet(0, 10000)
    device.digitalOut.counterInitSet(0, False, 0)
    device.digitalOut.counterSet(0, 5, 5)

    device.digitalOut.enableSet(1, True)
    device.digitalOut.outputSet(1, DwfDigitalOutOutput.PushPull)
    device.digitalOut.typeSet(1, DwfDigitalOutType.Custom)
    device.digitalOut.idleSet(1, DwfDigitalOutIdle.Low)
    device.digitalOut.dividerInitSet(1, 0)
    device.digitalOut.dividerSet(1, 100000)
    device.digitalOut.dataSet(1, '0100101111', False)

    device.digitalOut.configure(True)
    device.digitalOut.device.triggerPC()
    device.digitalOut.configure(False)
    p = 1

#-----------------------------上面需要修改--------------------------------

