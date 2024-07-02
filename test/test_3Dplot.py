'''
    测试画三维的图
    Li Jie 2024/06/29
'''
import numpy as np
import matplotlib.pyplot as plt

n = 10
x = np.zeros(n+1)
y = np.zeros(n+1)
z = np.zeros((n+1, n+1))

for i in range(n+1):
    v_l = 0.5 + (0.7 - 0.5) / n * i
    x[i] = v_l
    for j in range(n+1):
        v_s = 0.5 + (0.7 - 0.5) / n * j
        y[j] = v_s
        z[i, j] = (v_l - 0.6)**2 + (v_s - 0.6)**2

x, y = np.meshgrid(x, y)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(x, y, z, cmap='viridis')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()
