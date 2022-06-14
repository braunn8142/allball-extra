import json
import os
import sys
import random 


from physics_objects import Polygon,Circle,UniformCircle,UniformPolygon,world_poly,world_rect,to_uniform,Elevator,Spinner
import pygame
import math

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
width, height = 1600, 700
window = pygame.display.set_mode([width, height])
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

bg_objects = []
bg_objects_anim = []
fg_objects = []

## Function definition
# Formerly placed after the level_info_list in main

def create_poly_sqr(pos, size, color, vel, avel):  
  return Polygon(pos=pos, offsets=[(-size, -size),(-1*size,size),(size,size),(size,-1*size)], color=color, vel=vel, avel=avel)

def create_non_com_sqr(pos, size, color, vel, avel):  
  return Polygon(pos=pos, offsets=[(0, 0),(0, -2 * size),(2*size,-2*size),(2*size,0)], color=color, vel=vel, avel=avel)

def create_poly_rect(pos, s_length, s_height, color, vel, avel):  
  return Polygon(pos=pos, offsets=[(-s_length, -s_height), (-s_length, s_height),(s_length, s_height), (s_length, -s_height)], color=color, vel=vel, avel=avel)

# Notes: Color1 is the outline color
def create_spiked_mine(pos, speed, avel, outer_rad, mid_size, inner_rad, color1, color2, color3):  
  bg_objects.append(Circle(pos=pos, vel=speed, radius=outer_rad, color=color1))
  bg_objects.append(Circle(pos=pos, vel=speed, radius=outer_rad-2, color=color2))              
  bg_objects.append(create_poly_sqr(pos, mid_size, color2, speed, avel=-avel))
  bg_objects.append(create_poly_sqr(pos, mid_size-(mid_size*.04), color3, speed, avel=avel))    
  bg_objects.append(Circle(pos=pos, vel=speed, radius=inner_rad, color=color1))
  bg_objects.append(Circle(pos=pos, vel=speed, radius=inner_rad-(inner_rad*.04), color=color2))

def create_box_circle(pos, speed, avel, box_size, circle_rad, color1, color2, color3):
  bg_objects.append(create_poly_sqr(pos, box_size, color1, speed, avel=avel))
  bg_objects.append(create_poly_sqr(pos, box_size-(box_size *.04), color3, speed, avel=avel))    
  bg_objects.append(Circle(pos=pos, vel=speed, radius=circle_rad, color=color1))
  bg_objects.append(Circle(pos=pos, vel=speed, radius=circle_rad-(circle_rad*.04), color=color2))

# Contains no animated objects, or objects that use functions to directly add them to the array
def create_template_background(speed, preset):  
  randomTemp = (random.randint(100, 700),random.randint(50,500))
  test_obj_arr = []
  if preset == 1:
    test_obj_arr = [
        (Circle(pos=(width/4,100), vel=(speed,0), radius=12, color=[0,0,0])),
        (Circle(pos=(width/4,100), vel=(speed,0), radius=10, color=[170,170,255])),
        (create_poly_sqr(randomTemp, 11, [0,0,0], (speed/3,0), avel=5)),
        (create_poly_sqr(randomTemp, 10, [255,165,0], (speed/3,0), avel=5)),  
        (Circle(pos=(width/6,height/1.5), vel=(speed/3,0), radius=22, color=[0,0,0])),
        (Circle(pos=(width/6,height/1.5), vel=(speed/3,0), radius=20, color=[200,100,200])),               
        (Circle(pos=(width/2,height/3), vel=(speed,speed/3), radius=22, color=[0,0,0])),
        (Circle(pos=(width/2,height/3), vel=(speed,speed/3), radius=20, color=[random.randint(100,255),100,200]))
        ]
  elif preset == 2:
    test_obj_arr = [
      (create_non_com_sqr((width/2,height/2-50), -250, [0, 55, 55], (0, 0), avel=.5)),            
      (Circle(pos=(width/2,height/2-50), vel=(0,0), radius=355, color=[0, 75, 75])),
      (create_poly_sqr((width/2,height/2-50), 250, [0, 55, 55], (0, 0), avel=.05)), 
      (create_poly_sqr((width/2,height/2-50), 200, [0, 75, 75], (0, 0), avel=.05)), 
      (create_poly_sqr((width/2,height/2-50), 150, [0, 95, 95], (0, 0), avel=.05)),
      (create_poly_sqr((width/2,height/2-50), 100, [0, 115, 115], (0, 0), avel=.05)),  
      (create_poly_sqr((width/2,height/2-50), 50, [0, 135, 135], (0, 0), avel=.05)),        
    ]
  elif preset == 3:
    test_obj_arr = [            
      (create_poly_sqr((width/2,height/2-50), 120, [0, 35, 35], (0, 0), avel=.1 )), 
      (create_poly_sqr((width/2,height/2-50), 100, [0, 55, 55], (0, 0), avel=.1)), 
      (create_poly_sqr((width/2,height/2-50), 80, [0, 75, 75], (0, 0), avel=.1)), 
      (create_poly_sqr((width/2,height/2-50), 60, [0, 95, 95], (0, 0), avel=.1)),
      (create_poly_sqr((width/2,height/2-50), 40, [0, 115, 115], (0, 0), avel=.1)),  
      (create_poly_sqr((width/2,height/2-50), 20, [0, 135, 135], (0, 0), avel=.1)),            
    ]

  elif preset == 4 or preset == 5:
    test_obj_arr = [
      (create_non_com_sqr((width/2,height/2-50), -250, [55, 0, 0], (0, 0), avel=1)),
      (create_non_com_sqr((width/2,height/2-50), 250, [55, 0, 0], (0, 0), avel=1)),            
      (Circle(pos=(width/2,height/2-50), vel=(0,0), radius=355, color=[75, 0, 0])),
      (create_poly_sqr((width/2,height/2-50), 250, [55, 0, 0], (0, 0), avel=.05)), 
      (create_poly_sqr((width/2,height/2-50), 200, [75, 0, 0], (0, 0), avel=.05)), 
      (create_poly_sqr((width/2,height/2-50), 150, [95, 0, 0], (0, 0), avel=.05)),
      (create_poly_sqr((width/2,height/2-50), 100, [115, 0, 0], (0, 0), avel=.05)),  
      (create_poly_sqr((width/2,height/2-50), 50, [135, 0, 0], (0, 0), avel=.05)),        
    ]
  return test_obj_arr

## Next two functions are exported
def bg_anim_setup(speed, preset):
  global bg_objects
  global bg_objects_anim
  # preset 1: Comets
  if preset == 1:  
    bg_objects.append(Circle(pos=(width/4,100), vel=(speed,0), radius=12, color=[0,0,0]))
    bg_objects.append(Circle(pos=(width/4,100), vel=(speed,0), radius=10, color=[170,170,255]))
    
    randomTemp = (random.randint(100, 700),random.randint(50,500))
    bg_objects.append(create_poly_sqr(randomTemp, 11, [0,0,0], (speed/3,0), avel=5))
    bg_objects.append(create_poly_sqr(randomTemp, 10, [255,165,0], (speed/3,0), avel=5))  
  
    bg_objects.append(Circle(pos=(width/6,height/1.5), vel=(speed/3,0), radius=22, color=[0,0,0]))
    bg_objects.append(Circle(pos=(width/6,height/1.5), vel=(speed/3,0), radius=20, color=[200,100,200]))            
              
    bg_objects.append(Circle(pos=(width/2,height/3), vel=(speed,speed/3), radius=22, color=[0,0,0]))
    bg_objects.append(Circle(pos=(width/2,height/3), vel=(speed,speed/3), radius=20, color=[random.randint(100,255),100,200]))

    create_spiked_mine((200,320), (speed, speed), 3, 25, 20, 20, [255,255,255], [0,0,0], [200,0,0])
    create_spiked_mine((300,220), (speed, speed), 3, 25, 20, 20, [255,255,255], [0,0,0], [200,0,0])
    create_spiked_mine((400,120), (speed, speed), 3, 25, 20, 20, [255,255,255], [0,0,0], [200,0,0])
    create_spiked_mine((600,20), (speed, speed), 3, 25, 20, 20, [255,255,255], [0,0,0], [200,0,0])
    
    # Append any animated background elements after static ones    
    bg_objects_anim.append(Circle(pos=(200,320), vel=(speed, speed), radius=14, color=[0,0,0]))       
    bg_objects_anim.append(Circle(pos=(300,220), vel=(speed,speed), radius=14, color=[0,0,0]))
    bg_objects_anim.append(Circle(pos=(400,120), vel=(speed, speed), radius=14, color=[0,0,0]))       
    bg_objects_anim.append(Circle(pos=(600,20), vel=(speed,speed), radius=14, color=[0,0,0]))           
  elif preset == 2:    
    bg_objects = create_template_background(speed, preset)    
    bg_objects_anim.append((create_poly_sqr((width/2,height/2-50), 25, [0, 0,0], (0, 0), avel=.05))) 
  elif preset == 3:
    bg_objects = create_template_background(speed, preset)   
  elif preset == 4:
    bg_objects = create_template_background(speed, preset)    
    bg_objects_anim.append((create_poly_sqr((width/2,height/2-50), 25, [0, 0,0], (0, 0), avel=.05)))
    bg_objects.append((create_non_com_sqr((0,height/2-50), 150, [255,255,220], (0, 0), avel=0)))
    bg_objects.append((create_non_com_sqr((0,height/2-50), 140, [255, 200, 200], (0, 0), avel=0)))
    bg_objects.append((create_non_com_sqr((0,height-100), 150, [255,255,220], (0, 0), avel=0)))
    bg_objects.append((create_non_com_sqr((0,height-100), 140, [255,200,200], (0, 0), avel=0)))

  elif preset == 5:
    bg_objects = create_template_background(speed, preset)

  return bg_objects

def fg_anim_setup(levelexitpos):
  fg_objects = []
  fg_objects.append((create_poly_sqr((levelexitpos), 23, [255,255,255], (0, 0), avel=0)))
  fg_objects.append((create_poly_sqr((levelexitpos), 15, [0,0,0], (0, 0), avel=2.5)))
  fg_objects.append((create_poly_sqr((levelexitpos), 15 * .9, [255,255,255], (0, 0), avel=2.5)))
  fg_objects.append((create_poly_sqr((levelexitpos), 7, [0,0,0], (0, 0), avel=-5)))
  fg_objects.append((create_poly_sqr((levelexitpos), 7 * .9, [255,255,255], (0, 0), avel=-5)))  
  
  return fg_objects