# mirrors.py

Given multiple mirrors arranged in a straight line, each with their own wedge angles and refractive indices, `mirrors.py` calculates the angles of the light rays reflected from the front and back surfaces of each mirror, and the angle of the light ray is transmitted through all the mirrors.

### Coordinates
The z-axis lies along the optical axis, with the positive direction pointing from the first mirror to the last mirror. This is chosen so that if one is looking down the negative z-direction at a detector screen before the first mirror, it will show the reflected rays upon a right-handed xy-plane. Similarly, standing in front of the last mirror, the transmitted light is observed with respect to right-handed x and y axes.

For a light ray incident on the surface of a mirror, the angle is measured with respect to the optical axis. The x or y component of the angle is positive if the angle inclines towards the positive x or y axis, respectively. The x or y component of the wedge angle of a mirror's surface is measured with respect to the x or y axis, respectively, and is positive in it inclines towards the positive z axis (this is defined so a positive wedge will cause a positive reflection).

### Assumptions
It is assumed that all angles are small enough such that the approximation ``sin(x)=x`` holds and that the distances between the mirrors and the thicknesses of the mirrors are small enough so that light rays never diverge enough to miss a mirror (that is, the mirrors have effectively infinite diameter).

## Usage
Set up an "optical bench" by creating an object of the `Optics` class. Optionally pass the refractive index `n0` of the medium outside the mirrors (defaults to **1** for vacuum).
```python
optics = mirrors.Optics(n0)
```

Add mirrors in order using the `.add_mirror()` method. Pass the front and back wedge angles, and optionally refractive index (defaults to **1.5** for glass). Each wedge angle can be a 2-element list for the X and Y direction, or a single number (as if the wedge along one direction is precisely zero).

```python
optics.add_mirror(front_wedge1, back_wedge1, refractive_index1)
optics.add_mirror(front_wedge2, back_wedge2, refractive_index2)
⋮
```

You can add multiple mirrors at once by passing multiple tuples of the above arguments. You can also pass `Mirror` objects, which have the above arguments as their attributes. You can also pass combinations of `Mirror` objects and tuples.

```python
m1 = mirrors.Mirror(fw1, bw1, index1)
optics.add_mirror(m1, (fw2, bw2, index2), ... )
```

Calculate the reflection angles with `.reflections_angles()`, and the transmitted ray angle with `.transmission_angle()`. Optionally pass the incident angle of the initial ray hitting the front surface of the first mirror (default **0**).
```python
reflections = optics.reflection_angles(incident)
transmitted = optics.transmission_angle(incident)
```

A numpy array is returned. If there are **m** number of mirrors, the shape of the reflections array is (m,2) if both the x and y directions of the wedge angles were given for each mirror, and (m,1) if only one direction of the wedge angles was given for each mirror. Similarly, the the shape of the transmitted array is either 1x1 or 1x2.

The reverse calculation (calculating the wedge angles from the reflection angles) can be done with the [kiwisolver](https://kiwisolver.readthedocs.io/en/latest/basis/basic_systems.html) package.

