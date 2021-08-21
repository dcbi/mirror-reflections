# mirrors.py

Given multiple mirrors arranged in a straight line, `mirrors.py` can calculate:
- the angles of the light rays reflected from the front and back surfaces of each mirror with respect to the optical axis, given the tilt angles of the each surface,
- the angle of the light ray transmitted through all the mirrors, with respect to the optical axis,
- the tilt angles of each surface, given the measured reflections,
- the optimal orientation of each mirror, given their wedge angles, that minimizes the transmitted angle.

### Coordinates
The z-axis lies along the optical axis, with the positive direction pointing from the first mirror to the last mirror. This is chosen so that if one is looking down the negative z-direction at a detector screen before the first mirror, it will show the reflected rays upon a right-handed xy-plane. Similarly, standing in front of the last mirror and looking at it down the negative z-axis, the transmitted light is observed with respect to right-handed x and y axes.

For a light ray incident on the surface of a mirror, the angle is measured with respect to the optical axis. The x or y component of the angle is positive if the angle inclines towards the positive x or y axis, respectively.

The x or y component of the wedge angle of a mirror's surface is measured with respect to the x or y axis, respectively. The angle is considered positive if it inclines towards the positive z axis (this is defined so a positive wedge will cause a positive reflection).

### Assumptions
It is assumed that the distances between the mirrors, the thicknesses of the mirrors, and all relevant angles are small enough so that light rays never diverge far enough to miss a mirror (that is, the mirrors have effectively infinite diameter).

## Dependencies
 - Numpy
 - Scipy.optimize

## Usage
Set up an "optics table" by creating an object of the `Optics` class. Optionally pass the refractive index of the medium outside the mirrors.
```python
optics = Optics(refractiveIndex=1)
```

Add mirrors in order using the `.add_mirror()` method. Pass the front and back wedge angles, and optionally the refractive index. Each wedge angle can be a number or a 2-element list/tuple for the X and Y directions.
```python
optics.add_mirror(frontWedge1, backWedge1, refractiveIndex=1.5)
optics.add_mirror([frontWedgeX, frontWedgeY], [backWedgeX, backWedgeY], refractiveIndex=1.5)
⋮
```

You can also add a `Mirror` object itself, or multiple at the same time.
```python
m1 = Mirror(frontWedge1, backWedge1)
m2 = Mirror(frontWedge2, backWedge2)
⋮
optics.add_mirror(m1)
optics.add_mirror(m2, m3, ...)
```
### Calculating reflection/transmission angles
Calculate the reflection angles with the method `Optics.reflections_angles()`, and the transmitted angle with `Optics.transmission_angle()`. Optionally pass the incident angle of the initial ray hitting the first mirror and whether or not to use the small angle approximation (that is, sin x = x). If not using the small angle approximation, the units of the angles must be in radians (NOT μrads, for example).
```python
reflections = optics.reflection_angles(incident=0, approx=True)
transmitted = optics.transmission_angle(incident=0, approx=True)
```

A numpy.ndarray object is returned, the shape/dimension of which is determined by the number of mirrors and whether or not the wedge angles were given in both X and Y. If wedge angles are given in both X and Y, call it '2D-mirrors'. Otherwise, call it '1D-mirrors'.

In the case of *m* 2D-mirrors with *m>1*, the shape of the reflections array is (*m*,2,2). The indices go as \[mirror, surface, X or Y\]. For example:
```python
reflections[3,0,1]
```
is the angle of reflection from the 3rd mirror's front surface in Y.

In the case of *m* 1D-mirrors with *m>1*, the shape of the reflections array (*m*,2). The indices go as \[mirror, surface\].

In the case of a single 2D-mirror, the shape of the reflections array is (2,2). The indices go as \[surface, X or Y\]. In the case of a single 1D-mirror, the shape is (2,) with its singular index representing the front or back surface.

The transmitted angle is either shaped (2,) or is 0-dimensional, which is a single number. It is shaped (2,) for 2D-mirrors, representing the angle in X and Y. 

### Calculating wedge angles
To calculate the wedge angles from measured reflections, call the function `wedges_from_reflections()`. Pass an array of reflection angles, a list of refractive indices, and optionally whether or not to use the small-angle approximation.
```python
wedgeResults = wedges_from_reflections(reflection_array, index_array, approx=True)
```
It is best to shape the array of reflection angles passed to the function to match what would be returned by the `Optics.reflection_angles()` method described above, although it is not necessary as long as the the array order the numbers in a way that it can be reached via `numpy.ndarray.reshape()`.

For example, for three 2D-mirrors, the array should be (3,2,2). However, you can also make it (6,2) with the rows alternating between front and back surfaces and ordered by mirror.

A `scipy.optimize.OptimizeResult` object is returned. The attribute `scipy.optimize.OptimizeResult.x` stores the result array. The shape is as described above, but instead of each angle being a reflection, it is a tilt of a mirror surface.

### Calculating the optimal orientation
The optimal orientation is specified by the angles by which to rotate each mirror such that the total angle of the transmitted light ray is minimized. To calculate these angles, call the function `minimize_transmitted_angle()`. Pass any `Optics` object. A `scipy.optimize.OptimizeResult` object is returned. The attribute `scipy.optimize.OptimizeResult.x` stores the list of rotation angles.

