import numpy as np

class Mirror():

    def __init__(self, frontWedge, backWedge, refractiveIndex=1.5):
        self.frontWedge = np.array(frontWedge)
        self.backWedge = np.array(backWedge)
        self.refractiveIndex = refractiveIndex

    def clock(self, angle):
        R = np.array([ [np.cos(angle), -np.sin(angle)] , [np.sin(angle), np.cos(angle)] ])
        uFront = np.array([ self.frontWedge[1], -self.frontWedge[0] ]).reshape((2,1))
        uBack = np.array([ self.backWedge[1], -self.backWedge[0] ]).reshape((2,1))
        Ru_front = R @ uFront
        Ru_back = R @ uBack
        self.frontWedge[1] = Ru_front[0]
        self.frontWedge[0] = -Ru_front[1]
        self.backWedge[1] = Ru_back[0]
        self.backWedge[0] = -Ru_back[1]

def angles(incident=0, wedge=0, n1=1, n2=1):

    ## __ represents an angle with respect to the axis normal to the mirror (rather than the optical axis)

    __incident__ = incident - wedge
    __reflect__ = - __incident__
    reflect = incident + 2 * __reflect__

    __trans__ = - (n1/n2) * __incident__
    trans = __trans__ - wedge

    return np.array([reflect, trans])

class Optics():
    def __init__(self, n=1):
        self.refractiveIndex = n
        self.mirror = list()

    def add_mirror(self, *args):
        if isinstance(args[0], Mirror): self.mirror.append(x)
        else: self.mirror.append( Mirror(*args) )

    def reflection_angles(self, incident=0):
        m = len(self.mirror)
        RTS = list()                     ## Reflection and Transmission angles per Surface per mirror

        for i in range(m):
            if i == 0:
                first = angles(incident, self.mirror[i].frontWedge, self.refractiveIndex, self.mirror[i].refractiveIndex)
            else:
                first = angles(-RTS[i-1][1][1], self.mirror[i].frontWedge, self.refractiveIndex, self.mirror[i].refractiveIndex)

            second = angles(-first[1], self.mirror[i].backWedge, self.mirror[i].refractiveIndex, self.refractiveIndex)

            RTS.append( (first,second) )

        ### RTS [mirror #][surface #][R or T][X or Y]
        RTS = np.array( RTS )

        R = RTS[0,0,0]
        next = RTS[0,1,0]
        dim = R.ndim
        if dim:
            R = np.vstack((R, angles( -next, -self.mirror[0].frontWedge, self.mirror[0].refractiveIndex, self.refractiveIndex)[1] ))
        else:
            R = np.hstack((R, angles( -next, -self.mirror[0].frontWedge, self.mirror[0].refractiveIndex, self.refractiveIndex)[1] ))

        for i in range(1,m):                 ## for each mirror
            for s in (0,1):             ## for each surface, front and back
                next = RTS[i,s,0]
                ## sets incoming angle to be either the reflected angle of the back or front surface of the current mirror

                ## if back surface, propagate to front surface
                if s:
                    next = angles( -next, -self.mirror[i].frontWedge, self.mirror[i].refractiveIndex, self.refractiveIndex)[1]

                ## propagate through all previous mirrors
                for j in range(i-1,-1,-1):
                    next = angles( -next, -self.mirror[j].backWedge, self.refractiveIndex, self.mirror[j].refractiveIndex)[1]
                    next = angles( -next, -self.mirror[j].frontWedge, self.mirror[j].refractiveIndex, self.refractiveIndex)[1]

                if dim: R = np.vstack( (R, next) )
                else: R = np.hstack( (R, next) )
        return R

    def transmission_angle(self, incident=0):
        m = len(self.mirror)
        T = list()             ## Transmitted angle per surface per mirror

        for i in range(m):
            if i == 0:
                first = angles(incident, self.mirror[i].frontWedge, self.refractiveIndex, self.mirror[i].refractiveIndex)[1]
            else:
                first = angles(-T[i-1,1], self.mirror[i].frontWedge, self.refractiveIndex, self.mirror[i].refractiveIndex)[1]

            second = angles(-first, self.mirror[i].backWedge, self.mirror[i].refractiveIndex, self.refractiveIndex)[1]

            T.append( (first,second) )

        return T[-1][1]

    def count_mirrors(self):
        return len(self.mirror)

    def remove_mirror(self, index):
        self.mirror.pop(index)
