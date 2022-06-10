
import math
from pygame.math import Vector2
from pygame.draw import circle
from pygame.draw import line
from pygame.draw import polygon

'''
mass -> moment of inertia -> mom
pos -> angle
vel -> avel
force -> torque

When we update linear motion,    vnew = nvold + (F/mass) * dt
dvel = force/mass * dt
dpos = vel * dt

deltaW = torque/momi * dt
deltaAngle = w * dt


'''
class Particle:
    def __init__(self, mass = math.inf, pos = (0,0), vel = (0,0),
    momi = math.inf, angle=0, avel=0):
        self.mass = mass
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.angle = angle
        self.avel = avel
        self.momi = momi
        self.clear_force()
    

    def clear_force(self):
        self.force = Vector2(0,0)
        self.torque = 0
        

    def add_force(self, force):
        self.force += force

    def impulse(self,j,point=None):
        if self.mass == math.inf:
            pass
        deltaV = j/self.mass
        if point is not None:
            s = point - self.pos
            self.avel += s.cross(j)/self.momi
        self.vel += Vector2(deltaV)
        

    def update(self, dt):
        # update velocity using the current force
        self.vel += (self.force/self.mass) * dt
        # update position using the newly updated velocity
        self.pos += (self.vel * dt)

        #rotation
        self.avel += (self.torque/self.momi) * dt
        self.angle += self.avel * dt
        


class Circle(Particle):
    def __init__(self,radius = 10, color = [255,255,255], width = 0, **kwargs):
        # **kwargs is a dictionary to catch all other keyword arguments
        super().__init__(**kwargs)
        #**kwargs unpacking the dictionary into key=value, key=value, etc.
        self.radius = radius
        self.color = color
        self.width = width
        self.contact_type = "Circle"
    def draw(self, window):
        circle(window,self.color,self.pos,self.radius,self.width)


'''
Wall will have a point1 and point2, acting as an infinite length wall.
position = midpoint
normal = 90 degrees from wall orientation, rotated clockwise.
Normal points to free space, where the objects should be.
Default mass should be infinite.


'''



class Wall(Particle):
    def __init__(self, point1, point2, reverse=False, color=[0,0,0], width=1):
        self.point1 = Vector2(point1)
        self.point2 = Vector2(point2)
        self.contact_type = "Wall"
        super().__init__(pos=(self.point1 + self.point2)/2)
        self.width = width
        self.color = color
        self.normal = (self.point2 - self.point1).normalize().rotate(90)
        if reverse:
            self.normal *= -1

    def draw(self, screen):
        line(screen, self.color, self.point1, self.point2, self.width)
        

'''
Polygon, vertices defined in order relative to a given position
'''
class Polygon(Particle): #convex polygon
    def __init__(self,offsets=((-1,-1),(-1,1),(1,1),(1,-1)),color=[255,255,255],normals_length=0,reverse = False,width=0,**kwargs):
        self.color = color
        self.angle = 0
        self.normals_length = normals_length
        self.reverse = reverse
        self.width = width
        super().__init__(**kwargs)
        #Convert all offsets to vector2
        self.offsets = [Vector2(x) for x in offsets]
        rotway = -90 if reverse else 90
        self.local_normals = [(x-self.offsets[y-1]).normalize().rotate(rotway) for y,x in enumerate(self.offsets)]
        
        self.normals = self.local_normals.copy()
        self.points = self.offsets.copy()
        self.contact_type = "Polygon"
        self.update_points()


        pass

    def update_points(self):      
       self.points = [x.rotate_rad(self.angle) + self.pos for x in self.offsets]
       self.normals = [x.rotate_rad(self.angle) for x in self.local_normals]



    def draw(self,surf):
        polygon(surf,self.color,self.points,self.width)
        if self.normals_length > 0:
            for index, normal in enumerate(self.normals):
                if not self.reverse: normal *= -1
                line(surf,[0,0,0],self.points[index],self.points[index] + (self.normals_length * normal),6)


    
    def update(self,dt):
        super().update(dt)
        self.update_points()



'''
Look up formula for moment of inertia of a disk

'''


class UniformCircle(Circle):
    def __init__(self, radius = 0, density = 0, **kwargs):
        # calculate mass and moment of inertia
        mass = math.pi * (radius * radius) * density
        momi = mass * 0.5 * (radius * radius)
        super().__init__(radius = radius,mass=mass, momi=momi, **kwargs)




'''
Really important that the moment of inertia is calculated correctly with the mass,
or the physics will look off
The easiest way is to have a wrapper for Polygon that computes the mass and moment of inertia assuming a constant density

We also need to find the center of mass, since freely rotating shapes  will rotate around their center of mass.
Then we will adjust the offsets so that the origin of the offsets is the center of mass.

To calculate the area of a polygon, break it into triangles, find the area of each triangle, and then add them up.

s1 = offsets[i]
s0 = offsets[i-1]

Area of one triangle, defined by sides s0 and s1 = 0.5 * s0.cross(s1)


Mass = density * area

Moment of inertia of a triangle about one of its corners =
M/6 *  ( magnitude(s0)^2 + magnitude(s1)^2 + s0.dot(s1))

OR
M/6 *  (s0.dot(s0) + s1.dot(s1) + s0.dot(s1))

Total mass = sum of the mass of each triangle
Total momi = sum of all moments of inertia.

Center of mass:
R = (sum of mI * rI) / mI  

Center of mass of a triangle:
rI  = 1/3 * s0 + s1

Keep a running total of m(triangle) and r(triangle)
Outside of the loop, divide by the total mass

R = sum(m(triangle) * r(triangle)) / total mass


Now that we know where the center of mass is, we need to shift the offsets so it spins around the center of mass
Subtract all the offsets by the difference between offsets[0] and calculated center of mass (R)
Then add R to the position of the polygon.

To handle rotation:
Add R rotated by the angle


We need to correct the moment of inertia to reflect the rotation about the new point
Parallel axis theorem
I(offcenter) = I(center of mass) + (total mass) * (displacement)^2   where displacement = our R.

I(center of mass) = I(offcenter)  - (total mass) * (displacement)^2 where I(off-center) is the moment of inertia we found initially




'''

class UniformPolygon(Polygon):



    def __init__(self, density=1, offsets=[], pos=[0,0], angle=0, shift=True, **kwargs):
        total_momi = 0
        total_mass = 0
        total_r = Vector2(0,0)
        offsets = [Vector2(x) for x in offsets]
        # Calculate mass, moment of inertia, and center of mass
        # by looping over all "triangles" of the polygon
        for i in range(len(offsets)):
            s0 = offsets[i]
            s1 = offsets[i-1]
            # triangle mass
            m = self.triangle_mass(density,s0,s1)
            # triangle moment of inertia
            momi = self.triangle_momi(m,s0,s1)
            # triangle center of mass
            com = self.triangle_com(s0,s1)

            # add to total mass
            total_mass += m
            # add to total moment of inertia
            total_momi += momi
            # add to center of mass numerator
            total_r += m * com
            
        
        # calculate total center of mass by dividing numerator by denominator (total mass)
        total_com = total_r/total_mass
        self.tcom = total_com

        if shift:
            # Shift offsets by com
            #Using list comprehension to override offsets
            offsets = [x - total_com for x in offsets]
            # shift pos
            pos -= total_com.rotate(angle)
            #print(str(b-pos))
            # Use parallel axis theorem to correct the moment of inertia
            I_com = total_momi - total_mass * total_com.dot(total_com)
            total_momi = I_com
            pass
        
       

        # Then call super().__init__() with those correct values
        super().__init__(mass=total_mass, momi=total_momi, offsets=offsets, pos=pos, angle=angle, **kwargs) 
    
    def triangle_mass(self,density,s0,s1):
        return density * 0.5 * s0.cross(s1)

    def triangle_com(self,s0,s1):
        return 1/3 * (s0 + s1)
    
    def triangle_momi(self,mass,s0,s1):
        return mass/6 * (s0.dot(s0) + s1.dot(s1) + s0.dot(s1))



def world_rect(P1,P2,color=[0,0,0]):
  flip = P2[1] < P1[1]
  new_off = (
    P1,
    (P1[0],P2[1]),
    P2,
    (P2[0],P1[1])
  )

  d = Polygon(reverse=flip,color=color,offsets=new_off)
  d.wasrect = True
  return d


def world_poly(color,pos,off,rev=True):
  u = Polygon(offsets=off,color=color,pos=pos,reverse=True)
  d= UniformPolygon(offsets=off,color=color,pos=pos,reverse=rev)
  diff = u.points[0] - d.points[0]
  d.pos += diff
  d.update_points()
  return d

def to_uniform(u):
  omass = u.mass
  d= UniformPolygon(offsets=u.offsets,color=u.color,pos=u.pos,reverse=u.reverse)
  diff = u.points[0] - d.points[0]
  d.pos += diff
  d.update_points()
  d.mass = omass
  return d


class Elevator():

    def __init__(self,polygon,location_p1,location_p2,trip_time,cycletype=1):
        self.poly = polygon
        self.tripTime = trip_time
        self.elapsed = 0
        self.L1 = Vector2(location_p1)
        self.L2 = Vector2(location_p2)
        self.ctype = cycletype



    def update(self,dt):
        self.elapsed += dt
        trip = self.elapsed % self.tripTime
        if self.ctype==0:
            lerp_pos = trip/self.tripTime
            self.poly.pos = Vector2.lerp(self.L1,self.L2,lerp_pos)
        elif self.ctype==1:
            half = 0.5 * self.tripTime
            halftrip = trip%half
            lerp_pos = halftrip/half
            if trip > half:
                lerp_pos = 1 - lerp_pos
            self.poly.pos = Vector2.lerp(self.L1,self.L2,lerp_pos)
        self.poly.update(dt)

class Spinner():
    def __init__(self,polygon,angletimestring):
        self.poly = polygon
        d = angletimestring.split(",")
        self.ro_times = [(float(d[i]),float(d[i+1])) for i in range(0,len(d)-1,2)]
        self.oangle = math.degrees(polygon.angle)
        self.elapsed = 0
        self.roindex = 0
        print(self.ro_times)

    def update(self,dt):
        self.elapsed += dt
        time = self.ro_times[self.roindex][1]
        nangle = self.ro_times[self.roindex][0]
        #print(nangle)
        if self.elapsed < time:
            percent = (self.elapsed%time)/time
            newest = (1-percent) * self.oangle  + (percent*nangle)
            self.poly.angle = math.radians(newest)
        else:
            self.elapsed = 0
            if self.roindex + 1 >= len(self.ro_times):
                self.roindex = 0
            else:
                self.roindex += 1
            self.oangle = nangle
        self.poly.update(dt)


        
        

