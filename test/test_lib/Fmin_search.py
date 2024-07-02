'''
    最小值优化, 目前用的是Nelder-Mead方法
    包括可视化过程
    Li Jie 2024/06/27
    ------------------------------------------
    修改了函数的调用关系, 现在只需要修改objective_function()中的标出来的一部分就可以
    Li Jie
'''
import numpy as np
from scipy.fft import fft
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import math

# 定义目标函数
def objective_function(coef, Din, weight, Nsample_orig):

    #下面的函数是每个人自己把码值还原成输出的函数
    
    #-----------------------------------------请修改下面-----------------------------------------
    weight_local = np.concatenate((weight['high'], weight['low']))
    weight_local *= coef
    Dout = (Din['DinP'] @ weight_local[:6]) / 2 + Din['DinMT'] @ weight_local[6:9] + Din['DinD'] @ weight_local[9:11]
    Dout_d = Dout - np.mean(Dout)
    #-----------------------------------------请修改上面-----------------------------------------
    
    N = Nsample_orig
    winh = np.hanning(N)  # 使用汉宁窗函数
    
    start = 0  # Python 的索引从 0 开始
    OSR = 1
    input_FFT = fft(winh * Dout_d[start:start + N])
    input_FFT_abs = np.abs(input_FFT)
    input_FFT_power = input_FFT_abs ** 2
    
    # 去掉直流成分
    input_FFT_power[0] = 0
    
    # 获取结果
    peak = np.max(input_FFT_abs)
    k = np.argmax(input_FFT_abs)
    
    total_power = 0
    signal_power = 0
    
    for l in range(max(0, k-7), min(N//2, k+7)+1):
        signal_power += input_FFT_power[l]
    
    for l in range(8, N // (2 * OSR)):
        total_power += input_FFT_power[l]
    
    # 返回负的信噪比，因为我们要最小化这个函数
    return 10*math.log10((total_power-signal_power)/signal_power)



# 优化函数
def optimize_sndr(coef, Din, weight, Nsample):
    global iteration, fval_history, global_paused  

    # 初始化优化变量和状态
    initial_coef = coef
    global_paused = False

    # 停止按钮回调函数
    def pause_optimization(event):
        global global_paused
        global_paused = True

    # 优化回调函数
    def optimization_callback(coef):
        global iteration, fval_history, global_paused
        if global_paused:
            raise StopIteration("Optimization paused by user")
        fval = objective_function(coef, Din, weight, Nsample)
        fval_history.append(fval)
        iteration += 1
        update_plot(iteration, fval_history, fval)

    # 初始化图形
    def init_plot():
        plt.ion()  # 打开交互模式
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Objective Function Value')
        ax.set_title('Optimization Process using Nelder-Mead')
        return fig, ax

    # 更新图形
    def update_plot(iteration, fval_history, fval):
        ax.set_xlim(0, iteration)
        ax.set_ylim(min(fval_history) - 1, max(fval_history) + 1)
        line.set_data(range(iteration), fval_history)
        fig.canvas.draw()
        fig.canvas.flush_events()
        # 显示当前SNDR值
        sndr_text.set_text(f'SNDR: {fval:.2f} dB')

    iteration = 0
    fval_history = []

    # 初始化图形
    fig, ax = init_plot()
    line, = ax.plot([], [], 'ro-', markersize=5, label='Function Value')
    ax.legend()

    # 添加暂停按钮
    pause_ax = plt.axes([0.8, 0.01, 0.1, 0.05])  # [left, bottom, width, height]
    pause_button = Button(pause_ax, 'Pause')
    pause_button.on_clicked(pause_optimization)

    # 添加显示SNDR的文本
    sndr_text = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    # 使用Nelder-Mead方法进行最小化，并记录过程
    try:
        result = minimize(objective_function, initial_coef, args=(Din, weight, Nsample), method='Nelder-Mead', callback=optimization_callback)
    except StopIteration:
        print("Optimization paused by user")

    # 打印结果
    print("优化后的系数:", result.x)
    print("最小化的目标函数值:", result.fun)

    # 关闭交互模式
    plt.ioff()
    plt.show(block=False)

    return result
