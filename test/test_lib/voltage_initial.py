'''
    电压和电流源初始化设置
    Li Jie 2024/06/25
    备注：    
    fv    输出电压
    fi    输出电流
    hizv  输出高阻, 能更快转换到输出电压模式
    hizi  输出高阻, 能更快转换到输出电流模式
    sinki 输入电流模式(接地模式, 要抽电流的话请使用负电流)

    mi    测量电流
    mv    测量电压
    mtemp 测量温度
    hiz   测量引脚高阻抗

    ua5   电流范围5uA
    ua20  电流范围20uA
    ua200 电流范围200uA
    ma2   电流范围2mA
    ma50  电流范围50mA

    一共有16个通道
    --------------------------------------------
    修改了部分可能的报错, 请不要删除time.sleep(0.1)
    Li Jie 2024/06/27
'''

import time

def v_initial(spsmu):
    spsmu.baud_rate = 921600
    ## channel cfg
    spsmu.write("sour:mode 1,fv,mi,MA50")
    spsmu.write("sour:mode 2,fv,mi,MA50")
    spsmu.write("sour:mode 3,fv,mi,MA50")
    spsmu.write("sour:mode 4,fv,mi,MA50")
    spsmu.write("sour:mode 5,fv,mi,MA50")
    spsmu.write("sour:mode 6,fv,mi,MA50")
    spsmu.write("sour:mode 7,fv,mi,MA50")
    spsmu.write("sour:mode 8,fv,mv,MA50")
    spsmu.write("sour:mode 9,fv,mv,MA50")
    spsmu.write("sour:mode 10,fi,mi,UA20")
    spsmu.write("sour:mode 11,fi,mi,UA20")
    spsmu.write("sour:mode 12,fv,mi,MA50")
    spsmu.write("sour:mode 13,fv,mi,MA50")
    spsmu.write("sour:mode 14,fv,mi,MA50")
    spsmu.write("sour:mode 15,fi,mi,UA20")
    spsmu.write("sour:mode 16,hizv,mi,MA50")

    #channel 1, TAVDD
    spsmu.write("sour:volt 1,3.3" )
    time.sleep(0.1)

    #channel 2, VDDX
    spsmu.write("sour:volt 2,0.95" )
    time.sleep(0.1)

    #channel 3, LOGIC
    spsmu.write("sour:volt 3,0.9" )
    time.sleep(0.1)

    #channel 4, 1P2NOT
    spsmu.write("sour:volt 4,1.2" )
    time.sleep(0.1)

    #channel 5, CKBUF
    spsmu.write("sour:volt 5,0.9" )
    time.sleep(0.1)

    #channel 6, SAR
    spsmu.write("sour:volt 6,0.9" )
    time.sleep(0.1)

    #channel 7, OTHER
    spsmu.write("sour:volt 7,0.9" )
    time.sleep(0.1)

    #channel 8, L_WT
    spsmu.write("sour:volt 8,0.63" )
    time.sleep(0.1)

    #channel 9, S_WT
    spsmu.write("sour:volt 9,0.592" )
    print
    time.sleep(0.1)

    #channel 10, I_DU
    spsmu.write("sour:curr 10,1" )
    time.sleep(0.1)

    #channel 11, I_L
    spsmu.write("sour:curr 11,1" )
    time.sleep(0.1)

    #channel 12, VINCM
    spsmu.write("sour:volt 12,0.55" )
    time.sleep(0.1)

    #channel 13, OUTBUF
    spsmu.write("sour:volt 13,1.1" )
    time.sleep(0.1)

    #channel 14, VCKCM
    spsmu.write("sour:volt 14,0.45" )
    time.sleep(0.1)

    #channel 15, I_L
    spsmu.write("sour:curr 15,1" )
    time.sleep(0.1)

