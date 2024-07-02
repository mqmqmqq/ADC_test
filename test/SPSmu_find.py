'''
    列出可以连接的设备
    Li Jie 2024/06/27
'''

import pyvisa

rm = pyvisa.ResourceManager()
find_device = rm.list_resources()

print(find_device)