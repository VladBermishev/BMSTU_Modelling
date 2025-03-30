import matplotlib; matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import numpy as np

alpha = math.pi / 4
v0 = 100
r = 10
g = 9.8
current_pos = (0, 0)


def x(t):
    global alpha, v0
    return math.cos(alpha)*v0*t


def y(t):
    global alpha, v0, g
    return (math.sin(alpha)*v0)*t - g*t*t/2


fig, ax = plt.subplots()
t = np.linspace(0, 50, 100)
z0 = list(map(x, t))
z1 = list(map(y, t))

line = ax.scatter(z0[0], z1[0], c="b", label=f'v0 = {v0} m/s')
ax.set(xlim=[0, 10000], ylim=[-1000, 1000], xlabel='Time [s]', ylabel='Z [m]')
ax.legend()


def update(frame):
    data = np.stack([z0[:frame], z1[:frame]]).T
    line.set_offsets(data)
    return line,


ani = animation.FuncAnimation(fig=fig, func=update, frames=100, interval=30)
plt.show()