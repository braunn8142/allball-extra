import pygame
from pygame.math import Vector2, Vector3
from physics_objects import Circle, Elevator, Polygon,Spinner
from contact import generate_contact, resolve_contact, resolve_contact_bumper
from forces import Gravity
import math
import random
from tipy import file_to_level


# initialize pygame and open window
pygame.init()
width, height = 800, 700
window = pygame.display.set_mode([width, height])
center = Vector2(width/2, height/2)
diagonal = math.sqrt(width**2 + height**2)
BU = width/30

# set timing stuff
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.SysFont('monaco-ms', 24, True, False)
font_large = pygame.font.SysFont('monaco-ms', 48, True, False)

font2 = pygame.font.SysFont("comicsans-ms", 25, True, False)
def draw_text_located(t,black_back=True,ldiv=2,tdiv=2):
    t1 = font2.render(t,True,[255,255,255])
    xloc = window.get_width()/ldiv  - t1.get_width()/2
    yloc = window.get_height()/tdiv - t1.get_height()/2
    t_loc = (xloc,yloc)
    if black_back:
     r = pygame.Rect(t_loc[0], t_loc[1], t1.get_width(), t1.get_height())
     pygame.draw.rect(window, [0, 0, 0], r)
    window.blit(t1,t_loc)

# set objects
objects = [] 

circle = Circle(pos=(width/4,height-2*BU), vel=(0,0), radius=0.6*BU, mass=1, color=[0,0,255], width=0)

coeff_of_friction = 0.9
objects.append(circle)
gravity_objects = objects.copy()
# Background visuals 
background_anim_timer = 0
bg_anim_timer_length = 240 # time in ms
bg_object_ofscreen_offset = 100
bg_objects = []
bg_objects_anim = []
fg_objects = []

game_time = 0
test_last_check = 0
test_count = 0
bg_og_colors = [(0,35,35),(0,55,55),(0,75,75),(0,95,95),(0,115,115),(0,135,135)]
curr_bg_color = [0,0,0]

# Jumping variables
jumpsquat_timer = 0
jumpsquat_length = 8
max_jump_height = 400

# Level name and number variables
lv_name = "TestName"
lv_number = 2
levels = [
  "platformer_level2.json",
  "platformer_level6.json",
  "platformer_level7.json", 
  "platformer_level5.json", 
  "platformer_level_test2.json",
  "platformer_level4.json",
  "platformer_level3.json",
  "dead_level.json"]

level_info_list = [
    ("Onward", 100, 0, "Purple"),
    ("Wall Kicks Will Work", 50, 1, "Red"),
    ("Pinball", 130, 0, "Yellow"),
    ("Primate Platforms", 35, 2, "Black"),
    ("Water Plant", 100, 3, "Dark Blue"),
    ("Goodnight", 100, 4, "Red"),
    ("And Big Balls", 100, 5, "Black"),
    ("Death", 100, 3, "Purple")        
   ]

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

# region
def bg_anim_setup(speed, preset):
  global bg_objects
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

def fg_anim_setup(levelexitpos):
  fg_objects.append((create_poly_sqr((levelexitpos), 23, [255,255,255], (0, 0), avel=0)))

  fg_objects.append((create_poly_sqr((levelexitpos), 15, [0,0,0], (0, 0), avel=2.5)))
  fg_objects.append((create_poly_sqr((levelexitpos), 15 * .9, [255,255,255], (0, 0), avel=2.5)))

  fg_objects.append((create_poly_sqr((levelexitpos), 7, [0,0,0], (0, 0), avel=-5)))
  fg_objects.append((create_poly_sqr((levelexitpos), 7 * .9, [255,255,255], (0, 0), avel=-5)))

def setup_level_info(lv_info_index, levelexitpos):
  global bg_objects, bg_objects_anim, lv_name, lv_number, bg_color, fg_objects
  bg_objects = []
  bg_objects_anim = []
  fg_objects = []
  lv_number = lv_info_index + 1
  lv_name = level_info_list[lv_info_index][0]
  bg_anim_setup(level_info_list[lv_info_index][1], level_info_list[lv_info_index][2])
  fg_anim_setup(levelexitpos)
  bg_color = level_info_list[lv_info_index][3]  


#Main level object. Translates the dict from file_to_level into usable arrays for the main game loop.
def lv(index): 
  t = file_to_level(levels[index])
  lv.current_level = index
  lv.mobile = t['mobile']   
  lv.objects = t[''] + [circle] + t['gravitationals'] 
  lv.spikes = t['spikes']
  lv.bumpers = t['bumpers']
  lv.special = t['special']  
  lv.checkpoints = t['checkpoints']
  lv.adders = t['lifeadders']
  lv.gravitationals = t['gravitationals']
  lv.nextlvl = t['nextlvl'] or Circle()
  lv.last_check = lv.checkpoints[0]
  lv.elevators = t['elevators']
  lv.spinners = t['spinners']
  lv.all = lv.checkpoints + lv.adders + lv.objects + lv.spikes  + lv.mobile + lv.bumpers + lv.special + lv.gravitationals
  circle.pos = lv.last_check.pos.copy()
  # Level number (index), level exit position (middle of offset 0 and 3)
  setup_level_info(index, (lv.nextlvl.offsets[0] + lv.nextlvl.offsets[2])/2)
# endregion

lv(0)

gravity = Gravity([0,980], objects_list=gravity_objects)

# game loop
running = True
jumpter = 100
jump_held = False
hold_time = 0
hit_floor = False  
lives = 30

def overfloor(c): 
  truths = (False,False)
  if c.a == circle or c.b == circle:
    truths = (True,False)
    if c.overlap() > 0:
      truths = (True,True)
  return truths

def checkpoint_return():
  circle.pos = lv.last_check.pos.copy()
  circle.vel  = Vector2(0,0)
  gravity.acc = Vector2(0,980)


def rotate_check():
   g = lv.checkpoints.index(lv.last_check)
   lv.last_check = lv.checkpoints[(g+1)%len(lv.checkpoints)]
 



def win_screen():
   while True:
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_SPACE:
            lv(-1)
            lives = 30
            return
      window.fill([0,100,0]) 
      draw_text_located(" Hey, I think you won. Press SPACE to play again. ",2,2)
      pygame.display.update()
      clock.tick(fps)



def advance_lvl(c,r):
  if r:
    truth = (c.a == lv.nextlvl and c.b == circle) or (c.b == lv.nextlvl and c.a == circle)
    if truth:
      if lv.current_level == len(levels)-2:
        win_screen()
      lv(lv.current_level + 1)
      checkpoint_return()

gravity_objects.extend(lv.mobile)

def short_hop_timer_reset():
    # Setup shorthop checks
    # The ball will have 6 frames of "jumpsquat". Game runs in 60fps, so roughly a 10th of a second.
    # The ball will jump after 6 frames, regardless if the button is still held down.  
    # Spacebar pressed down, reset the jumpsquat timer.
    global jumpsquat_timer
    jumpsquat_timer = 0

def short_hop_check():
    # Checks jumpsquat timer. If the timer is 
    global jumpter
    if jumpsquat_timer <= jumpsquat_length:
        jump_height = 2 * (max_jump_height/3)
        jumpter = jump_height
    else:
        jumpter = max_jump_height

def jump_control_setup():
    # If the player is holding jump for longer than the jumpsquat time, then force the ball to jump
    keys = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pos()    
    if keys[pygame.K_SPACE] and jumpsquat_timer > jumpsquat_length: 
        short_hop_check()
        short_hop_timer_reset()
    elif keys[pygame.K_f]:
      circle.pos = mouse
      circle.vel = Vector2(0,0)
      #print(f"Mouse POS: {mouse}")
        
bg_circle = Circle(pos=(width/4,height/2), vel=(0,0), radius=20, color=[100,100,255])
bg_circle2 = Circle(pos=(width/4,height/2), vel=(0,0), radius=22, color=[0,0,0])

def draw_update_obj(obj):
    obj.update(dt)
    obj.draw(window)
    if obj.pos.x > width + bg_object_ofscreen_offset:
      obj.pos.x = 0 - bg_object_ofscreen_offset
    if obj.pos.y > height + bg_object_ofscreen_offset:
      obj.pos.y = 0 - bg_object_ofscreen_offset

def bg_anim_loop():           
  # Now set all of the moving objects
  for obj in bg_objects:
    draw_update_obj(obj)
    
  # Change color of the animating objects
  for obj in bg_objects_anim:              
    time2 = abs(background_anim_timer - (bg_anim_timer_length/2))  
    obj.color = (255, 120-(time2), 120-(time2))    
    draw_update_obj(obj)

def fg_anim_loop():
  # Update and draw of the foreground objects
  for obj in fg_objects:
    draw_update_obj(obj)
  # Do other stuff (WIP)

def bg_timer_test():
  global test_last_check, test_count
  test_check_diff = game_time - test_last_check
  if test_check_diff > 1:    
    test_count+=1
    if test_count > 5:
      test_count = 0      
    test_last_check = game_time    

def bg_obj_change_test():
  global bg_objects
  for i in range(len(bg_objects)):    
    bg_objects[i].color = curr_bg_color
    if i >= test_count:
      bg_objects[i].color = bg_og_colors[i]

  
def bg_color_check(time, str_toggle):
  if(str_toggle):
    if bg_color == "Purple":      
      return [255, 135+(time), 255]
    elif bg_color == "Yellow":
      return [255, 255, 135+(time)]
    elif bg_color == "Red":
      return [255, 135+(time), 135+(time)]
    elif bg_color == "Black":
      return [time,time,time]
    elif bg_color == "Dark Blue":
      return [135+(time), 135+(time), 255]

  if bg_color == "Purple":
    return [255, 195+(time/2), 255]
  elif bg_color == "Yellow":
    return [255, 255, 195+(time/2)]
  elif bg_color == "Red":
    return [255, 195+(time/2), 195+(time/2)]
  elif bg_color == "Black":
    return [time/2, time/2, time/2]
  elif bg_color == "Dark Blue":
    return [195+(time/2), 195+(time/2), 255]

while running:
    # EVENT loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                circle.avel = 30
            if event.key == pygame.K_LEFT:
                circle.avel = -30
            if event.key == pygame.K_DOWN:
              rotate_check()
              checkpoint_return()
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT,pygame.K_RIGHT):
              circle.avel = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
          short_hop_timer_reset()
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
          short_hop_check()

    # Control setup            
    jump_control_setup()
  
    # Timer increment
    game_time += dt

    for o in lv.objects:
        o.clear_force()

    gravity.apply()



   #New code for handling elevators. Makes use of gravity list but that may change
    for e in lv.elevators:
      e.update(dt)
  
    for s in lv.spinners:
      s.update(dt)


        
    # update objects
    for o in lv.objects:
      o.update(dt)
      if o == circle:
        continue
      c = generate_contact(o,circle)
      if c.overlap() > 0:
         r = resolve_contact(c, restitution=0.2, friction=coeff_of_friction,jump=jumpter)
         if o in lv.gravitationals:
           truth = -1 if o.contact_type == "Polygon" else 1
           way = -1 if o.flipped else 1
           gravity.acc = gravity.acc.length() * truth * c.normal() * way
         if jumpter > 0:
            jumpter = 0
         advance_lvl(c,r)

    for spec in lv.special:
      for o in gravity.objects_list:
        c=generate_contact(spec,o)
        r=resolve_contact(c, restitution=spec.res, friction=spec.fric,jump=jumpter if o==circle else 0)
        if c.overlap() > 0:
          if jumpter > 0:
            jumpter = 0
          
    for spike in lv.spikes:
        c = generate_contact(spike,circle)
        if c.overlap() > 0:
          checkpoint_return()
          if lives > 0:
             lives -= 1
          if lives == 0:
            lv(len(levels)-1)
            lv.current_level = -1
            lives = 30
            

    for bumper in lv.bumpers:
        c = generate_contact(bumper,circle)
        r = resolve_contact_bumper(c,bumper=bumper)      

    for check in lv.checkpoints:
      c = generate_contact(check,circle)
      if c.overlap() > 0 and lv.last_check != check:
        lv.last_check = check

    for bonus in lv.adders:
       c = generate_contact(bonus,circle)
       if c.overlap() > 0:
          lv.adders.remove(bonus)
          lv.all.remove(bonus)
          lives += 20

    # Increase the timer used for checking the jump
    jumpsquat_timer += (dt * 60)    
    # Force jumpter to 0 when not holding space
    if not jump_held:
        jumpter = 0

    # DRAW section ------------------------
    # clear the screen
    window.fill([255,255,255])
        
    # Background color changing
    background_anim_timer += (dt * 60)
    if background_anim_timer >= bg_anim_timer_length:
      background_anim_timer = 0
    time = abs(background_anim_timer - (bg_anim_timer_length/2))            
    curr_bg_color = bg_color_check(time, False)
    window.fill(curr_bg_color) 
    
    
    # Background animation setup
    speed = 10      
    bg_anim_loop()
    bg_timer_test()   
        
    if level_info_list[lv_number-1][2] == 3:
      bg_obj_change_test()

    #draw objects
    for o in lv.all:                         
      o.draw(window)
      if o==circle:
        ddir = Vector2(o.radius).rotate_rad(o.angle)
        pygame.draw.line(window,[255,255,255],o.pos,o.pos + ddir)

    # Now draw all FOREGROUND objects
    fg_anim_loop()
   
    # Create a rectangle for the bottom display    
    boxspacer = 10
    box_height_offset = 100
    pygame.draw.rect(window, [100,100,100], pygame.Rect((0, height-box_height_offset), (width, box_height_offset))) # Outer box
    # Color changing box
    pygame.draw.rect(window, bg_color_check(time, True), pygame.Rect((boxspacer, (height-box_height_offset)+boxspacer), (width-2*boxspacer, box_height_offset-2*boxspacer))) # Inner box          
    pygame.draw.rect(window, [200, 200, 200], pygame.Rect((boxspacer*2, (height-box_height_offset)+boxspacer*2), (width-4*boxspacer, box_height_offset-4*boxspacer)))
        
    # Display text for the bottom display    
    ## Draw Text
    attempts_left_text = font.render(f"LIVES: {lives}", True, [0,0,0])
    attempts_left_text_rect = attempts_left_text.get_rect(center = (width/8, height-(box_height_offset/2)))
    window.blit(attempts_left_text, attempts_left_text_rect)
    
    level_name_text = font_large.render(f"{lv_number}: {lv_name}", True, [0,0,0])    
    level_name_text_rect = level_name_text.get_rect(center = (width/2, height-(box_height_offset/2)))        
    window.blit(level_name_text, level_name_text_rect)
    


    # update the display
    pygame.display.update()

    # delay for correct timing
    clock.tick(fps)



