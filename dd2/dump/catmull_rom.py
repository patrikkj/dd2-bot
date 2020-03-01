import numpy
import pylab as plt

def CatmullRomSpline(P0, P1, P2, P3, nPoints=100):
    """
    P0, P1, P2, and P3 should be (x,y) point pairs that define the Catmull-Rom spline.
    nPoints is the number of points to include in this curve segment.
    """
    # Convert the points to numpy so that we can do array multiplication
    P0, P1, P2, P3 = map(numpy.array, [P0, P1, P2, P3])

    # Calculate t0 to t4
    alpha = 0.5
    def tj(ti, Pi, Pj):
        xi, yi = Pi
        xj, yj = Pj
        return (((xj-xi)**2 + (yj-yi)**2)**0.5)**alpha + ti

    t0 = 0
    t1 = tj(t0, P0, P1)
    t2 = tj(t1, P1, P2)
    t3 = tj(t2, P2, P3)

    # Only calculate points between P1 and P2
    t = numpy.linspace(t1, t2, nPoints)

    # Reshape so that we can multiply by the points P0 to P3
    # and get a point for each value of t.
    t = t.reshape(len(t), 1)
    print(t)
    A1 = (t1-t)/(t1-t0)*P0 + (t-t0)/(t1-t0)*P1
    A2 = (t2-t)/(t2-t1)*P1 + (t-t1)/(t2-t1)*P2
    A3 = (t3-t)/(t3-t2)*P2 + (t-t2)/(t3-t2)*P3
    print(A1)
    print(A2)
    print(A3)
    B1 = (t2-t)/(t2-t0)*A1 + (t-t0)/(t2-t0)*A2
    B2 = (t3-t)/(t3-t1)*A2 + (t-t1)/(t3-t1)*A3

    C = (t2-t)/(t2-t1)*B1 + (t-t1)/(t2-t1)*B2
    return C

def CatmullRomChain(P):
    """
    Calculate Catmull–Rom for a chain of points and return the combined curve.
    """
    sz = len(P)

    # The curve C will contain an array of (x, y) points.
    C = []
    for i in range(sz-3):
        c = CatmullRomSpline(P[i], P[i+1], P[i+2], P[i+3])
        C.extend(c)

    return C

# Define a set of points for curve to go through
# Points = [[0, 1.5], [2, 2], [3, 1], [4, 0.5], [5, 1], [6, 2], [7, 3]]


x = [2113.613525390625, -1665.4444580078125, 1658.8759765625, 3432.317138671875, 5451.61669921875, 5618.708984375, 10086.0634765625, 7449.1953125, 9784.462890625, 11389.9580078125, 12941.857421875, 14431.943359375, 14085.1640625, 10669.455078125, 7983.41650390625, 6523.5380859375, 4550.8359375, 7876.765625, 6541.00341796875, 3248.576416015625, 1620.5869140625, -974.154052734375, -2790.5107421875, -3272.70263671875, -2319.399658203125, 140.05076599121094]
y = [-2593.782470703125, -2609.941162109375, -2578.390380859375, -3670.53564453125, -2572.214599609375, -1142.6474609375, 2834.659423828125, 55.56529998779297, -583.8148193359375, -3292.16845703125, -3681.58203125, -2343.821044921875, 595.2433471679688, 4093.303955078125, 5230.53564453125, 6959.10302734375, 7122.24169921875, 5165.9130859375, 2747.17333984375, 2808.266845703125, 4361.48388671875, 3051.271240234375, 3365.573486328125, 5118.205078125, 6213.00390625, 7121.7509765625]
points = list(zip(x, y))

# Calculate the Catmull-Rom splines through the points
c = CatmullRomChain(points)

# Convert the Catmull-Rom curve points into x and y arrays and plot
x, y = zip(*c)
plt.plot(x, y)

# Plot the control points
px, py = zip(*points)
plt.plot(px, py, 'or')

plt.show()