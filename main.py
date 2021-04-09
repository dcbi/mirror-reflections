class Mirror():

	def __init__(self, front_wedge=0, back_wedge=0, refractive_index=1.5):
		self.wf = front_wedge
		self.wb = back_wedge
		self.n = refractive_index

	@staticmethod
	def angles(incident=0, wedge=0, n1=1, n2=1):

		## __ represents an angle with respect to the axis normal to the mirror (rather than the optical axis)

		__incident__ = incident - wedge
		__reflect__ = - __incident__
		reflect = incident + 2 * __reflect__

		__trans__ = - (n1 / n2) * __incident__
		trans = __trans__ - wedge

		return reflect, trans

class Optics():
	def __init__(self, n=1):
		self.n = n
		self.mirror = list()
		self.space = list()

	def add_mirror(self, wf=0, wb=0, n=1.5):
		self.mirror.append( Mirror(wf, wb, n) )

	def add_space(self, d=10):
		if isinstance(d, list) or isinstance(d, tuple):
			self.space = self.space + d
		else:
			self.space.append(d)

	def calculate_reflections(self, incident=0):
		m = len(self.mirror)
		RTS = list()                                 ### list of Reflection and Transmission angles for each Surface (front/back)

		first = Mirror.angles(incident, self.mirror[0].wf, self.n, self.mirror[0].n)
		RTS.append( ( first, 
                              Mirror.angles(-first[1], self.mirror[0].wb, self.mirror[0].n, self.n) 
                             )
                           )

		### RTS [mirror #][surface #][R or T]

		for i in range(1,m):
			RTS.append( ( Mirror.angles(0, self.mirror[i].wf, self.n, self.mirror[i].n) ,
                                      Mirror.angles(-RTS[i-1][1][1], self.mirror[i].wb, self.mirror[i].n, self.n) 
                                     ) 
                                   )

		R = [ RTS[0][0][0] ]
		next = RTS[0][1][0]
		R.append( Mirror.angles( -next, -self.mirror[0].wf, self.mirror[0].n, self.n )[1] )

		for i in range(1,m): 				## for each mirror
			for x in (0,1): 			## for each surface, front and back
				next = RTS[i][x][0]
				## sets incoming angle to be either the reflected angle of the back or front surface of the current mirror

				## if back surface, propagate to front surface
				if x:
					next = Mirror.angles( -next, -self.mirror[i].wf, self.mirror[i].n, self.n )[1]

				## propagate through all previous mirrors
				for j in range(i-1,-1,-1):
					next = Mirror.angles( -next, -self.mirror[j].wb, self.n, self.mirror[j].n )[1]
					next = Mirror.angles( -next, -self.mirror[j].wf, self.mirror[j].n, self.n )[1]

				R.append( next )
		return R
