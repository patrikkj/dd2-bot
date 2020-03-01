import random

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

import dd2.models as models
import dd2.utils as utils

plt.rcParams["figure.figsize"] = (9,7)
plt.rcParams['lines.linewidth'] = 0.8
plt.rcParams['lines.markersize'] = np.sqrt(10)
plt.rcParams['legend.fontsize'] = 5

def _get_min_max(arr):
    bounds = min(arr), max(arr)
    diff = abs(bounds[1] - bounds[0])
    return bounds[0] - 0.1*diff, bounds[1] + 0.1*diff

# Initialization
fig = plt.figure()
fig.suptitle('Parametric spline interpolation')
fig.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.5,
            wspace=0.35)
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(3, 2, 2)
ax3 = fig.add_subplot(3, 2, 4)
ax4 = fig.add_subplot(3, 2, 6)

# coords = np.array([
#     [ 2113.61352539, -2593.7824707],
#     [-1665.44445801, -2609.94116211],
#     [ 1658.87597656, -2578.39038086],
#     [ 3432.31713867, -3670.53564453],
#     [ 5451.61669922, -2572.21459961],
#     [ 5618.70898438, -1142.64746094],
#     [10086.06347656,  2834.65942383],
#     [ 7449.1953125 ,    55.56529999],
#     [ 9784.46289062,  -583.81481934],
#     [11389.95800781, -3292.16845703],
#     [12941.85742188, -3681.58203125],
#     [14431.94335938, -2343.82104492],
#     [14085.1640625 ,   595.24334717],
#     [10669.45507812,  4093.30395508],
#     [ 7983.41650391,  5230.53564453],
#     [ 6523.53808594,  6959.10302734],
#     [ 4550.8359375 ,  7122.24169922],
#     [ 7876.765625  ,  5165.91308594],
#     [ 6541.00341797,  2747.17333984],
#     [ 3248.57641602,  2808.2668457 ],
#     [ 1620.58691406,  4361.48388672],
#     [ -974.15405273,  3051.27124023],
#     [-2790.51074219,  3365.57348633],
#     [-3272.70263672,  5118.20507812],
#     [-2319.3996582 ,  6213.00390625],
#     [  140.05076599,  7121.75097656]
# ])

# coords = np.array([
#     [ 1658.87597656, -2578.39038086],
#     [ 3432.31713867, -3670.53564453],
#     [ 5451.61669922, -2572.21459961],
#     [ 5618.70898438, -1142.64746094],
#     [ 6735.        ,  -148.        ],
#     [ 7852.        ,   846.        ],
#     [ 8969.        ,  1840.        ],
#     [10086.06347656,  2834.65942383]
# ])


coords = np.array([[ 2.18235254e+03, -4.79393457e+03,  1.41781775e+03],
       [ 1.88943311e+03, -2.65706738e+03, -1.30375702e+02],
       [ 3.02378845e+02, -2.59267944e+03, -2.90524811e+02],
       [-1.38347998e+03, -2.88529370e+03, -2.90524811e+02],
       [-1.74261890e+03, -4.59236865e+03, -2.90524811e+02],
       [-1.81200842e+03, -6.32011426e+03, -3.69454712e+02],
       [-1.74956567e+03, -4.11583057e+03, -2.90525024e+02],
       [-1.19233154e+03, -2.87784009e+03, -2.90525024e+02],
       [ 3.99773438e+02, -2.60262964e+03, -2.90525024e+02],
       [ 1.97796338e+03, -2.72632666e+03, -1.11628540e+02],
       [ 3.56424365e+03, -3.63298340e+03,  1.01887222e+02],
       [ 5.04654248e+03, -2.86598193e+03,  2.15521606e+02],
       [ 5.91703223e+03, -7.02835876e+02,  3.10244789e+01],
       [ 7.75570459e+03,  8.36302124e+02, -1.14842880e+02],
       [ 9.75171582e+03,  2.56611499e+03, -3.34343506e+02],
       [ 1.12503428e+04,  3.92966650e+03, -3.86101196e+02],
       [ 1.27915625e+04,  5.33197266e+03, -3.86101196e+02],
       [ 1.08583506e+04,  3.48520142e+03, -3.86101196e+02],
       [ 9.06242188e+03,  1.91714124e+03, -3.28258911e+02],
       [ 7.69385303e+03,  1.75138809e+02, -5.44650316e+00],
       [ 9.33417383e+03, -4.94858398e+02,  2.64718475e+02],
       [ 1.05615186e+04, -1.32199805e+03,  3.75971954e+02],
       [ 1.09271836e+04, -2.91503955e+03,  4.42352356e+02],
       [ 1.22567266e+04, -3.67745337e+03,  6.71165161e+02],
       [ 1.37377715e+04, -3.28544775e+03,  9.69329407e+02],
       [ 1.43253496e+04, -1.95232239e+03,  1.30263074e+03],
       [ 1.42372363e+04,  3.96298790e+01,  1.30263074e+03],
       [ 1.41301533e+04,  1.36044739e+03,  1.30263074e+03],
       [ 1.26645146e+04,  1.96213049e+03,  1.15703345e+03],
       [ 1.14100713e+04,  3.18615479e+03,  7.98559326e+02],
       [ 1.01544844e+04,  4.41129395e+03,  7.98559326e+02],
       [ 9.02361328e+03,  5.31602490e+03,  4.28338470e+02],
       [ 7.33921045e+03,  4.75552295e+03,  1.60383209e+02],
       [ 6.89306396e+03,  3.04291479e+03,  4.67678070e+02],
       [ 5.25334229e+03,  2.77409814e+03,  4.67678070e+02],
       [ 3.60525269e+03,  2.81516675e+03,  4.67678070e+02],
       [ 2.50835547e+03,  3.54520972e+03,  4.67678070e+02],
       [ 1.03353503e+03,  4.14236621e+03,  4.14361511e+02],
       [-3.89909241e+02,  3.26562256e+03,  1.16385368e+02],
       [-2.20820679e+03,  3.06943872e+03,  1.16385368e+02],
       [-3.05767920e+03,  4.24879297e+03, -1.68247056e+00],
       [-2.73114355e+03,  5.86435645e+03, -1.98649307e+02],
       [-1.32912891e+03,  6.33968945e+03, -2.01029343e+02],
       [-1.40281372e+02,  7.02561719e+03, -2.01390686e+02],
       [-1.51003589e+03,  6.29854736e+03, -2.01122284e+02],
       [-3.04489258e+03,  5.61180420e+03, -1.98662338e+02],
       [-3.09388794e+03,  4.10062598e+03,  5.64714279e+01],
       [-8.43397583e+02,  1.71678796e+03,  1.16385368e+02],
       [ 7.54691223e+02,  1.35565039e+03,  1.16385368e+02],
       [ 2.54214355e+03,  1.33466394e+03,  3.60036011e+01],
       [ 5.12257227e+03,  7.06274841e+02, -3.49733551e+02]])

w = np.power(np.array([1, 3, 1, 2, 1, 1, 1, 2, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 3, 1, 3,
       2, 2, 2, 2, 1, 2, 2, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 2, 1, 1,
       1, 2, 2, 3, 1, 1, 1]), 1)

p = models.path.Path(coords, smooth_factor=1, n_factor=100)
p_w = models.path.Path(coords, weights=w, smooth_factor=1, n_factor=100)

# Generate point
x_lower, x_upper = _get_min_max(p.x)
x_diff = x_upper - x_lower

y_lower, y_upper = _get_min_max(p.y)
y_diff = y_upper - y_lower

base = [x_lower + random.random()*x_diff, y_lower + random.random()*y_diff]

ax1.title.set_text('2D grid')
ax1.set_xlabel('x')
ax1.set_ylabel('y')
ax1.set_xlim(*_get_min_max(p.x))
ax1.set_ylim(*_get_min_max(p.y))
ax1.grid(True)
ax1.set_aspect('equal')

ax2.title.set_text('1st order derivatives')
ax2.set_xlabel('t')
ax2.set_ylabel('ddx')
ax2.set_xlim(*_get_min_max(p.t))
ax2.set_ylim(*_get_min_max(p.derivatives.flatten()))
ax2.grid(True)

ax3.title.set_text('2nd order derivatives')
ax3.set_xlabel('t')
ax3.set_ylabel('d2dx')
ax3.set_xlim(*_get_min_max(p.t))
ax3.set_ylim(*_get_min_max(p.derivatives_2.flatten()))
ax3.grid(True)

ax4.title.set_text('Theta')
ax4.set_xlabel('t')
ax4.set_ylabel('θ')
ax4.set_xlim(*_get_min_max(p.t))
ax4.set_ylim(*_get_min_max(utils.math.get_angle(*p.derivatives)))
ax4.grid(True)


def animate(i):
    global base
    speed = 0.3
    head = int(np.floor(p.n * (speed*((i+1)+1)%100*1.4) / 100)) + 1
    # head = int(p.n)
    _head = min(head-1, p.n - 1)

    base[0] += (random.random() - 0.5)*0.2*x_diff
    base[1] += (random.random() - 0.5)*0.2*y_diff 
    base[0] = max(min(base[0], x_upper), x_lower)
    base[1] = max(min(base[1], y_upper), y_lower)
    base = np.array(base)

    # Slices
    t = p.t[:head]
    solutions_w = p_w.solutions[:,:head]
    solutions = p.solutions[:,:head]
    derivatives = p.derivatives[:,:head]
    derivatives_2 = p.derivatives_2[:,:head]
    angles = utils.math.get_angle(*derivatives)
    p_angles = utils.math.get_angle(*p.derivatives)
    point, _, _, _ = p.find_nearest_point(base)

    def eval_tangent(delta):
        _head = min(head-1, p.n)
        return solutions[:,_head] + delta*derivatives[:,_head]

    # Plotting
    ax1.legend(("Data points", "Interpolation (k=3)"), loc=1)
    line1_args = []
    line1_args.extend([p.x, p.y, 'bo'])
    line1_args.extend([p.solutions[0], p.solutions[1], 'g,'])
    line1_args.extend([*solutions[:,_head], 'ro'])
    # line1_args.extend([solutions_w[0], solutions_w[1], 'g--'])
    # line1_args.extend([*point, 'rx'])
    # line1_args.extend([*base, 'ro'])
    # line1_args.extend([*list(zip(base, point))])
    # line1_args.extend([*list(zip(eval_tangent(-0.1), eval_tangent(0.1)))])
    line1 = ax1.plot(*line1_args)
    
    ax2.legend(("dx/dt", "dy/dt"), loc=1)
    line2_args = []
    line2_args.extend([p.t, p.derivatives[0], 'g'])
    line2_args.extend([p.t, p.derivatives[1], 'b'])
    line2_args.extend([(t[-1], t[-1]), ax2.get_ylim(), 'k'])
    line2 = ax2.plot(*line2_args)
    
    ax3.legend(("d2x/dt2", "d2y/dt2"), loc=1)
    line3_args = []
    line3_args.extend([p.t, p.derivatives_2[0], 'g'])
    line3_args.extend([p.t, p.derivatives_2[1], 'b'])
    line3_args.extend([(t[-1], t[-1]), ax3.get_ylim(), 'k'])
    line3 = ax3.plot(*line3_args)
    
    ax4.legend(("Angle (relative)",), loc=1)
    line4_args = []
    line4_args.extend([p.t, p_angles, 'g'])
    line4_args.extend([(t[-1], t[-1]), ax4.get_ylim(), 'k'])
    line4 = ax4.plot(*line4_args)
    return np.concatenate((line1, line2, line3, line4))

ani = animation.FuncAnimation(
    fig, animate, interval=10, blit=True, save_count=50)
plt.show()
