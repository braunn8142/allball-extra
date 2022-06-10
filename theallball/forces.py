import pygame
from pygame.math import Vector2
from itertools import combinations
import math

class SingleForce:
    def __init__(self, objects_list=[]):
        self.objects_list = objects_list

    def apply(self):
        for obj in self.objects_list:
            force = self.force(obj)
            obj.add_force(force)

    def force(self, obj): # virtual function
        return Vector2(0, 0)


class PairForce:
    def __init__(self, objects_list=[]):
        self.objects_list = objects_list

    def apply(self):
        # Loop over all pairs of objects and apply the calculated force
        # to each object, respecting Newton's 3rd Law.  
        # Use either two nested for loops (taking care to do each pair once)
        # or use the itertools library (specifically, the function combinations).

        for a,b in combinations(self.objects_list,2):
            force = self.force(a,b)
            a.add_force(force)
            b.add_force(force * -1)

    def force(self, a, b): # virtual function
        return Vector2(0, 0) #Returns the force on a due to b, and the force on b due to a.


class BondForce:
    def __init__(self, pairs_list=[]):
        # pairs_list has the format [[obj1, obj2], [obj3, obj4], ... ]
        self.pairs_list = pairs_list

    def apply(self):
        # Loop over all pairs from the pairs list.  
        # Apply the force to each member of the pair respecting Newton's 3rd Law.
        for a,b in self.pairs_list:
            force1 = self.force(a,b)
            a.add_force(force1)
            b.add_force(force1 * -1)

        
    def force(self, a, b): # virtual function
        return Vector2(0, 0)

# Add Gravity, SpringForce, SpringRepulsion, AirDrag
class Gravity(SingleForce):
    def __init__(self, acc=(0,0), **kwargs):
        self.acc = Vector2(acc)
        super().__init__(**kwargs)

    def force(self, obj):  #overriding the super class
        return obj.mass*self.acc
        # Note: this will throw an error if the object has infinite mass.
        # Think about how to handle those.
    

class SpringForce(BondForce):
    def __init__(self, k,l,b, **kwargs):
        self.k = k
        self.l =l 
        self.b = b
        super().__init__(**kwargs)

    def force(self,obj1,obj2):
        r = Vector2(obj1.pos-obj2.pos)
        r = r if r.magnitude() != 0 else obj1.force.normalize()
        rhat = r.normalize()
        rabs = r.magnitude()
        v = Vector2(obj1.vel-obj2.vel)


        p2 = (-self.b*v*rhat)
        p1 = (-self.k * (r.magnitude() - self.l))
    
        #f_spring = (-self.k * (r.magnitude()-self.l)) - (self.b*v*r.normalize()) * r.normalize()
        f_spring = (p1 + p2) * r.normalize()
        return f_spring

    def draw(self,surface):
        for a,b in self.pairs_list:
            dist = Vector2(a.pos-b.pos)
            diff = self.l/max(1,dist.magnitude())
            pygame.draw.line(surface,[255,0,0],a.pos,b.pos,max(1,min(a.radius,math.floor(diff * 8))))


class AirDrag(SingleForce):
    def __init__(self,p,cd,wind=(0,0), **kwargs):
        self.p = p
        self.cd = cd
        self.wind = wind
        super().__init__(**kwargs)

    
    def force(self,obj):
        A = (math.pi * (obj.radius*obj.radius))
        V = obj.vel - self.wind
        vabs = Vector2(obj.vel).magnitude()
        F = (-0.5) * self.cd * self.p * A * vabs * V
        return F

class Friction(SingleForce):
    def __init__(self,u,g, **kwargs):
        self.u = u
        self.g = g
        super().__init__(**kwargs)

    
    def force(self,obj):
        F = -self.u * obj.mass * self.g * obj.vel
        return F


class SpringRepulsion(PairForce):
    def __init__(self,k=0, **kwargs):
        self.k = k
        super().__init__(**kwargs)
    def force(self,a,b):
        r = a.pos - b.pos
        q = (a.radius + b.radius) - r.magnitude()
        f_rep = Vector2(0,0)
        if q > 0 and r.magnitude() != 0:
            f_rep  = Vector2(self.k * q * r.normalize())

        
        return f_rep


