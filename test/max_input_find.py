'''
    寻找输入摆幅的最大值
    Li Jie 2024/06/30
    -----------------------
'''

import time
import numpy as np
import matplotlib.pyplot as plt
import math
import pyvisa
from pydwf import DwfLibrary, DwfState, DwfDigitalInSampleMode
from pydwf.utilities import openDwfDevice
from matplotlib.animation import FuncAnimation
from collections import deque
from test_lib import FFT_try #from [你的文件夹名字] import FFT_try
from test_lib import voltage_initial #需要修改初始化电压电流的话请去voltage_initial修改
from test_lib import SGS100A_initial

# 全局变量来存储SNDR值
sdr_queue = deque(maxlen=50)

# 将十进制转换为对应位数的二进制码向量
# 一般不需要修改
def decimal_to_binary_vector(n, length=None):
    binary_str = bin(n)[2:]
    if length:
        binary_str = binary_str.zfill(length)
    binary_vector = [int(bit) for bit in binary_str]
    return binary_vector

# 数据处理
# -----------------------------下面需要修改--------------------------------
def data_process(rgData, frequency, decimate, fsample, Nsample):

    # 以下代码是基于时钟没送出来的获取数据的模式
    # 如果时钟送出来，或者有不一样的地方，请修改这里
    data_step = frequency * decimate / fsample
    print('step: %.4f' % data_step)
    tmp = 1
    while (tmp + 1 < len(rgData) and rgData[tmp] == rgData[tmp + 1]):
        if tmp > len(rgData)/Nsample*10 :
            tmp = 0
            break
        tmp = tmp + 1
    data_start = round(tmp + data_step / 2 + 1)
    print('start: %.0f' % data_start)
    data_out = []
    for i in range(Nsample):
        delt = int(round(i * data_step + data_start))
        if delt < len(rgData):
            data_out.append(decimal_to_binary_vector(rgData[delt], length=channels))
        else:
            data_out.append(0)
    data_array = np.array(data_out)

    # 只是单纯把码值送过去，减少计算量
    dat_P = data_array[:Nsample,   :6]

    weight_P = np.array([32, 16, 8, 4, 2, 1])

    dat_ana = dat_P @ weight_P
    
    return dat_ana
# -----------------------------上面需要修改--------------------------------


# 从digilent获取数据，一般这里不需要修改
def get_data():
    digitalIn.inputOrderSet(False)  # true:24...39,0...23;false:0...23,24...31
    digitalIn.sampleFormatSet(channels)
    digitalIn.sampleModeSet(DwfDigitalInSampleMode.Simple)  # Set sample mode to Simple
    digitalIn.dividerSet(divider)
    digitalIn.configure(False, True)  # Configure and start acquisition

    frequency = digitalIn.internalClockInfo() / divider / 1e6
    print('sample frequency is %.2fMHz' % frequency) # 打印显示现在实际的输出频率

    # 等待到数据存取完毕
    while True:
        time.sleep(0.1)
        sts = digitalIn.status(True)

        if sts in (DwfState.Config, DwfState.Prefill, DwfState.Armed):
            continue
        elif sts == DwfState.Done:
            break
        else:
            print("Error")
            return None, None, None, None

    print("available %.0f, lost %.0f, corrupt %.0f" % digitalIn.statusRecord()) # 显示有效的数据数，丢失和损坏数据数

    # Get acquisition data for all specified channels
    rgData = digitalIn.statusData(int(Nsample * (math.ceil(frequency * decimate / fsample) + 1000)))
 
    data_out = data_process(rgData, frequency, decimate, fsample, Nsample) # 调用上面的函数处理数据

    return np.max(data_out)


# 主要程序部分
# -----------------------------下面需要修改--------------------------------
dwf = DwfLibrary()
with openDwfDevice(dwf) as device:
    digitalIn = device.digitalIn
    channels  = 20     # 使用的通道数
    Nsample   = 65536  # FFT的点数
    divider   = 10     # 主时钟频率除以分频率就是采样频率，默认主时钟频率为 800MHz，实际频率取决于窗口输出。
    fsample   = 800    # ADC采样频率，单位为MHz
    decimate  = 125    # ADC decimate倍率
    nbit      = 6      # bit数
    fin       = fsample/decimate*(Nsample*16.25+11)/Nsample

    # 电源板初始化，如果没有电源板请注释掉这一段
    rm = pyvisa.ResourceManager()
    spsmu = rm.open_resource('ASRL3::INSTR') # 这里括号里的名称会根据设备不同而不同，请先运行SPSmu_find找到自己这边电源板对应的名称
    spsmu17 = rm.open_resource('USB0::0x0AAD::0x0088::114817::INSTR')
    spsmu16 = rm.open_resource('USB0::0x0AAD::0x0088::114816::INSTR')
    voltage_initial.v_initial(spsmu)
    SGS100A_initial.open_and_set(spsmu16, fsample, 0.7, 'INT')
    SGS100A_initial.open_and_set(spsmu17, fin, 0.5, 'EXT')
    SGS100A_initial.error_find(spsmu16)
    SGS100A_initial.error_find(spsmu17)

    get_data()

    #作图
    print('----------------------start----------------------')

    #扫描输入
    ntot = 20    
    x = np.ones(ntot+1)
    y = np.ones(ntot+1)
    tolerence = 4
    for i in range(ntot+1):
        vin = 0.6 + (0.8-0.6)/ntot*i
        print("input voltage is %f" %vin)
        SGS100A_initial.set_amplitude(spsmu17, vin)
        SGS100A_initial.error_find(spsmu17)
        time.sleep(5)    #等待电压写入和稳定
        x[i] = vin
        y[i] = get_data()
        print("max code is %f" %y[i])
        if y[i] == 63:
            tolerence -= 1  #设置到最大输入后几次就停止，避免电压过大击穿
            if tolerence == 0:
                break

    SGS100A_initial.close(spsmu16)
    SGS100A_initial.close(spsmu17)  #记得关闭

    plt.plot(x, y, marker='o')

    plt.title('vin vs code')
    plt.xlabel('vin')
    plt.ylabel('code out')

    # 显示图形
    plt.show()
#-----------------------------上面需要修改--------------------------------

