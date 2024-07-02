'''
    测试FFT代码
    Li Jie 2024/06/25
    -------------------
    测试fminsearch代码
    Li Jie 2024/06/27
'''
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from test_lib import FFT_try
from test_lib import Fmin_search

plt.close('all')

Nsample_orig = 65536

num_H = 100
wid = 0
Nsample = Nsample_orig
start = 15

fclk = 800
fsample = 100
decim = 125
fs = fclk * 1e6 / decim

tolerance = 1000
nbit = 6

# Read CSV file
file_path = 'C:/Users/12559/Desktop/Lab/matlab/lj/2024_0626/'
file_name = 'fc800M_fs100M_low_d125_vin600_vclk700_65536_8b_2Mi_2.csv'
file = file_path+file_name
dat_ini_raw = pd.read_csv(file, header=None).values

dat_ini_P = dat_ini_raw[:, 0:6]
dat_ini_L = dat_ini_raw[:, 6:12]
dat_ini_S = dat_ini_raw[:, 12:18]
dat_ini_D = dat_ini_raw[:, 18:20]

datastep = fsample * decim / fclk

tmp = 1
while np.all(dat_ini_P[tmp, :] == dat_ini_P[tmp + 1, :]):
    tmp += 1
datastart = round(tmp + datastep / 2 + 1)

dat_all_P = np.zeros((Nsample  + tolerance, 6))
dat_all_L = np.zeros((Nsample + tolerance, 6))
dat_all_S = np.zeros((Nsample  + tolerance, 6))
dat_all_D = np.zeros((Nsample  + tolerance, 2))

for i in range(1, Nsample + tolerance + 1):
    delt = round((i - 1) * datastep)
    dat_all_P[i - 1, :] = dat_ini_P[datastart + delt, :]
    dat_all_L[i - 1, :] = dat_ini_L[datastart + delt, :]
    dat_all_S[i - 1, :] = dat_ini_S[datastart + delt, :]
    dat_all_D[i - 1, :] = dat_ini_D[datastart + delt, :]

dat_P = dat_all_P[start:start + Nsample, :]
dat_L = dat_all_L[start:start + Nsample, :]
dat_S = dat_all_S[start:start + Nsample, :]
dat_D = dat_all_D[start:start + Nsample, :]

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

sum_cnt = sum(count)
per_ct  = count/sum_cnt
print("Falls in 1st is %.2f\nFalls in 2nd is %.2f\nFalls in 3nd is %.2f" %(per_ct[0],per_ct[1],per_ct[2]))

weight_P = np.array([32, 16, 8, 4, 2, 1])
weight_MT = np.array([0, 0.25, 0])
weight_DT = np.array([-0.5, -0.25])

dat_ana = dat_P @ weight_P / 2 + MT @ weight_MT + dat_D @ weight_DT

Din = {
    'DinP' : dat_P,
    'DinMT': MT,
    'DinD' : dat_D
}

weight = {
    'high' : np.array([32, 16, 8, 4, 2, 1, 0.001, 0.25, 0.001]),
    'low': np.array([-0.5, -0.25])
}

coef = np.ones(11)
Nsample = 65536

SNDR = Fmin_search.objective_function(coef, Din, weight, Nsample)

result = Fmin_search.optimize_sndr(coef,Din,weight,Nsample)

weight_P  = weight_P * result.x[:6] 
weight_MT = weight_MT * result.x[6:9]
weight_DT = weight_DT * result.x[9:11]

vout_fmin = dat_P @ weight_P / 2 + MT @ weight_MT + dat_D @ weight_DT
vout_fmin = vout_fmin/sum(result.x)*(2^nbit)

SNR, SNDR, SFDR, THD, ENOB, FLOOR_NOISE, HD, fffff = \
        FFT_try.fft_test(vout_fmin, fsample / decim * 1e6, 10, 0, Nsample, 1)
vout, vout_res, fin_ind = FFT_try.ifft_res(vout_fmin-np.mean(vout_fmin), fsample / decim * 1e6, 0, Nsample)



# 绘图
plt.figure(3)
plt.subplot(2, 1, 1)
plt.plot(vout_res)
plt.subplot(2, 1, 2)
plt.plot(vout, label='check')
plt.plot(vout_fmin, label='res')
plt.show()