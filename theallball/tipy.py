import json
import os
import sys
from turtle import color


from physics_objects import Polygon,Circle,UniformCircle,UniformPolygon,world_poly,world_rect,to_uniform,Elevator,Spinner
import pygame
import math


os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
width, height = 1600, 800
window = pygame.display.set_mode([width, height])
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

def file_to_level(fname):  
  #Dict that represents the whole level, partitioned into arrays
  leveldata = {
    '' : [],
    'spikes' : [],
    'bumpers' : [],
    'special': [],
    'checkpoints' : [],
    'gravitationals' : [],
    'lifeadders':[],
    'mobile': [],
    'elevators': [],
    'spinners' : [],
    'nextlvl' : None,
    'foreground': [],
    'windows': [],
    'danger': [],
  }

  layerdata = {
    '' : [],
    'layer1' : []
  }
  #Dict that relates a numerical ID to a world object.
  id_poly = {

  }

  colors = {
    '' : [0,0,0],
    'bumpers' : [0,0,255],
    'special' : pygame.Color("#5c2414"),
    'special_alt' : pygame.Color('#ffa500'),
    'gravitationals' : pygame.Color("#712B75"),
    'gravitationals_flipped': pygame.Color("#006400"),
    'spikes' : [255,0,0],
    'door' : pygame.Color("#D49B54"),
    'next' : pygame.Color("#000000"),
    'windows' : pygame.Color("#444444"),
    'danger' : pygame.Color('#555555')
    # fdff00
  }

  # List of the inner-box (foreground) colors for each object type
  # Not called by any funciton. Just placeholder
  ## Foreground types:
  # danger - flashes red, matches spikes color
  # windows - shows current animated background

  colorsFront = {
    '': ["#FFFFFF"],
    'bumpers' : pygame.Color("#f8e0b5"),
    'special' : pygame.Color("#e48f77"),
    'gravitationals' : pygame.Color("#ba96c5"),    
    'special_alt' : pygame.Color('#f8e0b5'),
    'windows' : pygame.Color('#444444'),
    'danger' : pygame.Color('#555555')
  }

  #This function finds out where a generated object goes depending on its properties, and also modifies it if necessary.
  def check_door(o,r):
    id_poly[o['id']] = r
    # o['type'] checks the "Type" field in Tiled
    if o['type'] == "special":
      r.res = 0.2
      r.fric  = 0.6
    if o['type'] == "spikes":
      r.spike = True

    if o['type'] == "gravitationals":
      r.flipped = False

    if o['type'] == "windows":
      r.windows = True
      r.color = colorsFront['windows']
    
    if o['type'] == "danger":      
      r.color = colorsFront['danger']

    if 'properties' in o:
      prop = dict([(p['name'],p['value']) for p in o['properties']])
      if 'flipped' in prop.keys():
        r.flipped = True
        r.color = colors['gravitationals_flipped']
      
      if 'res' in prop.keys(): r.res = prop['res']
      if 'fric' in prop.keys(): r.fric = prop['fric']
      if 'color' in prop.keys(): r.color = pygame.Color(prop['color'])

      if 'avel' in prop.keys():
        r.avel = prop['avel']
        return False
      
      if 'velx' in prop.keys():
        if 'vely' in prop.keys():
          r.vel = [prop['velx'], prop['vely']]
          return False
        return False
      
      if 'mass' in prop.keys():
        for arr in leveldata.values():
          if arr is list and r in arr:
            arr.remove(r)
        r.mass = prop['mass']
        leveldata['mobile'].append(r)
    if o['name'] == "next":
      r.color = colors['next']
      leveldata['nextlvl'] = r
      return False    
    return False
      
  # lines 20 - 124 go at the start of this funciton
  with open(fname,'r') as f:
    data = f.read()
    fulldata = json.loads(data)
    f.close()
    for q in fulldata['layers']:
      # foreground layer implementation 
      if q['name'] == "foreground":
        for o in q['objects']:
          t = o['type']
          if 'ellipse' in o:
            rad = o['width']/2
            pos2 = (o['x'] + rad,o['y'] + rad)
            r = Circle(radius= rad,pos=pos2,color=colors[t])
            if check_door(o,r):
              continue
            if r.color == colorsFront['windows']:
              leveldata['windows'].append(r)
            elif r.color == colorsFront['danger']:
              leveldata['danger'].append(r)
            else:
              leveldata['foreground'].append(r)
            continue
          if 'polygon' in o:
            n_off = [(b['x'],b['y']) for b in o['polygon']]
            r = Polygon(pos=(o['x'],o['y']),offsets=n_off,color=colors[t],reverse=True)
            if 'uniform' in str(o):
                r = to_uniform(r)
                r.mass = math.inf
            if check_door(o,r):
              continue            
            if r.color == colorsFront['windows']:
              leveldata['windows'].append(r)
            elif r.color == colorsFront['danger']:
              leveldata['danger'].append(r)
            else:
              leveldata['foreground'].append(r)
            continue
          x = o['x']
          y = o['y']
          w = o['width']
          h = o['height']
          r = world_rect((x,y),(x+w,y+h),color = colors[t])
          if 'uniform' in str(o):
            r = to_uniform(r)
            r.mass = math.inf
          if check_door(o,r):
            continue
          leveldata['foreground'].append(r)

      if q['name'] == "checkpoints":
        for o in q['objects']:
          r =  Circle(0.6 * 30,color=[0,255,255],pos = (o['x'],o['y']))
          leveldata['checkpoints'].append(r)
      
      if q['name'] == "lifeadders":
        for o in q['objects']:
          r =  Circle(0.6 * 30,color=[0,255,0],pos = (o['x'],o['y']))
          leveldata['lifeadders'].append(r)
          

      if q['name'] == 'main':
        for o in q['objects']:
          t = o['type']
          if 'ellipse' in o:
            rad = o['width']/2
            pos2 = (o['x'] + rad,o['y'] + rad)
            r = Circle(radius= rad,pos=pos2,color=colors[t])
            if check_door(o,r):
              continue
            leveldata[t].append(r)
            continue
          if 'polygon' in o:
            n_off = [(b['x'],b['y']) for b in o['polygon']]
            r = Polygon(pos=(o['x'],o['y']),offsets=n_off,color=colors[t],reverse=True)
            if 'uniform' in str(o):
                r = to_uniform(r)
                r.mass = math.inf
            if check_door(o,r):
              continue
            leveldata[t].append(r)
            continue
          x = o['x']
          y = o['y']
          w = o['width']
          h = o['height']
          r = world_rect((x,y),(x+w,y+h),color = colors[t])
          if 'uniform' in str(o):
            r = to_uniform(r)
            r.mass = math.inf
          if check_door(o,r):
            continue
          leveldata[t].append(r)

      if q['name'] == "elevators":
        for o in q['objects']:
          prop = dict([(p['name'],p['value']) for p in o['properties']])
          e = Elevator(polygon=id_poly[prop['poly_reference']],location_p1=(prop['p1x'],prop['p1y']),location_p2=(prop['p2x'],prop['p2y']),trip_time = prop['duration'])
          e.ctype = prop['loop_type']
          leveldata['elevators'].append(e)

      if q['name'] == "spinners":
        for o in q['objects']:
          prop = dict([(p['name'],p['value']) for p in o['properties']])
          e = Spinner(polygon=id_poly[prop['poly_reference']],angletimestring=prop['angletimes'])
          leveldata['spinners'].append(e)
  return leveldata

def file_to_background(fname):  
  #Dict that represents the whole level, partitioned into arrays
  layerdata = {
    '' : [],
    'layer1' : [],
    'layer2' : [],
    'layer3' : [],

  }
  #Dict that relates a numerical ID to a world object.
  id_poly = {

  }

  colors = {
    '' : [0,0,0],
    'bumpers' : [0,0,255],
    'special' : pygame.Color("#5c2414"),
    'special_alt' : pygame.Color('#ffa500'),
    'gravitationals' : pygame.Color("#712B75"),
    'gravitationals_flipped': pygame.Color("#006400"),
    'spikes' : [255,0,0],
    'door' : pygame.Color("#D49B54"),
    'next' : pygame.Color("#000000"),
    'windows' : pygame.Color("#444444"),
    'danger' : pygame.Color('#555555')
    # fdff00
  }

  # List of the inner-box (foreground) colors for each object type
  # Not called by any funciton. Just placeholder
  ## Foreground types:
  # danger - flashes red, matches spikes color
  # windows - shows current animated background

  colorsFront = {
    '': ["#FFFFFF"],
    'bumpers' : pygame.Color("#f8e0b5"),
    'special' : pygame.Color("#e48f77"),
    'gravitationals' : pygame.Color("#ba96c5"),    
    'special_alt' : pygame.Color('#f8e0b5'),
    'windows' : pygame.Color('#444444'),
    'danger' : pygame.Color('#555555')
  }

  #This function finds out where a generated object goes depending on its properties, and also modifies it if necessary.
  def check_door(o,r):
    id_poly[o['id']] = r
    # o['type'] checks the "Type" field in Tiled
    if o['type'] == "special":
      r.res = 0.2
      r.fric  = 0.6
    if o['type'] == "spikes":
      r.spike = True

    if o['type'] == "gravitationals":
      r.flipped = False

    if o['type'] == "windows":
      r.windows = True
      r.color = colorsFront['windows']
    
    if o['type'] == "danger":      
      r.color = colorsFront['danger']

    if 'properties' in o:
      prop = dict([(p['name'],p['value']) for p in o['properties']])
      if 'flipped' in prop.keys():
        r.flipped = True
        r.color = colors['gravitationals_flipped']
      
      if 'res' in prop.keys(): r.res = prop['res']
      if 'fric' in prop.keys(): r.fric = prop['fric']
      if 'color' in prop.keys(): r.color = pygame.Color(prop['color'])

      if 'avel' in prop.keys():
        r.avel = prop['avel']
        return False
      
      if 'velx' in prop.keys():
        if 'vely' in prop.keys():          
          r.vel = pygame.Vector2(prop['velx'], prop['vely'])
          return False
        r.vel = pygame.Vector2(prop['velx'], 0)
        return False

  # Process each layer individually
  with open(fname,'r') as f:
    data = f.read()
    fulldata = json.loads(data)
    f.close()
    for q in fulldata['layers']:      
        for o in q['objects']:      
          t = o['type']
          b = o['name']
          if 'ellipse' in o:
            rad = o['width']/2
            pos2 = (o['x'] + rad,o['y'] + rad)
            r = Circle(radius= rad,pos=pos2,color=colors[t])
            if check_door(o,r):
              continue
            layerdata[q['name']].append(r)
            continue
          if 'polygon' in o:
            n_off = [(b['x'],b['y']) for b in o['polygon']]
            r = Polygon(pos=(o['x'],o['y']),offsets=n_off,color=colors[t],reverse=True)
            if 'uniform' in str(o):
                r = to_uniform(r)
                r.mass = math.inf
            if check_door(o,r):
              continue                                    
            layerdata[q['name']].append(r)                        
            continue
          x = o['x']
          y = o['y']
          w = o['width']
          h = o['height']
          r = world_rect((x,y),(x+w,y+h),color = colors[t])
          if 'uniform' in str(o):
            r = to_uniform(r)
            r.mass = math.inf
          if check_door(o,r):
            continue
          layerdata[q['name']].append(r)
    return layerdata    

os.chdir(sys.path[0])
#print(os.getcwd())