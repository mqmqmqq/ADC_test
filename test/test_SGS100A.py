'''
    尝试连接和控制SGS100A
    Li Jie 2024/06/28
'''
import pyvisa
import math

fclk = 800
decim = 125
Nsample = 65536
fin   = fclk/decim*(Nsample*16.25+11)/Nsample
vclk  = 0.7
vin   = 0.72

def mv_to_dBm(vin):
    vout = 10*math.log10(20*(vin**2))
    return vout

rm = pyvisa.ResourceManager()
#下面的两个序列需要先运行SPSmu_find来确定，不同电脑会不同
spsmu17 = rm.open_resource('USB0::0x0AAD::0x0088::114817::INSTR')
spsmu16 = rm.open_resource('USB0::0x0AAD::0x0088::114816::INSTR')
print(spsmu17.query("*IDN?"))
print(spsmu16.query("*IDN?"))

spsmu17.baud_rate = 115200

spsmu17.write("*RST")
spsmu16.write("*RST")

spsmu17.write("*CLS")
spsmu16.write("*CLS")

# print(spsmu17.query("LOCK? 72349234"))
# print(spsmu16.query("LOCK? 72349234"))

spsmu17.write("SOUR:OPM NORM")
spsmu16.write("SOUR:OPM NORM")

spsmu17.write("SOUR:FREQ:CW %.9f MHz" % fin)
spsmu16.write("SOUR:FREQ:CW %f MHz" % fclk)

spsmu17.write("SOUR:POW %fdBm" % mv_to_dBm(vin))
spsmu16.write("SOUR:POW %fdBm" % mv_to_dBm(vclk))

# print(spsmu17.query("SOUR:POW:PEP?"))
# print(spsmu16.query("SOUR:POW:PEP?"))

spsmu17.write("SOUR:ROSC:SOUR EXT")
spsmu16.write("SOUR:ROSC:SOUR INT")

spsmu17.write("OUTP:STAT ON")
spsmu16.write("OUTP:STAT ON")


print(spsmu17.query("SYSTem:ERRor:ALL?"))
print(spsmu16.query("SYSTem:ERRor:ALL?"))
#请在此添加断点，防止运行完直接关闭
spsmu17.write("OUTP:STAT OFF")
spsmu16.write("OUTP:STAT OFF")

# spsmu17.write("UNL 72349234")
# spsmu16.write("UNL 72349234")