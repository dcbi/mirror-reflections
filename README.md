# mirror-reflections
Calculates the angles with respect to the optical axis of the light reflected from the front and back surfaces of multiple mirrors in a straight line, as seen from in front of the first mirror, given the front and back wedge angles and refractive indices of each mirror.

It is assumed that all angles are small enough such that the approximation ``sin(x)=x`` holds and that the distances between mirrors are small enough so that light rays never diverge enough to miss a mirror (that is, the mirrors have effectively infinite diameter).

The sign of angles follows the following convention:
 - the angle of an incident/reflected/transmitted ray is positive if it is above the line parallel to the optical axis and intersecting the point where the ray meets the mirror.
 - a wedge angle is positive if it tilts the mirror such that an incoming ray along the optical axis will reflect at a positive angle (i.e. if light is coming from the left, the top of the mirror tilts to the right and the bottom tilts to the left).

## Usage
Set up an "optical bench" by creating an object of the `Optics` class. Optionally pass the refractive index `n0` of the medium outside the mirrors (defaults to **1** for vacuum).
```python
optics = Optics(n0)
```

Add mirrors in order. Pass the front and back wedge angles, and optionally refractive index (defaults to **1.5** for glass).

```python
optics.add_mirror(front_wedge1, back_wedge1, refractive_index1)
optics.add_mirror(front_wedge2, back_wedge2, refractive_index2)
...
```

Calculate the reflection angles with `.calculate_reflections()`. Optionally pass the incident angle of the initial ray hitting the front surface of the first mirror (default **0**). A list is returned. If there are **m** number of mirrors, the list length is **2m**.

```python
reflections = optics.calculate_reflections(incident)
```

The reverse (calculating the wedge angles from the reflection angles) can be done with the [kiwisolver](https://kiwisolver.readthedocs.io/en/latest/basis/basic_systems.html) package.

