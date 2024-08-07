'''
    使用两个discovery实时SNDR 6bit版本
    请将两台设备的T1连接, 来实现时钟同步
    Li Jie 2024/07/31
'''

import time
import numpy as np
import matplotlib.pyplot as plt
import math
import pyvisa
from pydwf import DwfLibrary, DwfState, DwfDigitalInSampleMode, PyDwfError, DwfDeviceParameter
from matplotlib.animation import FuncAnimation
from collections import deque
from test_lib import FFT_try #from [你的文件夹名字] import FFT_try
from test_lib import voltage_initial #需要修改初始化电压电流的话请去voltage_initial修改
from test_lib import discovery_assit

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
    rgdata1 = rgData['data1']
    rgdata2 = rgData['data2']
    while (tmp + 1 < len(rgdata2) and rgdata2[tmp] == rgdata2[tmp + 1]):
        if tmp > len(rgData)/Nsample*10 :
            tmp = 0
            break
        tmp = tmp + 1
    data_start = round(tmp + data_step / 2 + 1)
    print('start: %.0f' % data_start)
    data_out = []
    for i in range(Nsample):
        delt = int(round(i * data_step + data_start))
        if delt < len(rgdata1):
            part1 = decimal_to_binary_vector(rgdata1[delt], length=channel1)
            part2 = decimal_to_binary_vector(rgdata2[delt], length=channel2)
            data_out.append(part1+part2)
        else:
            data_out.append(0)
    data_array = np.array(data_out)

    # 具体数据处理，这里实现的是把码值还原成输出，需要按照需求修改
    # 此时data_array是通道从高到低的码值
    dat_P = data_array[:Nsample, :]

    dat_P = dat_P * 2 - 1
    weight_P = np.ones(16)

    dat_ana = dat_P @ weight_P / 2
    
    return dat_ana
# -----------------------------上面需要修改--------------------------------


# 从digilent获取数据，一般这里不需要修改
def get_data():
    digitalIn1.inputOrderSet(False)  # true:24...39,0...15;false:0...23,24...31
    digitalIn2.inputOrderSet(False)  # true:24...39,0...15;false:0...23,24...31
    digitalIn1.sampleFormatSet(channel1)
    digitalIn1.sampleFormatSet(channel2)
    digitalIn1.sampleModeSet(DwfDigitalInSampleMode.Simple)  # Set sample mode to Simple
    digitalIn2.sampleModeSet(DwfDigitalInSampleMode.Simple)  # Set sample mode to Simple
    digitalIn1.dividerSet(divider1)
    digitalIn2.dividerSet(divider2)
    frequency1 = digitalIn1.internalClockInfo() / divider1 / 1e6
    frequency2 = digitalIn2.internalClockInfo() / divider2 / 1e6
    print('实际采样频率分别是 %.2fMHz, %.2fMHz' % (frequency1,frequency2)) # 打印显示现在实际的输出频率
    if frequency1 != frequency2 :
        print("请确认, 两个采样频率不一样")

    digitalIn1.configure(False, True)  # Configure and start acquisition
    digitalIn2.configure(False, True)  # Configure and start acquisition


    # 等待到数据存取完毕
    while True:
        time.sleep(0.1)
        sts = digitalIn1.status(True)

        if sts in (DwfState.Config, DwfState.Prefill, DwfState.Armed):
            continue
        elif sts == DwfState.Done:
            break
        else:
            print("Error")
            return None, None, None, None

    print("device1 available %.0f, lost %.0f, corrupt %.0f" % digitalIn1.statusRecord()) # 显示有效的数据数，丢失和损坏数据数
    print("device2 available %.0f, lost %.0f, corrupt %.0f" % digitalIn2.statusRecord()) # 显示有效的数据数，丢失和损坏数据数

    # Get acquisition data for all specified channels
    rgData1 = digitalIn1.statusData(int(Nsample * (math.ceil(frequency1 * decimate / fsample) + 1000)))
    rgData2 = digitalIn2.statusData(int(Nsample * (math.ceil(frequency2 * decimate / fsample) + 1000)))

    #这里也可以用来调换顺序
    rgData = {
        'data1' : rgData1,
        'data2' : rgData2
    }
 
    data_out = data_process(rgData, frequency1, decimate, fsample, Nsample) # 调用上面的函数处理数据

    SNR, SNDR, SFDR, THD, ENOB, FLOOR_NOISE, HD, fffff = \
        FFT_try.fft_test(data_out, fsample / decimate * 1e6, 10, 0, Nsample, 0)

    vout, vout_res, fin_ind = FFT_try.ifft_res(data_out, fsample / decimate * 1e6, 0, Nsample)
    return fffff, data_out, vout_res, (SNR, SNDR, SFDR, ENOB)

# 这里是画图的函数，一般不需要修改
def updata(frame):
    global fft_line, vin_line, vres_line, sndr_line, ax1, ax2, ax3, ax4

    # Clear previous annotations
    for txt in ax1.texts:
        txt.remove()
    for txt in ax2.texts:
        txt.remove()
    for txt in ax3.texts:
        txt.remove()

    fffff, data_out, vout_res, metrics = get_data()
    if fffff is None or data_out is None or vout_res is None:
        return fft_line, vin_line, vres_line, sndr_line  # Handle error
    
    SNR, SNDR, SFDR, ENOB = metrics

    fft_line.set_ydata(fffff)
    vin_line.set_ydata(data_out)
    vres_line.set_ydata(vout_res)

    # Add SNDR to the queue
    sdr_queue.append(SNDR)
    sndr_data = np.zeros(50)
    sndr_data[-len(sdr_queue):] = list(sdr_queue)
    sndr_line.set_ydata(sndr_data)

    # Add annotations to the first plot
    ax1.annotate(f'SNDR: {SNDR:.2f}', xy=(0.7, 0.9), xycoords='axes fraction', fontsize=12, color='red')
    ax1.annotate(f'SFDR: {SFDR:.2f}', xy=(0.7, 0.8), xycoords='axes fraction', fontsize=12, color='red')
    ax1.annotate(f'SNR: {SNR:.2f}', xy=(0.7, 0.7), xycoords='axes fraction', fontsize=12, color='red')
    ax1.annotate(f'ENOB: {ENOB:.2f}', xy=(0.7, 0.6), xycoords='axes fraction', fontsize=12, color='red')

    # Find max and min values for the second and third plots
    vin_max = np.max(data_out)
    vin_min = np.min(data_out)
    vres_max = np.max(vout_res)
    vres_min = np.min(vout_res)

    # Add annotations to the second plot
    ax2.annotate(f'Max: {vin_max:.2f}', xy=(0.7, 0.9), xycoords='axes fraction', fontsize=12, color='blue')
    ax2.annotate(f'Min: {vin_min:.2f}', xy=(0.7, 0.8), xycoords='axes fraction', fontsize=12, color='blue')

    # Add annotations to the third plot
    ax3.annotate(f'Max: {vres_max:.2f}', xy=(0.7, 0.9), xycoords='axes fraction', fontsize=12, color='green')
    ax3.annotate(f'Min: {vres_min:.2f}', xy=(0.7, 0.8), xycoords='axes fraction', fontsize=12, color='green')

    return fft_line, vin_line, vres_line, sndr_line


# 主要程序部分

try:
    dwf = DwfLibrary()
    device_count = dwf.deviceEnum.enumerateDevices()
    if device_count < 2:
        print("连接的仪器没有两台")
        
    device1 = dwf.deviceControl.open(-1)
    device2 = dwf.deviceControl.open(-1)
    discovery_assit.led_brightness(device1, 100)
    discovery_assit.led_brightness(device2, 20)
    print("led更亮的那一台是device1, 暗的那一台是device2")

    #下面的代码在锁两台仪器的时钟
    # 0--使用内部时钟
    # 1--将参考时钟通过T1送出去
    # 2--使用T1的参考时钟
    # 3--把T1作为参考 I/O
    device1.paramSet(DwfDeviceParameter.ClockMode, 1)
    device2.paramSet(DwfDeviceParameter.ClockMode, 2)
    print("device1送出参考时钟, device2接受参考时钟")

    # -----------------------------下面需要修改--------------------------------

    #如果物理连接和仪器标号不一样，最方便的是交换下面两行代码
    digitalIn1 = device1.digitalIn
    digitalIn2 = device2.digitalIn
    channel1  = 8  #device1中调用的通道数
    channel2  = 8   #device2中调用的通道数
    channels  = channel1 + channel2     # 使用的通道数
    Nsample   = 65536  # FFT的点数
    divider1   = 10     # 主时钟频率除以分频率就是采样频率，默认digital主时钟频率为 800MHz，实际频率取决于窗口输出。
    divider2   = 10     # analog和digital的主时钟频率不一样，所以用的仪器不同就要设置不同的比例，默认的alanlog主时钟是100MHz。
    fsample   = 800    # ADC采样频率，单位为MHz
    decimate  = 125    # ADC decimate倍率
    nbit      = 6      # bit数

    # 电源板初始化，如果没有电源板请注释掉这一段
    # rm = pyvisa.ResourceManager()
    # spsmu = rm.open_resource('ASRL3::INSTR') # 这里括号里的名称会根据设备不同而不同，请先运行SPSmu_find找到自己这边电源板对应的名称
    # spsmu.baud_rate = 921600
    # voltage_initial.v_initial(spsmu)


    #实时作图
    print('----------------------start----------------------')

    fig, ((ax1, ax4), (ax2, ax3)) = plt.subplots(2, 2, figsize=(10, 6)) # 画图的尺寸
    fig.tight_layout(pad=3.0)

    fft_line, = ax1.plot(np.zeros(Nsample // 2))
    vin_line, = ax2.plot(np.zeros(Nsample))
    vres_line, = ax3.plot(np.zeros(Nsample))
    sndr_line, = ax4.plot(np.zeros(50))

    ax1.set_title('fft')
    ax2.set_title('vin_line')
    ax3.set_title('vres_line')
    ax4.set_title('SNDR')

    ax1.set_ylim(-150,10)   # 根据频谱的预期范围设置
    ax2.set_ylim(-150,150)  # 根据码值的预期范围设置
    ax3.set_ylim(-4, 4)     # 根据残差的预期范围设置
    ax4.set_ylim(0, 60)     # 根据SNDR的预期范围设置

    ani = FuncAnimation(fig, updata, frames=range(100), blit=False, interval=1000)

    plt.show()
    #-----------------------------上面需要修改--------------------------------
    #下面增加的是关闭仪器和报错处理
    device1.__exit__()
    device2.__exit__()
except PyDwfError as exception :
    print("PyDwfError:", exception)
except :
    print("Other error")


