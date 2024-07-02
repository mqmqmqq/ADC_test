'''
    尝试电源板初始化
    Li Jie 2024/06/27
'''
import test_lib.voltage_initial as voltage_initial
import pyvisa


rm = pyvisa.ResourceManager()
find_device = rm.list_resources()
print(find_device)

spsmu = rm.open_resource('ASRL3::INSTR')
spsmu.baud_rate = 921600

voltage_initial.v_initial(spsmu)
