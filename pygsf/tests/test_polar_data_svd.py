
import numpy as np

from pygsf.orientations.orientations import Plane
from pygsf.mathematics.arrays import svd


plane1 = Plane(90, 0)
plane2 = Plane(90, 5)

# plane to xyz

n_axis_1 = plane1.normAxis()
n_axis_2 = plane2.normAxis()

normal_1 = n_axis_1.toXYZ()
normal_2 = n_axis_2.toXYZ()

print(normal_1)
print(normal_2)

xyzes = (normal_1, normal_2)

# pack tuples into array

a = np.stack(xyzes)
print(type(a))
print(a.shape)

# svd

res = svd(a)

"""
print(type(res))
for res_el in res:
    print(res_el)
"""

u = res[0]
s = res[1]
vh = res[2]

#print(vh)

print("mean", vh[0,:]) # mean value
print("girdle normal", vh[2, :]) # normal to girdle
