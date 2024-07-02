'''
    SGS100A初始化
    Li Jie 2024/06/28
'''
import math

def mv_to_dBm(vin):
    vout = 10*math.log10(20*(vin**2))
    return vout

def open_and_set(spsmu, f, a, clk_mode):
    spsmu.baud_rate = 115200
    spsmu.write("*RST")
    spsmu.write("*CLS")
    print(spsmu.query("LOCK? 72349234"))
    spsmu.write("SOUR:OPM NORM")
    spsmu.write("SOUR:FREQ:CW %.9f MHz" % f)
    spsmu.write("SOUR:POW %fdBm" % mv_to_dBm(a))
    spsmu.write("SOUR:ROSC:SOUR %s" %clk_mode)
    spsmu.write("OUTP:STAT ON")

def set_frequency(spsmu, f):
    spsmu.write("SOUR:FREQ:CW %.9f MHz" % f)

def set_amplitude(spsmu, a):
    spsmu.write("SOUR:POW %fdBm" % mv_to_dBm(a))

def error_find(spsmu):
    print(spsmu.query("SYSTem:ERRor:ALL?"))

def close(spsmu):
    spsmu.write("OUTP:STAT OFF")
    spsmu.write("UNL 72349234")