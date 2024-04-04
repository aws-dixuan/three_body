import numpy as np
from star import star
from system import system
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
threeD = False
delta_t = 0.1
tail_length = 200
stars = []
star1 = star(100.0, [10.0, 10.0, 7.0], [-4.0, -3.4, 10.0], tail_length)
stars.append(star1)
star2 = star(100.5, [-10.0, -10.0, 7.0], [2.3, -0.9, -3.0], tail_length)
stars.append(star2)
star3 = star(130.2, [10.0, -10.0, -3.0], [2.2, 1.8, 8.0], tail_length)
# stars.append(star3)
star4 = star(0.3, [50.0, -70.0, 0.0], [0.0, 0.0, 0.0], tail_length)
# stars.append(star4)
mySystem = system(stars, delta_t=delta_t)
if threeD:
    ax = plt.subplot(projection='3d', proj_type='persp')   # , proj_type='ortho'
else:
    ax = plt.subplot()


def axisEqual3D(ax):
    extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:, 1] - extents[:, 0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize/1.6
    for ctr, dim in zip(centers, 'xyz'):
        getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)


def animate(i):
    plt.cla()
    for star in mySystem.stars:
        position, radius, tail = star.plot()
        if threeD:
            ax.scatter(position[0], position[1], position[2], s=20 * radius ** 2)
            ax.plot3D(tail[:, 0], tail[:, 1], tail[:, 2])
            # hide frame
            ax.set_axis_off()
            # set x, y, z equal ratio
            axisEqual3D(ax)
        else:
            ax.scatter(position[0], position[1], s=20 * radius ** 2)
            ax.plot(tail[:, 0], tail[:, 1])
            # set x, y the same scale
            plt.gca().set_aspect('equal', adjustable='box')
            # axis off
            plt.xticks([])
            plt.yticks([])
            # plt.zticks([])
            # frame off
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
    ax.scatter(0, 0, 0)
    # background color
    # ax.set_facecolor('black')
    # plt.figure(facecolor='black')
    mySystem.update()


ani = FuncAnimation(plt.gcf(), animate, interval=10)
# plt.figure(facecolor='black')
plt.show()

