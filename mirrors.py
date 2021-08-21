import numpy as np
from scipy import optimize

class Mirror():

    def __init__(self, frontWedge, backWedge, refractiveIndex=1.5):
        self.Wedge = np.array([ frontWedge, backWedge ])
        self.refractiveIndex = refractiveIndex

    def clock(self, angle):
        rotationMatrix = np.array([ [np.cos(angle), -np.sin(angle)] , [np.sin(angle), np.cos(angle)] ])
        frontVector = np.array([ self.Wedge[0,1], -self.Wedge[0,0] ])
        backVector = np.array([ self.Wedge[1,1], -self.backWedge[1,0] ])
        frontRotated = rotationMatrix.dot( frontVector )
        backRotated = rotationMatrix.dot( backVector )
        self.Wedge[0,1] = frontRotated[0]
        self.Wedge[0,0] = -frontRotated[1]
        self.Wedge[1,1] = backRotated[0]
        self.Wedge[1,0] = -backRotated[1]


def angles(incident=0, wedge=0, n1=1, n2=1):
    reflect = 2 * wedge - incident

    transRelative = np.arcsin( - (n1/n2) * np.sin(incident - wedge) )
    trans = transRelative - wedge

    return np.array([reflect, trans])


def reflection_matrix(n_mirs, n_air=1):

    mirrorsRefIndex = np.array(n_mirs)
    m = mirrorsRefIndex.size
    d = mirrorsRefIndex.ndim
    R = np.zeros((2*m,2*m))

    normalizedIndex = mirrorsRefIndex / n_air
    reducedIndex = normalizedIndex - 1

    for i in range(2*m):
        if i % 2:
            if d: R[i,i] = normalizedIndex[i//2]
            else: R[i,i] = normalizedIndex
        else: R[i,i] = 1

        for j in range(i-1,-1,-1):
            if j % 2:
                if d: R[i,j] = reducedIndex[i//2]
                else: R[i,j] = reducedIndex
            else:
                if d: R[i,j] = -reducedIndex[i//2]
                else: R[i,j] = -reducedIndex
    return 2*R


##############################


class Optics():

    def __init__(self, n=1):
        self.refractiveIndex = n
        self.mirror = list()

    def add_mirror(self, *args):
        if isinstance(args[0], Mirror):
            for x in args: self.mirror.append(x)
        else: self.mirror.append( Mirror(*args) )

    def __shape__(self):
        return self.mirror[0].Wedge.shape


    def reflection_angles(self, incident=0, approx=True):
        if approx: return self.reflection_angles_approx(incident)
        else: return self.reflection_angles_exact(incident)

    def reflection_angles_approx(self, incident):
        reflectionMatrix = reflection_matrix( self.getIndexVector(), self.refractiveIndex )
        result = reflectionMatrix @ self.getWedgeVector()
        m = len(self.mirror)
        result = result.reshape( (m,*self.__shape__()) )
        if m == 1: return result[0]
        else: return result

    def reflection_angles_exact(self, incident, units=1):
        if no units == 1:

        m = len(self.mirror)
        shape = self.__shape__()

        RTS = np.zeros((m,2,*shape))            ## "REFELCTED angle and TRANSMITTED angle per mirror SURFACE"
                                                ### the indices are: [mirror, surface, reflection or transmission (, X or Y)]
        for i in range(m):
            if i == 0:
                RTS[i,0] = angles(incident, self.mirror[i].Wedge[0], self.refractiveIndex, self.mirror[i].refractiveIndex, approx)
            else:
                RTS[i,0] = angles(-RTS[i-1,1,1], self.mirror[i].Wedge[0], self.refractiveIndex, self.mirror[i].refractiveIndex, approx)

            RTS[i,1] = angles(-RTS[i,0,1], self.mirror[i].Wedge[1], self.mirror[i].refractiveIndex, self.refractiveIndex, approx)

        reflections = np.zeros((m,*shape))
        reflections[0,0] = RTS[0,0,0]

        next = RTS[0,1,0]
        reflections[0,1] = angles(-next, -self.mirror[0].Wedge[0], self.mirror[0].refractiveIndex, self.refractiveIndex, approx)[1]

        for i in range(1,m):
            for s in (0,1):
                next = RTS[i,s,0]

                if s:
                    next = angles(-next, -self.mirror[i].Wedge[0], self.mirror[i].refractiveIndex, self.refractiveIndex, approx)[1]

                for j in range(i-1,-1,-1):
                    next = angles( -next, -self.mirror[j].Wedge[1], self.refractiveIndex, self.mirror[j].refractiveIndex, approx)[1]
                    next = angles( -next, -self.mirror[j].Wedge[0], self.mirror[j].refractiveIndex, self.refractiveIndex, approx)[1]

                reflections[i,s] = next

        if m==1:
            return reflections[0]
        else:
            return reflections


    def transmission_angle(self, incident=0, approx=True):
        if approx: return self.transmission_angle_approx(incident)
        else: return self.transmission_angle_exact(incident)

    def transmission_angle_approx(self, incident):
        reducedIndex = self.getIndexVector() / self.refractiveIndex - 1
        wedgeVector = self.getWedgeVector()
        return np.dot( reducedIndex, wedgeVector() )

    def transmission_angle_exact(self, incident):
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


    def getIndexVector(self):
        return np.array([ mir.refractiveIndex for mir in self.mirror ])

    def getWedgeVector(self):
        m = len(self.mirror)
        wedgeVector = np.vstack(( self.mirror[0].Wedge[0] , self.mirror[0].Wedge[1] ))
        for i in range(1,m):
            wedgeVector = np.vstack(( wedgeVector, self.mirror[i].Wedge[0] ))
            wedgeVector = np.vstack(( wedgeVector, self.mirror[i].Wedge[1] ))
        return wedgeVector


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


##############################


def minimize_transmitted_angle(optics):

    m = len(optics.mirror)

    def clock_and_transmit(*rotation_angle):
        clocked = optics.clock(*rotation_angle, True)
        t = clocked.transmission_angle()
        return np.linalg.norm(t)

    bounds = optimize.LinearConstraint(np.identity(m),0,2*np.pi)
    result = optimize.minimize(clock_and_transmit, np.zeros(m), constraints=(bounds))

    return result


def wedges_from_reflections(true_reflections, indices, approx=True, max_angle=np.pi/2):

    m = len(indices)
    if isinstance(true_reflections, np.ndarray):
        pass
    else:
        true_reflections = np.array( true_reflections )

    s = true_reflections.size
    shape = self.__shape__()

    def reshape(nparr):
        A = nparr.reshape( (m,*shape) )
        if m == 1: A = A[0]
        return A

    true_reflections = reshape(true_reflections)

    bounds = optimize.LinearConstraint(np.identity(s), -max_angle, max_angle)

    testop = Optics()
    if d:
        for j in range(m): testop.add_mirror( (0,0) , (0,0) , indices[j] )
    else:
        for j in range(m): testop.add_mirror(0,0,indices[j])

    def SumSqDiff(test_wedges):
        test_wedges = reshape(test_wedges)

        for i in range(m): testop.mirror[i].Wedge = test_wedges[i]

        calculated_reflections = testop.reflection_angles(0, approx)
        diff = true_reflections - calculated_reflections
        return np.linalg.norm(diff)**2 

    result = optimize.minimize(SumSqDiff, np.zeros(s), constraints=(bounds))

    result.x = reshape(result.x)

    return result
