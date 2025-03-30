import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import numpy

N = 4
alpha = math.pi/4
r = 0.1
v0 = 10*N
#c = 0.15
c = 0
beta = c * 1.29 * (math.pi * r * r) / 2
p = 7000

m = p * 4/3 * math.pi * r ** 3
#m = N/10
g = 9.8
tau_coefficient = 0.25

wall_start_point = [N, 0]
wall_height = 5
wall_edge_point = [N, 5]


def rungeKutta(f1, f2, to, x_coord, y_coord, tEnd, tau):
    def increment(f, time_t, val, step):
        k0 = step * f(time_t, val)
        k1 = step * f(time_t + step / 2., val + k0 / 2.)
        k2 = step * f(time_t + step / 2., val + k1 / 2.)
        k3 = step * f(time_t + step, val + k2)
        return (k0 + 2. * k1 + 2. * k2 + k3) / 6.
    global v
    t = [to]
    y = [x_coord]
    z = [y_coord]
    while to < tEnd:
        v = math.sqrt(x_coord*x_coord + y_coord * y_coord)
        tau = min(tau, tEnd - to)
        x_coord = x_coord + increment(f1, to, x_coord, tau)
        y_coord = y_coord + increment(f2, to, y_coord, tau)
        to = to + tau
        t.append(to)
        y.append(x_coord)
        z.append(y_coord)
    return numpy.array(t), numpy.array(y), numpy.array(z)

def du(t, u):
    return -beta*u*v/m

def dw(t, w):
    return -g - beta*w*v/m

def X(t):
    global alpha, v0
    return math.cos(alpha)*v0*t


def Y(t):
    global alpha, v0, g
    return (math.sin(alpha)*v0)*t - g*t*t/2

def height(velocity):
    vx0 = velocity * math.cos(alpha)
    vy0 = velocity * math.sin(alpha)

    a, b, c = rungeKutta(du, dw, 0, vx0, vy0, 20, tau_coefficient)
    x = [0]
    y = [0]
    for i in range(len(a)):
        x.append(x[-1] + tau_coefficient * b[i])
        y.append(y[-1] + tau_coefficient * c[i])
    for i in range(len(a)):
        if x[i] - wall_height > wall_height:
            return y[i]



def bin_search(f, val_to_find, bounds, eps=1e-3):
    m = 0
    while (max(bounds) - min(bounds)) > eps:
        m = min(bounds) + (max(bounds) - min(bounds)) / 2
        if(f(m) > val_to_find):
            bounds[1] = m
        elif(f(m) < val_to_find):
            bounds[0] = m
        else:
            return (m, m)
    return bounds

x0 = 0
y0 = 0
vx0 = v0 * math.cos(alpha)
vy0 = v0 * math.sin(alpha)

a, b, c = rungeKutta(du, dw, 0, vx0, vy0, 20, tau_coefficient)
x = [0]
y = [0]
for i in range(len(a)):
    x.append(x[-1] + tau_coefficient * b[i])
    y.append(y[-1] + tau_coefficient * c[i])

current_pos = (0, 0)
t = numpy.linspace(0, 50, 400)
z0 = list(map(X, t))
z1 = list(map(Y, t))

fig, ax = plt.subplots()

wall = plt.plot([wall_start_point[0], wall_edge_point[0]], [wall_start_point[1], wall_edge_point[1]], label=f'Wall', marker='o')
line1 = ax.scatter(x[0], y[0], c="b", label=f'Newton')
line2 = ax.scatter(z0[0], z1[0], c="r", label=f'Galileo')
ax.set(xlim=[-5, 1500], ylim=[0, 400], xlabel='Time [s]', ylabel='Z[m]')
ax.legend()

def update(frame):
    data1 = numpy.stack([x[:frame], y[:frame]]).T
    line1.set_offsets(data1)
    data2 = numpy.stack([z0[:frame], z1[:frame]]).T
    line2.set_offsets(data2)
    return line1, line2


print(f"Newton flight path: {max(filter(lambda val: val[1] > 0, zip(x, y)), key=lambda k: k[0])[0]}")
print(f"Galley flight path: {max(filter(lambda val: val[1] > 0, zip(z0, z1)), key=lambda k: k[0])[0]}")
if N > wall_height:
    res = bin_search(height, 5, [0, 10000])
    print(f"Newton min velocity to pass wall: {(res[1] + res[0]) / 2}")
    print(f"Galley min velocity to pass wall: {math.sqrt((N**2 * g) /(N - 5))}")
else:
    print(f"Newton min velocity to pass wall: No valid solution")
    print(f"Galley min velocity to pass wall: No valid solution")
ani = animation.FuncAnimation(fig=fig, func=update, frames=1000, interval=1)
plt.show()
