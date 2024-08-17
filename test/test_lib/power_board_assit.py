'''
    包装后的电源板函数
    Li Jie 2024/08/16
    备注：

    out_mode可选择值:    
    fv    输出电压
    fi    输出电流
    hizv  输出高阻, 能更快转换到输出电压模式
    hizi  输出高阻, 能更快转换到输出电流模式
    sinki 输入电流模式(接地模式, 要抽电流的话请使用负电流)

    测量可选择值
    mi    测量电流
    mv    测量电压
    mtemp 测量温度
    hiz   测量引脚高阻抗

    irange可选择值:
    ua5   电流范围5uA
    ua20  电流范围20uA
    ua200 电流范围200uA
    ma2   电流范围2mA
    ma50  电流范围50mA

    一共有16个通道
'''

import time
import pyvisa

#设置输出模式和电流范围
def set_mode(spsmu, channel, out_mode, irange):
    spsmu.write("sour:mode %u,%s,mi,%s" %(channel, out_mode, irange))

#设置电压
def set_v(spsmu, channel, voltage):
    spsmu.write("sour:volt %u,%f" %(channel, voltage))
    time.sleep(0.1)

#设置电流
def set_i(spsmu, channel, current):
    spsmu.write("sour:curr %u,%f" %(channel, current))
    time.sleep(0.1)

#测电流
def measure_i(spsmu, channel):
    mode = spsmu.query("sour:mode? %u" %channel)
    parts = mode.strip().split(',')
    out_mode     = parts[0].strip('"')
    measure_mode = parts[1].strip('"')
    irange       = parts[2].strip('"')
    if measure_mode != "mi":
        spsmu.write("sour:mode %u,%s,mi,%s" %(channel, out_mode, irange))
    print("channel %u current is " % channel)
    print(spsmu.query("meas:curr? %u" %channel))

#测电压
def measure_v(spsmu, channel):
    mode = spsmu.query("sour:mode? %u" %channel)
    parts = mode.strip().split(',')
    out_mode     = parts[0].strip('"')
    measure_mode = parts[1].strip('"')
    irange       = parts[2].strip('"')
    if measure_mode != "mv":
        spsmu.write("sour:mode %u,%s,mv,%s" %(channel, out_mode, irange))
    print("channel %u voltage is " % channel)
    print(spsmu.query("meas:volt? %u" %channel))

#重新设置电流范围
def set_irange(spsmu, channel, irange):
    mode = spsmu.query("sour:mode? %u" %channel)
    parts = mode.strip().split(',')
    out_mode     = parts[0].strip('"')
    measure_mode = parts[1].strip('"')
    irange       = parts[2].strip('"')
    if out_mode == 'fi':
        current = spsmu.query("sour:curr:last? %u" %channel)
        spsmu.write("sour:mode %u,%s,%s,%s" %(channel, out_mode, measure_mode, irange))
        spsmu.write("sour:curr %u,%f" %(channel, current))
    else:
        spsmu.write("sour:mode %u,%s,%s,%s" %(channel, out_mode, measure_mode, irange))

#查看报错
def last_error(spsmu):
    print(spsmu.query("syst:err?"))

#初始化
def v_initial(spsmu):
    set_mode(spsmu, 1, 'fv', 'MA50')
    set_mode(spsmu, 2, 'fv', 'MA50')
    set_mode(spsmu, 3, 'fv', 'MA50')
    set_mode(spsmu, 4, 'fv', 'MA50')
    set_mode(spsmu, 5, 'fv', 'MA50')
    set_mode(spsmu, 6, 'fv', 'MA50')
    set_mode(spsmu, 7, 'fv', 'MA50')
    set_mode(spsmu, 8, 'fv', 'MA50')
    set_mode(spsmu, 9, 'fv', 'MA50')
    set_mode(spsmu, 10, 'fi', 'UA20')
    set_mode(spsmu, 11, 'fi', 'UA20')
    set_mode(spsmu, 12, 'fv', 'MA50')
    set_mode(spsmu, 13, 'fv', 'MA50')
    set_mode(spsmu, 14, 'fv', 'MA50')
    set_mode(spsmu, 15, 'fi', 'UA20')
    set_mode(spsmu, 16, 'hizv', 'MA50')
    spsmu.write("sour:mode 15,fi,mi,UA20")
    spsmu.write("sour:mode 16,hizv,mi,MA50")

    set_v(spsmu, 1, 3.3)        #channel 1, TAVDD
    set_v(spsmu, 2, 0.95)       #channel 2, VDDX
    set_v(spsmu, 3, 0.9)        #channel 3, LOGIC
    set_v(spsmu, 4, 1.2)        #channel 4, 1P2NOT
    set_v(spsmu, 5, 0.9)        #channel 5, CKBUF
    set_v(spsmu, 6, 0.9)        #channel 6, SAR
    set_v(spsmu, 7, 0.9)        #channel 7, OTHER
    set_v(spsmu, 8, 0.63)       #channel 8, L_WT
    set_v(spsmu, 9, 0.592)      #channel 9, S_WT
    set_i(spsmu, 10, 1)         #channel 10, I_DU
    set_i(spsmu, 11, 1)         #channel 11, I_L
    set_v(spsmu, 12, 0.55)      #channel 12, VINCM
    set_v(spsmu, 13, 1.1)       #channel 13, OUTBUF
    set_v(spsmu, 14, 0.45)      #channel 14, VCKCM
    set_i(spsmu, 15, 1)         #channel 15, I_L


#下面的代码用来直接测试调试功能
if __name__ == "__main__":

    rm = pyvisa.ResourceManager()
    spsmu = rm.open_resource('ASRL3::INSTR')
    spsmu.baud_rate = 921600

    #验证初始化
    v_initial(spsmu)

    #验证测试电压电流
    measure_i(spsmu, 1)
    measure_v(spsmu, 1)
    measure_i(spsmu, 1)
    measure_v(spsmu, 1)

    #验证切换电压
    set_v(spsmu, 1, 1)
    measure_v(spsmu, 1)
    measure_i(spsmu, 1)

    #验证切换电流范围
    measure_i(spsmu, 15)
    set_irange(spsmu, 15, 'UA200')
    measure_i(spsmu, 15)
    measure_v(spsmu, 15)

    #验证查看报错
    last_error(spsmu)