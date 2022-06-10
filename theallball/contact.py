from math import inf
from pygame.math import Vector2

'''
Energy is conserved
Newton's 3rd law (conservation of momentum)
Conservation of angular momentum
Direction of force is correct (Normal force vs friction force)

Steps for processing collisions:
    Detect collisions
        For all pairs of objects that might overlap, calculate the amount of overlap and if overlapping
        the normal of the overlap.
        Negative and positive overlap.
    Collision resolution: resolve_contact()
        1) Resolve overlap
            Translate the two objects apart until they are just touching.
            Keep the center of mass of both objects in the same place.
            We do this by making the displacement proportional to the inverse mass of each object.
            Reciprocal mass or 1/mass.
            overlap  = d  normal = n  (remember to normalize n once!)
            rA, rB = position
            d = (A.radius + B.radius) - abs(rA-rB)
            n = normalize(rA-rB)
                Total displacement = overlap.
                mA, mB = mass 
                delta(rA) = 1/mA ,  delta(rB) = 1/mB

                delta(rA) =  ((1/mA) / ((1/mA) + (1/mB))) * d * nhat

                delta(rB) =  ((1/mB) / ((1/mA) + (1/mB))) * d * -nhat


                Reduced mass = 1/ (1/mB) + (1/mA) = rmass

            Revised formulas = 
            delta(rA) = rmass/mA * d * nhat
            delta(rB) = rmass/mB * d * -nhat

            add a delta_pos() function to Particle class
            def delta_pos ( self,delta):
                self.pos += delta
        2) Resolve velocity
            Make them bounce or simply stop.
            Apply equal and opposite impulses to change the velocity.


            Impulse = force * time interval.   J = F * deltaT
            Impulse should be parallel to the normal because it comes from the normal force between
            the two objects.

            Need to calculate the right impulse for our collision
            respective to coefficient of restitution
            restitution = 0 perfectly inelastic (stop)
            restitution = 1 perfectly elastic (no energy loss)

            restitution = eR = - (final separating velocity / initial separating velocity)
             Note from me: project the velocities of A and B onto the normal vector.

             v = (vA - vB)
            Separating velocity = (vA - vB) * nhat
            Final separating velocity = -eR * (vA-vB) * nhat

            If we apply an impulse it changes the velocities
            delta(vA) =  J/mA   delta(vB) = -J/mB

            v(final)* nhat = -eR * v * nhat

            delta(v) = delta(vA) - delta(vB)  = J/mA + J/mB
            delta(v) = (1/mA + 1/mB) * J
            delta(v) * nhat = (1/mA + 1/mB) * J * nhat

            J = delta(v)  * nhat / (1/mA + 1/mB)   =  m * delta(v) * nhat
            J = -m * (l + eR) * v + nhat

            Create an impulse function in the Particle class.

            The only thing the impulse function does is change the velocity of the particle.
            delta(v) = J/mA
'''


# Returns a new contact object of the correct type
# This function has been done for you.
def generate_contact(a, b):
    # Check if a's type comes later than b's alphabetically.
    # We will label our collision types in alphabetical order, 
    # so the lower one needs to go first.
    if b.contact_type < a.contact_type:
        a, b = b, a
    # This calls the class of the appropriate name based on the two contact types.
    return globals()[f"Contact_{a.contact_type}_{b.contact_type}"](a, b)
    

'''
For each particle, find the velocity at the point of contact
vA(contact) = (translational velocity) + wA cross sA (or rotational velocity)
wA = a, avel


sA
rC = point of contact
sA = rC - rA(point of rotation of object)

Find vB(contact)
vB(contact) = vB + wA cross sB
sB = rC - rB

wA cross sA = wA * (sA rotated 90 degrees)
wA cross sA = wA* (-sA.x, sA.y)


Relative velocity = v = vA(contact) - vB(contact)
Proceed as normal with resolve_contact()

We need to add a function in contact class 


'''

'''
Jumping
He wants an additional normal velocity
vNF = -epsilon * vN

vNF = final normal velocity
vN = initial normal velocity
For jumping we need to add an additional term. Add a jump velocity

vNF = -epsilon*vN + vJ

(delta)vN = -(1+epsilon)*vN + vJ
Multiply both sides by m, reduced mass
m(delta)vN = -(1+epsilon)*m*vN + m*vJ
explanation of above line:
    m(delta)vN = jN
    -(1+epsilon)*m*vN = impulse to bounce
    m*vJ = additional normal impulse for jumping

Running jumps should make a difference
If the player is jumping, we want to reduce the sideways or tangential impulse by some factor.
Tangential impulse is jT
Factor should be between 0 and 1, like 0.5



'''





def impart_rotational(contact):
    a = contact.a
    b = contact.b
    sOfA = contact.point() - a.pos
    sOfB = contact.point() - b.pos
    contactRotationA = Vector2(-sOfA.y,sOfA.x)
    contactRotationB = Vector2(-sOfB.y,sOfB.x)
    velA = a.vel  + a.avel * contactRotationA
    velB = b.vel + b.avel * contactRotationB
    return velA - velB


# Resolves a contact (by the default method) and returns True if it needed to be resolved
def resolve_contact(contact, restitution=0,friction=0,jump=0):
    d = contact.overlap()
    n = contact.normal()
    a = contact.a
    b = contact.b
    u = friction
    if d > 0:
        #resolve overlap
        m = 1 / ((1/a.mass) + (1/b.mass))
        #translate a by m/mA d*nhat
        a.pos += (m/a.mass) * d * n
        #translate b by -m/mB * d*nhat
        b.pos += -(m/b.mass) * d * n
        #resolve velocity
        #relative velocity
        v = impart_rotational(contact)
        vdot = Vector2.dot(v,n)
        #t = (v-v.dot(n) * n).normalize()
        t = Vector2(-n[1],n[0])
        vt = Vector2(v).dot(t)
        if vt < 0:
                t *= -1
                vt *= -1

        
        if vdot < 0:
            jN = -(1+restitution) * m * vdot + (m*jump)
            jT = vt * m * -1
            if abs(jT) > (jN * u):
                jT = -1 * u * jN
            else:
                slide = abs(vt/vdot) * d
                a.pos += slide * (m/a.mass) * -t
                b.pos += slide * (m/b.mass) * t
            
            J = (jN * n) + (jT*t)
            a.impulse(J)
            b.impulse(-J) 

            return True
        
    return False



def resolve_contact_bumper(contact, bvel=800,bumper=None):
    d = contact.overlap()
    n = contact.normal()
    a = contact.a
    b = contact.b
    if d > 0:
        #resolve overlap
        m = 1 / ((1/a.mass) + (1/b.mass))
        #translate a by m/mA d*nhat
        if not bumper==a:
         a.pos += (m/a.mass) * d * n
        #translate b by -m/mB * d*nhat
        if not bumper==b:
         b.pos += -(m/b.mass) * d * n
        #resolve velocity
        #relative velocity
        v = a.vel - b.vel
        vdot = Vector2.dot(v,n)
        if vdot < 0:
            J = m*(-vdot + bvel)*n
            if not bumper==a:
                a.impulse(J)
            if not bumper==b:
             b.impulse(-J)
            return True
    return False


# Generic contact class, to be overridden by specific scenarios
class Contact():
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.renew()
        
    def renew(self):
        pass
 
    def overlap(self):  # virtual function
        return 0

    def normal(self):  # virtual function
        return Vector2(0, 0)
    
    def point(self):  #Point of contact
        return Vector2(0,0)


# Contact class for two circles
class Contact_Circle_Circle(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)


    def update(self):
        self.overlap = 0
        self.normal = Vector2(0,0)
    

    def overlap(self):
        return (self.a.radius+self.b.radius) - (self.a.pos-self.b.pos).magnitude()

    def normal(self):
        return (self.a.pos-self.b.pos).normalize()  # Fill in the appropriate expression
    
    def point(self):
        return (self.a.pos + self.b.pos) /2


'''
Overlap = radius - distance.
Distance = Vector2.dot(circle_pos - wall_pos,wall_normal)
'''
class Contact_Circle_Wall(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)
        self.circle = a
        self.wall = b


    def update(self):
        self.overlap = 0
        self.normal = Vector2(0,0)
    

    def overlap(self):
        return self.circle.radius - Vector2.dot(self.circle.pos - self.wall.pos,self.wall.normal)

    def normal(self):
        return self.wall.normal # Fill in the appropriate expression

    def point(self):
        return self.circle.pos + (self.circle.radius * -1 * self.wall.normal)



#Empty class for wall-wall collision
class Contact_Wall_Wall(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)


class Contact_Polygon_Polygon(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)


class Contact_Polygon_Wall(Contact):
    def __init__(self, a, b):
        super().__init__(a, b)      


'''
Check overlap with each side.
Check overlap with a vertex

Triangle Example
Check overlap with each side
    Treat each side like a wall
    Wall position = polygon point or points[i] and wall normal is polygon normal associated with that point or normals[i]
    Calculate overlap just like for a circle wall overlap
        If the overlap is negative for even just one side, then the circle is not overlapping the polygon..
            If a side has negative overlap, then you can stop calculating the rest of the sides.

Part 2
    If a circle is beyond one of the endpoints of the least overlapped side, then we are overlapping
    that vertex
    Project onto vector that represents the direction of a side

'''

class Contact_Circle_Polygon(Contact):
    def __init__(self,a,b):
        self.circle = a
        self.polygon = b
        self.vertexoverlap = False
        super().__init__(a,b)

    def fast_over(self,pos,norm):
        return self.circle.radius - Vector2.dot(self.circle.pos-pos,norm)

    
    def renew(self): 
        #check overlap with each side.
        min_overlap = inf
        self.vertexoverlap = False
        for index,wallnorm in enumerate(self.polygon.normals):
            wallpos = self.polygon.points[index]
            overlap = self.fast_over(wallpos,wallnorm)
            if overlap < min_overlap:
                min_overlap = overlap
                self.index = index

        #Check overlap with vertex
        p1 = self.polygon.points[self.index]
        p2 = self.polygon.points[self.index-1]
        sidevector = (p1-p2)
        projection = (self.circle.pos-p1).dot(sidevector)
        if (self.circle.pos - p1).dot(sidevector) > 0:
            #beyond point2
            self.vertexoverlap = True    
        elif (self.circle.pos-p2).dot(sidevector)  < 0: #Chose >0 based on previous instruction, may be false
            self.vertexoverlap = True
            self.index = self.index - 1

    def overlap(self):
        if not self.vertexoverlap:
            wall_pos = self.polygon.points[self.index]
            wall_norm = self.polygon.normals[self.index]
            return self.fast_over(wall_pos,wall_norm)
        else:
            #circle-circle collision but one circle is radius 0
            return self.circle.radius - (self.circle.pos-self.polygon.points[self.index]).magnitude()


    def normal(self):
        if not self.vertexoverlap:
            return self.polygon.normals[self.index]
        else:
            return (self.circle.pos - self.polygon.points[self.index]).normalize()
        return Vector2(0,0)

    def point(self):
        if self.vertexoverlap:
            return self.polygon.points[self.index]
        else:
            proj_point = self.polygon.normals[self.index] * -1 * self.circle.radius
            return self.circle.pos + proj_point


    

