import numpy as np
from scipy import optimize

class Mirror():

    def __init__(self, frontWedge, backWedge, refractiveIndex=1.5):
        self.Wedge = np.array([ frontWedge, backWedge ])
        self.refractiveIndex = refractiveIndex

    def clock(self, angle):
        R = np.array([ [np.cos(angle), -np.sin(angle)] , [np.sin(angle), np.cos(angle)] ])
        uFront = np.array([ self.Wedge[0,1], -self.Wedge[0,0] ])
        uBack = np.array([ self.Wedge[1,1], -self.backWedge[1,0] ])
        Ru_front = R.dot( uFront )
        Ru_back = R.dot( uBack )
        self.Wedge[0,1] = Ru_front[0]
        self.Wedge[0,0] = -Ru_front[1]
        self.Wedge[1,1] = Ru_back[0]
        self.Wedge[1,0] = -Ru_back[1]

def angles(incident=0, wedge=0, n1=1, n2=1, approx=True):

    reflect = 2 * wedge - incident

    if approx:
        _trans__ = - (n1/n2) * (incident - wedge)
    else:
        __trans__ = np.arcsin( - (n1/n2) * np.sin(incident - wedge) )

    trans = __trans__ - wedge

    return np.array([reflect, trans])

class Optics():
    def __init__(self, n=1):
        self.refractiveIndex = n
        self.mirror = list()

    def add_mirror(self, *args):
        if isinstance(args[0], Mirror):
            for x in args: self.mirror.append(x)
        else: self.mirror.append( Mirror(*args) )

    def reflection_angles(self, incident=0, approx=True):
        m = len(self.mirror)
        RTS = list()                     ## Reflection and Transmission angles per Surface per mirror

        for i in range(m):
            if i == 0:
                first = angles(incident, self.mirror[i].Wedge[0], self.refractiveIndex, self.mirror[i].refractiveIndex, approx)
            else:
                first = angles(-RTS[i-1][1][1], self.mirror[i].Wedge[0], self.refractiveIndex, self.mirror[i].refractiveIndex, approx)

            second = angles(-first[1], self.mirror[i].Wedge[1], self.mirror[i].refractiveIndex, self.refractiveIndex, approx)

            RTS.append( (first,second) )

        ### RTS [mirror #, surface #, R or T (, X or Y)]
        RTS = np.array( RTS )

        R = RTS[0,0,0]
        next = RTS[0,1,0]
        dim = R.ndim
        if dim:
            R = np.vstack((R, angles(-next, -self.mirror[0].Wedge[0], self.mirror[0].refractiveIndex, self.refractiveIndex, approx)[1] ))
        else:
            R = np.hstack((R, angles(-next, -self.mirror[0].Wedge[0], self.mirror[0].refractiveIndex, self.refractiveIndex, approx)[1] ))

        for i in range(1,m):                 ## for each mirror
            for s in (0,1):             ## for each surface, front and back
                next = RTS[i,s,0]
                ## sets incoming angle to be either the reflected angle of the back or front surface of the current mirror

                ## if back surface, propagate to front surface
                if s:
                    next = angles(-next, -self.mirror[i].Wedge[0], self.mirror[i].refractiveIndex, self.refractiveIndex, approx)[1]

                ## propagate through all previous mirrors
                for j in range(i-1,-1,-1):
                    next = angles( -next, -self.mirror[j].Wedge[1], self.refractiveIndex, self.mirror[j].refractiveIndex, approx)[1]
                    next = angles( -next, -self.mirror[j].Wedge[0], self.mirror[j].refractiveIndex, self.refractiveIndex, approx)[1]

                if dim: R = np.vstack( (R, next) )
                else: R = np.hstack( (R, next) )

        if m==1: return R
        else:
            if dim: return R.reshape(m,2,2)
            else: return R.reshape(m,2)

    def transmission_angle(self, incident=0, approx=True):
        m = len(self.mirror)
        T = list()             ## Transmitted angle per surface per mirror

        for i in range(m):
            if i == 0:
                first = angles(incident, self.mirror[i].Wedge[0], self.refractiveIndex, self.mirror[i].refractiveIndex, approx)[1]
            else:
                first = angles(-T[i-1][1], self.mirror[i].Wedge[0], self.refractiveIndex, self.mirror[i].refractiveIndex, approx)[1]

            second = angles(-first, self.mirror[i].Wedge[1], self.mirror[i].refractiveIndex, self.refractiveIndex, approx)[1]

            T.append( (first,second) )

        return T[-1][1]

    def __getitem__(self, key):
        return self.mirror[key]

    def __iter__(self):
        return opticsiter(self)

    def clock(self, *rotation_angle, copy=False):
        if copy:
            opt = self
            for i in range(len(opt.mirror)):
                opt.mirror[i].clock(rotation_angle[i])
            return opt
        else:
            for i in range(len(self.mirror)):
                self.mirror[i].clock(rotation_angle[i])

class opticsiter():
    def __init__(self, optics_obj):
        self.opt = optics_obj
        self.index = 0
    def __next__(self):
        if self.index < len(self.opt.mirror):
            result = self.opt.mirror[self.index]
            self.index += 1
            return result
        else: raise StopIteration

def reflection_matrix(m, n_air=1, n_mir=1.5):
    R = np.zeros((2*m,2*m))
    alpha = n_mir / n_air
    beta = alpha - 1

    for i in range(2*m):
        if i % 2: R[i,i] = alpha
        else: R[i,i] = 1

        for j in range(i-1,-1,-1):
            if j % 2: R[i,j] = beta
            else: R[i,j] = -beta

    return 2*R

def transmission_angle(n1, n2, m):
    return np.sum([])

def minimize_transmitted_angle(optics):
    m = len(optics.mirror)

    def clock_and_transmit(*rotation_angle):
        clocked = optics.clock(*rotation_angle, True)
        t = clocked.transmission_angle()
        return np.linalg.norm(t)

    bounds = optimize.LinearConstraint(np.identity(m),0,2*np.pi)
    result = optimize.minimize(clock_and_transmit, np.zeros(m), constraints=(bounds))

    return result

def wedges_from_reflections(true_reflections, indices, approx=True):
    indices = np.array(indices)
    m = indices.size
    d = true_reflections.ndim
    s = true_reflections.size
    bounds = optimize.LinearConstraint(np.identity(s), -np.pi/2, np.pi/2)

    testop = Optics()
    if d == 1: testop.add_mirror(0,0,indices)
    elif d == 3:
        for i in range(m): testop.add_mirror((0,0), (0,0), indices[i])
    elif m == 1: testop.add_mirror((0,0), (0,0), indices)
    else:
            testop.add_mirror(0,0,indices[0])
            testop.add_mirror(0,0,indices[1])

    def SumSqDiff(test_wedges):
        test_wedges = test_wedges.reshape((m,2,2))

        for i in range(m): testop.mirror[i].Wedge = test_wedges[i]

        calculated_reflections = testop.reflection_angles(0, approx)
        diff = true_reflections - calculated_reflections
        return np.linalg.norm(diff)**2 

    result = optimize.minimize(SumSqDiff, np.zeros(s), constraints=(bounds))

    return result
