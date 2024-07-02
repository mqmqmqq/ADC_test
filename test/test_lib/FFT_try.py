'''
    FFTs
    增加了fft_test
    Li Jie 2024/06/18
    -------------------------
    增加了ifft_res
    Li Jie 2024/06/20
    -------------------------
    修复了0输入时候的ifft报错中断
    Li Jie 2024/06/27
    -------------------------
'''
import numpy as np
from scipy.fft import fft
from scipy.signal import get_window
import matplotlib.pyplot as plt

def fft_test(Vin, fs, num_H, wid, Nsample, En_plot):
    data = Vin
    
    # 设置窗口和 FFT 参数
    if wid == 0:
        fundpnts = 0
        s_point = np.finfo(float).eps
        windpnts = 1
    else:
        fundpnts = 10
        windpnts = 2
        s_point = 0

    # 计算 FFT 的参数
    fres = fs / Nsample

    # 选择数据窗口
    y = data[:Nsample]
    f = np.arange(Nsample) * fres

    # 窗口处理
    yw = y
    if wid == 1:
        yw = y * get_window('hann', Nsample)

    # 执行 FFT
    fftout = np.abs(fft(yw)) / (Nsample / 2)
    fftoutdB = 20 * np.log10(fftout + s_point)
    Fin_ind = np.argmax(fftout[4:Nsample//2]) + 4  # 索引从4开始，除去DC
    Fin1_dB = np.max(fftoutdB[4:Nsample//2])
    fin = Fin_ind * fres

    # 计算谐波频率
    harm = np.zeros(num_H + 1)
    for i in range(1, num_H + 2):
        done = 0
        k = 1
        while not done:
            if i * fin < (k - 1 / 2) * fs:
                harm[i-1] = i * fin - (k - 1) * fs
                done = 1
            elif i * fin < k * fs:
                harm[i-1] = k * fs - i * fin
                done = 1
            else:
                k += 1

    harm_ind = np.round(harm / fres).astype(int)  # 确保索引是整数
    win_ind_min = (harm_ind[1:num_H + 1] - windpnts).astype(int)
    win_ind_max = (harm_ind[1:num_H + 1] + windpnts).astype(int)
    HD = np.zeros(num_H)

    for i in range(num_H):
        HD[i] = np.sum(fftout[win_ind_min[i]:win_ind_max[i]+1] ** 2)

    # 计算信噪比和其他参数
    fftout_n = fftout.copy()
    P_DC = np.sum(fftout_n[:3] ** 2)
    fund_ind = np.arange(harm_ind[0] - fundpnts, harm_ind[0] + fundpnts + 1).astype(int)
    P_S = np.sum(fftout_n[fund_ind] ** 2)
    P_ND = np.sum(fftout_n[:Nsample//2] ** 2) - P_S - P_DC
    P_D = np.sum(HD[:num_H])

    fftout_n[fund_ind] = 1e-20
    fftout_n[:3] = 1e-20
    P_H = np.max(HD[:num_H])

    SNDRo = 10 * np.log10(P_S / P_ND)
    THDo = -10 * np.log10(P_S / P_D)
    SNRo = 10 * np.log10(P_S / (P_ND - P_D))
    SFDRo = 10 * np.log10(P_S / P_H)
    ENOBo = (SNDRo - 1.76) / 6.02
    FLOOR_NOISEo = -SNRo - 10 * np.log10(Nsample / 2) + fftoutdB[harm_ind[0]]
    HDo = 10 * np.log10(HD / P_S)

    SNR = SNRo
    SFDR = SFDRo
    SNDR = SNDRo
    THD = THDo
    FLOOR_NOISE = FLOOR_NOISEo
    ENOB = ENOBo
    HD = HDo

    # 绘制 FFT 图像
    
    fffff = fftoutdB[:Nsample//2] - Fin1_dB
    if En_plot == 1:
        plt.figure()
        plt.plot(f[:Nsample//2] / 1e6, fftoutdB[:Nsample//2] - Fin1_dB, 'black', linewidth=0.5)
        for i in range(len(harm)):
            plt.plot(harm[i] / 1e6, fftoutdB[harm_ind[i]] - Fin1_dB, 'r*')
            plt.text(harm[i] / 1e6, fftoutdB[harm_ind[i]] - Fin1_dB + 3, str(i+1), color='m', fontsize=8)
        plt.ylabel('Full-Scale Normalized Magnitude[dB]')
        plt.xlabel('Frequency [MHz]')
        plt.title(f'FFT ({Nsample} points)\nFs = {fs/1e6} MSps, Fin = {fin/1e6} MHz ({fftoutdB[harm_ind[0]]:1.2g} dBfs)')
        plt.grid()
        plt.ylim([-150, 10])
        plt.xlim([0, f[Nsample//2] / 1e6])
        
        s1 = f'SFDR = {SFDRo:4.1f} dB\n'
        s2 = f'THD = {THDo:4.1f} dB\n'
        s3 = f'SNR = {SNRo:4.1f} dB\n'
        s4 = f'SNDR = {SNDRo:4.1f} dB\n'
        s5 = f'ENOB = {ENOBo:4.2f} bit\n'
        
        if harm[0] / 1e6 < f[Nsample//2] / 1e6 / 4:
            xstation = f[Nsample//2] / 1e6 / 2
        elif harm[0] / 1e6 > (f[Nsample//2] * 3) / 1e6 / 4:
            xstation = f[Nsample//2] / 1e6 / 4
        else:
            xstation = f[Nsample//2] / 1e6 / 32

        plt.text(xstation, -10, s1)
        plt.text(xstation, -20, s2)
        plt.text(xstation, -30, s3)
        plt.text(xstation, -40, s4)
        plt.text(xstation, -50, s5)
        plt.show(block=False)

    return SNR, SNDR, SFDR, THD, ENOB, FLOOR_NOISE, HD, fffff

#--------------------------------------------------------------------------------------------------#

def ifft_res(Vin, fs, wid, Nsample):
    data = Vin - np.mean(Vin)

    fres = fs / Nsample  # 频率分辨率
    Nsample = round(fs / fres)  # 采样点数

    y = data[:Nsample]

    yw = y
    if wid == 1:
        yw = y * get_window('hann', Nsample)

    fftout_ini = fft(yw)
    fftout = np.abs(fftout_ini) / (Nsample / 2)  # 归一化
    Fin_ind = np.argmax(fftout[:Nsample // 2])

    fftout_res = fft(yw)
    fftout_res[Fin_ind] = 0
    if Fin_ind != 0:
        fftout_res[Nsample - Fin_ind] = 0

    fftout_ideal = fft(yw)
    for i in range(len(fftout_ideal)):
        if i != Fin_ind and i != Nsample - Fin_ind:
            fftout_ideal[i] = 0

    Vout = np.fft.ifft(fftout_ideal)
    Vout_res = np.fft.ifft(fftout_res)

    return Vout.real, Vout_res.real, Fin_ind