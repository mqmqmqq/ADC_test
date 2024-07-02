'''
    测试电源板扫描电压
    Li Jie 2024/06/27
'''
import time
import pyvisa

rm = pyvisa.ResourceManager()
find_device = rm.list_resources()
print(find_device)

spsmu = rm.open_resource('ASRL3::INSTR')

spsmu.baud_rate = 921600

for i in range(10):
    v1 = i*0.04+0.4
    spsmu.write("sour:volt 9, %f" %v1 )
    print(spsmu.query("meas:volt? 9" ))
    for j in range(10):
        v2 = j*0.04+0.4
        spsmu.write("sour:volt 8, %f" %v2 )
        print(spsmu.query("meas:volt? 8" ))
        time.sleep(20)