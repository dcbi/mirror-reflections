# mirrors.py

Given multiple mirrors arranged in a straight line, `mirrors.py` can calculate:
- the angles of the light rays reflected from the front and back surfaces of each mirror with respect to the optical axis, given the wedge angles of the each surface
- the angle of the light ray transmitted through all the mirrors, with respect to the optical axis
- the absolute (i.e. not relative) wedge angles of each surface, given the measured reflections
- the optimal orientation of each mirror, given their wedge angles, that minimizes the transmitted angle

### Coordinates
The z-axis lies along the optical axis, with the positive direction pointing from the first mirror to the last mirror. This is chosen so that if one is looking down the negative z-direction at a detector screen before the first mirror, it will show the reflected rays upon a right-handed xy-plane. Similarly, standing in front of the last mirror and looking at it down the negative z-axis, the transmitted light is observed with respect to right-handed x and y axes.

For a light ray incident on the surface of a mirror, the angle is measured with respect to the optical axis. The x or y component of the angle is positive if the angle inclines towards the positive x or y axis, respectively. The x or y component of the wedge angle of a mirror's surface is measured with respect to the x or y axis, respectively, and is positive in it inclines towards the positive z axis (this is defined so a positive wedge will cause a positive reflection).

### Assumptions
It is assumed that the distances between the mirrors, the thicknesses of the mirrors, and all relevant angles are small enough so that light rays never diverge far enough to miss a mirror (that is, the mirrors have effectively infinite diameter).

## Usage
Set up an "optics table" by creating an object of the `Optics` class. Optionally pass the refractive index of the medium outside the mirrors.
```python
optics = mirrors.Optics(refractiveIndex=1)
```

Add mirrors in order using the `.add_mirror()` method. Pass the front and back wedge angles, and optionally the refractive index. Each wedge angle can be a number or a 2-element list/tuple for the X and Y directions.
```python
optics.add_mirror(frontWedge1, backWedge1, refractiveIndex=1.5)
optics.add_mirror(frontWedge2, backWedge2, refractiveIndex=1.5)
⋮
```

You can also add a `Mirror` object itself, or multiple at the same time.
```python
m1 = mirrors.Mirror(frontWedge1, backWedge1)
m2 = mirrors.Mirror(frontWedge2, backWedge2)
⋮
optics.add_mirror(m1)
optics.add_mirror(m2, m3, ...)
```
### Calculating reflection/transmission angles
Calculate the reflection angles with the method `mirrors.Optics.reflections_angles()`, and the transmitted ray angle with `mirrors.Optics.transmission_angle()`. Optionally pass the incident angle of the initial ray hitting the front surface of the first mirror and whether or not to use the small angle approximation (that is, sin x = x). If not using the small angle approximation, the units of the angles must be in radians (not even microradians).
```python
reflections = optics.reflection_angles(incident=0, approx=True)
transmitted = optics.transmission_angle(incident=0, approx=True)
```

A numpy array is returned. If there are *m* number of mirrors with *m>1* and if both the x and y directions of the wedge angles were given for each mirror, then the shape of the reflections array is (*m*,2,2). If only a single number is given for each wedge angle, then the shape of the reflections array (*m*,2). If there is only a single mirror and both X and Y directions of wedge angles are given, then the shape is (2,2). If only a single number is given for the wedge angles, the shape is (2,). The shape of the transmitted angle array is (2,) if both x and y directions of the wedge angles were given. Otherwise it is 0-dimensional array.

### Calculating wedge angles
To calculate the wedge angles from measured reflections, call the function `mirrors.wedges_from_reflections()`. Pass an array of reflection angles, a list of refractive indices, and optionally whether to use the small-angle approximation. The shape of the array holding the measured reflections must be in the same shape as if it were returned from the `Optics.reflection_angles()` method described above. A `scipy.optimize.OptimizeResult` object is returned.

### Calculating the optimal orientation
The optimal orientation is specified by the angles by which to rotate each mirror such that the total angle of the transmitted light ray is minimized. To calculate the rotation angles, call the function `mirrors.minimize_transmitted_angle()`. Pass any `Optics` object. A `scipy.optimize.OptimizeResult` object is returned.

