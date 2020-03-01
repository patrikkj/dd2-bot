import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
from scipy import interpolate
plt.rcParams["figure.figsize"] = (10,8)
plt.rcParams['lines.linewidth'] = 0.8
plt.rcParams['lines.markersize'] = np.sqrt(10)

def _get_min_max(arr):
    bounds = min(arr), max(arr)
    diff = abs(bounds[1] - bounds[0])
    return bounds[0] - 0.1*diff, bounds[1] + 0.1*diff


class SubplotAnimation(animation.TimedAnimation):
    def __init__(self):
        fig = plt.figure()
        fig.suptitle('Parametric spline interpolation')
        fig.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.5,
                    wspace=0.35)
        self.ax1 = fig.add_subplot(1, 2, 1)
        self.ax2 = fig.add_subplot(3, 2, 2)
        self.ax3 = fig.add_subplot(3, 2, 4)
        self.ax4 = fig.add_subplot(3, 2, 6)

        self.x = np.array([2113.613525390625, -1665.4444580078125, 1658.8759765625, 3432.317138671875, 5451.61669921875, 5618.708984375, 10086.0634765625, 7449.1953125, 9784.462890625, 11389.9580078125, 12941.857421875, 14431.943359375, 14085.1640625, 10669.455078125, 7983.41650390625, 6523.5380859375, 4550.8359375, 7876.765625, 6541.00341796875, 3248.576416015625, 1620.5869140625, -974.154052734375, -2790.5107421875, -3272.70263671875, -2319.399658203125, 140.05076599121094])
        self.y = np.array([-2593.782470703125, -2609.941162109375, -2578.390380859375, -3670.53564453125, -2572.214599609375, -1142.6474609375, 2834.659423828125, 55.56529998779297, -583.8148193359375, -3292.16845703125, -3681.58203125, -2343.821044921875, 595.2433471679688, 4093.303955078125, 5230.53564453125, 6959.10302734375, 7122.24169921875, 5165.9130859375, 2747.17333984375, 2808.266845703125, 4361.48388671875, 3051.271240234375, 3365.573486328125, 5118.205078125, 6213.00390625, 7121.7509765625])
        self.w = np.ones(len(self.x))
#
        self.x = np.array([1658.8759765625, 3432.317138671875, 5451.61669921875, 5618.708984375, 6735, 7852, 8969,  10086.0634765625])
        self.y = np.array([-2578.390380859375, -3670.53564453125, -2572.214599609375, -1142.6474609375, -148, 846, 1840,   2834.659423828125])
        self.w = np.array([1, 2, 2, 2, 1, 1, 1, 1])
        m = len(self.x)
        self.tck, self.u = interpolate.splprep([self.x, self.y], self.w, s=10000*(m+(2*m)**0.5), k=3)

        self.u_new = np.arange(0, 1, 0.0001)
        self.out = interpolate.splev(self.u_new, self.tck)
        self.out_d1 = interpolate.splev(self.u_new, self.tck, der=1)
        self.out_d2 = interpolate.splev(self.u_new, self.tck, der=2)
        self.thetas = 360*np.arctan2(self.out_d1[1], self.out_d1[0])/np.pi

        self.ax1.title.set_text('2D grid')
        self.ax1.set_xlabel('x')
        self.ax1.set_ylabel('y')
        self.ax1.set_xlim(*_get_min_max(self.x))
        self.ax1.set_ylim(*_get_min_max(self.y))
        self.ax1.grid(True)
        self.ax1.set_aspect('equal')

        self.ax2.title.set_text('1st order derivatives')
        self.ax2.set_xlabel('t')
        self.ax2.set_ylabel('ddx')
        self.ax2.set_xlim(*_get_min_max(self.u_new))
        self.ax2.set_ylim(*_get_min_max(np.concatenate((self.out_d1[1], self.out_d1[0]))))
        self.ax2.grid(True)

        self.ax3.title.set_text('2nd order derivatives')
        self.ax3.set_xlabel('t')
        self.ax3.set_ylabel('d2dx')
        self.ax3.set_xlim(*_get_min_max(self.u_new))
        self.ax3.set_ylim(*_get_min_max(np.concatenate((self.out_d2[1], self.out_d2[0]))))
        self.ax3.grid(True)

        self.ax4.title.set_text('Theta')
        self.ax4.set_xlabel('t')
        self.ax4.set_ylabel('θ')
        self.ax4.set_xlim(*_get_min_max(self.u_new))
        self.ax4.set_ylim(*_get_min_max(self.thetas))
        self.ax4.grid(True)

        animation.TimedAnimation.__init__(self, fig, interval=1, blit=True)

    def _draw_frame(self, framedata):
        i = framedata
        print(i)
        # head_slice = (self.t > self.t[i] - 1.0) & (self.t < self.t[i])
        speed = 100
        n = 1000
        self.u_new = np.arange(0, ((i*speed)%n)/n + 1/n, 1/n)
        self.out = interpolate.splev(self.u_new, self.tck)
        self.out_d1 = interpolate.splev(self.u_new, self.tck, der=1)
        self.out_d2 = interpolate.splev(self.u_new, self.tck, der=2)
        self.thetas = 360*np.arctan2(self.out_d1[1], self.out_d1[0])/np.pi
        
        self.ax1.legend(("Data points", "Interpolation (k=3)"))
        self.line1 = self.ax1.plot(self.x, self.y, 'bo', self.out[0], self.out[1], 'g')
        
        self.ax2.legend(("dy/dt", "dx/dt"))
        self.line2 = self.ax2.plot(self.u_new, self.out_d1[1], 'g', self.u_new, self.out_d1[0], 'b')
        
        self.ax3.legend(("d2y/dt2", "d2x/dt2"))
        self.line3 = self.ax3.plot(self.u_new, self.out_d2[1], 'g', self.u_new, self.out_d2[0], 'b')
        
        self.ax4.legend(("Angle (degrees)",))
        self.line4 = self.ax4.plot(self.u_new, self.thetas, 'g')

        self._drawn_artists = [self.line1, self.line2, self.line3]

    def new_frame_seq(self):
        return iter(range(self.u_new.size))


ani = SubplotAnimation()
# ani.save('test_sub.mp4')
plt.show()