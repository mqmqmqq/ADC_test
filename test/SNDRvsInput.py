'''
    扫描输入
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

    # 具体数据处理，这里实现的是把码值还原成输出，需要按照需求修改
    # 下面是一个8bit含有matestable码值的示范
    # 此时data_array是通道从高到低的码值
    dat_P = data_array[:Nsample,   :6]
    dat_L = data_array[:Nsample,  6:12]
    dat_S = data_array[:Nsample, 12:18]
    dat_D = data_array[:Nsample, 18:20]

    dat_P = dat_P * 2 - 1
    MT = np.zeros((Nsample,3))
    count = np.zeros((3,1))
    for i in range(Nsample):
        flag = True
        for j in range(nbit):
            if (dat_S[i,j] == 1) and (flag == True):
                flag = False
                MT[i,2] = dat_P[i,j]
                count[2] += 1
            if (dat_L[i,j] == 1) and (flag == True):
                flag = False
                MT[i,1] = dat_P[i,j]
                count[1] += 1
            if flag == False:
                dat_P[i,j] = 0
        if flag:
            MT[i,0] = dat_P[i,nbit-1]
            count[0] += 1
    weight_P = np.array([130.079312339593, 64.1889997048791, 31.9834775115270, 15.9721535379942, \
                         8.10739984517575,4.63393995833461])
    weight_MT = np.array([-0.166468688118633, 0.982457640335805, 0.218728150278719])
    weight_DT = np.array([-2.03573165157928, -1.38116106951710])

    dat_ana = dat_P @ weight_P / 2 + MT @ weight_MT + dat_D @ weight_DT
    
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

    SNR, SNDR, SFDR, THD, ENOB, FLOOR_NOISE, HD, fffff = \
        FFT_try.fft_test(data_out, fsample / decimate * 1e6, 10, 0, Nsample, 0)

    return SNDR


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
    # spsmu = rm.open_resource('ASRL3::INSTR') # 这里括号里的名称会根据设备不同而不同，请先运行SPSmu_find找到自己这边电源板对应的名称
    spsmu17 = rm.open_resource('USB0::0x0AAD::0x0088::114817::INSTR')
    spsmu16 = rm.open_resource('USB0::0x0AAD::0x0088::114816::INSTR')
    # voltage_initial.v_initial(spsmu)
    SGS100A_initial.open_and_set(spsmu16, fsample, 0.7, 'INT')
    SGS100A_initial.open_and_set(spsmu17, fin, 0.65, 'EXT')
    SGS100A_initial.error_find(spsmu16)
    SGS100A_initial.error_find(spsmu17)

    get_data()

    #作图
    print('----------------------start----------------------')

    #扫描输入
    ntot = 24    
    x = np.ones(ntot+1)
    y = np.ones(ntot+1)
    for i in range(ntot+1):
        fin = fsample/decimate*(Nsample*(14.5+i*0.125)+111)/Nsample
        print("input frequency is %f" %fin)
        SGS100A_initial.set_frequency(spsmu17, fin)
        SGS100A_initial.error_find(spsmu17)
        time.sleep(10)    #等待电压写入和稳定
        x[i] = fin
        y[i] = get_data()
        print("SNDR is %f" %y[i])

    SGS100A_initial.close(spsmu16)
    SGS100A_initial.close(spsmu17)  #记得关闭

    plt.plot(x, y, marker='o')

    plt.title('fin vs SNDR')
    plt.xlabel('fin')
    plt.ylabel('SNDR')

    # 显示图形
    plt.show()

#-----------------------------上面需要修改--------------------------------

