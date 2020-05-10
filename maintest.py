import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from math import *
from collision import *
from point import *

from objloader import *
import FPSM

bxyz = []
line = False
dm = 0
coll = False
fres = 0
sres = 0
cam = [0, 0, 0]

def bullet():
    global bxyz
    speed = 0.1
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    x, y, z = m[12], m[13], m[14]
    if copysign(1, x) == -1 and x <= 0:
        glTranslate(speed, 0, 0)
    if copysign(1, x) == 1 and x >= 0:
        glTranslate(-speed, 0, 0)

    if copysign(1, y) == -1 and y <= 0:
        glTranslate(0, speed, 0)
    if copysign(1, y) == 1 and y >= 0:
        glTranslate(0, -speed, 0)

    if copysign(1, z) == -1 and z <= 0:
        glTranslate(0, 0, speed)
    if copysign(1, z) == 1 and z >= 0:
        glTranslate(0, 0, -speed)
        
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    bxyz = [m[12], m[13], m[14]]

def distance(x1, y1, x2, y2):
    dist = sqrt(((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1)))
    print(dist)
    return dist

def moving():
    global dm
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    keys = pygame.key.get_pressed()

    if keys[K_w] or keys[K_s] or keys[K_a] or keys[K_d]:
        fwd = 0.5*(keys[K_w]-keys[K_s])
        strafe = 0.5*(keys[K_a]-keys[K_d])
        if abs(fwd) or abs(strafe):
            glTranslate(fwd*m[2]*dm,0 ,fwd*m[10]*dm)
            glTranslate(strafe*m[0]*dm,0 ,strafe*m[8]*dm)
        if dm < 0.5: dm += 0.01
    else:
        dm = 0

def drawXYZ():
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3d(0, 0, 0)
    glVertex3d(100, 0, 0)

    glColor3f(0, 1, 0)
    glVertex3d(0, 0, 0)
    glVertex3d(0, 100, 0)

    glColor3f(0, 0, 1)
    glVertex3d(0, 0, 0)
    glVertex3d(0, 0, -100)

    glColor3f(1, 1, 1)
    glEnd()

def colcheck(r1, r2):
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    distance = sqrt((m[12]) * (m[12]) +
                           (m[13]) * (m[13]) +
                           (m[14]) * (m[14]))
    return distance <= r1+r2

def colhandler():
    global fres,sres,coll,line
    keys = pygame.key.get_pressed()
    fwd = 5*(keys[K_w]-keys[K_s])
    strafe = 5*(keys[K_a]-keys[K_d])
    if  coll or line:
        if abs(fwd) or abs(strafe):
            if abs(fwd) and abs(strafe):
                fres = -fwd
                sres = -strafe
                m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                glTranslate(-fwd*m[2],0 ,-fwd*m[10])
                coll = False
                line = False
            else:
                fres = -fwd
                sres = -strafe
                m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                glTranslate(-fwd*m[2],0 ,-fwd*m[10])
                glTranslate(-strafe*m[0],0 ,-strafe*m[8])
                coll = False
                line = False
        else:
            m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
            glTranslate(fres*m[2],0 ,fres*m[10])
            glTranslate(sres*m[0],0 ,sres*m[8])
            coll = False
            line = False

def pLine(x1 ,z1, x2, z2, px, pz):
    buffer = 1
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    d1 = distance(px, pz, m[12] + x1, m[14] +z1)
    d2 = distance(px, pz, m[12] + x2, m[14] +z2)
    dline = distance(m[12]+x1 ,m[14]+z1 ,m[12]+x2 ,m[14]+z2)
    #print(d1, d2, dline)
    if (d1+d2 >= dline - buffer) and (d1+d2 <= dline + buffer): return True
    else: False

def main():
    global coll,line,cam
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 1, 512)
    viewport = (800,600)
    hx = viewport[0]/2
    hy = viewport[1]/2
    screen = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    pygame.mouse.set_pos(hx / 2, hy / 2)
   
    glMatrixMode(GL_PROJECTION)
    gluPerspective(90, viewport[0]/viewport[1], 0.01, 10000)
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])

    glEnable (GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

    #Loading objects
    lsfx = os.path.join(scriptDIR,"Game Objects\\Weapon\\sfx\\laser.wav")
    effect1 = pygame.mixer.Sound(lsfx)
    effect1.set_volume(0.2)
    
    i = 0
    direct = os.path.join(scriptDIR, "Game Objects\\Weapon\\Animated")
    guna = [None for _ in range(8)]
    for filename in os.listdir(direct):
        if filename.endswith(".obj"):
            obj1 = os.path.join(direct, filename)
            guna[i] = OBJ(obj1,swapyz = True)
            i = i + 1
        else:
            continue

    obj1 = os.path.join(scriptDIR,"Game Objects\\Platform\\1\\plat2.obj")
    world = OBJ(obj1,swapyz = True)
    
    obj2 = os.path.join(scriptDIR,"Game Objects\\Robots\\4\\boss.obj")
    rob1 = OBJ(obj2,swapyz = True)
    rob1mid = objcenter(obj2)
    obj2 = os.path.join(scriptDIR,"Game Objects\\Robots\\4\\rocketleft.obj")
    rocketleft = point(obj2)

    clock = pygame.time.Clock()
    exit = True
    i = 0
    fire = False
    shot = True

    while exit:
        
        clock.tick(40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()  

        #EXIT GAME
        if keys[pygame.K_ESCAPE]:
            exit = False
 
        
            
        #UP_DOWN
        mup = -2 * (keys[K_UP]-keys[K_DOWN])
        if abs(mup):
            mup = mup * 4
            glTranslatef(0, mup, 0)

        glLightfv(GL_LIGHT0, GL_POSITION, [1, -1, 1, 0])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 

        glPushMatrix()
        glTranslate(30, 0, 0)
        glTranslate(0, -170, 0)
        glRotate(-90, 1, 0, 0) 
        glScale(50, 50, 50) 
        glCallList(world.gl_list)
        glPopMatrix()

        glPushMatrix()
        glTranslate(30, 0, 0)
        glTranslate(0, -40, 0)
        glRotate(-90, 1, 0, 0)
        glScale(0.3, 0.3, 0.3)
        glCallList(rob1.gl_list)
        glPushMatrix()
        if shot:
            glTranslate(rocketleft[0], rocketleft[2], rocketleft[1])
            shot = False
        else: glTranslate(bxyz[0], bxyz[1], bxyz[2])
        bullet()
        gluSphere(gluNewQuadric(),20,100,20)
        glPopMatrix()
        glTranslate(rob1mid[0], rob1mid[2], rob1mid[1])
        glScale(15, 15, 15) 
        if colcheck(20.5, 20.5): 
            coll = True
        #if coll: glColor(1, 0, 0, 0.5)
        #else: glColor(0, 0, 0, 0.2)
       # gluSphere(gluNewQuadric(),20,100,20)
        #glColor(1, 1, 1, 1)
        glPopMatrix()

        
        fire = False  
        mov = FPSM.Spectator()
        if coll: colhandler()
        else:
            mov.get_keys()
            cam = mov.controls_3d(6, 0,'w','s','a','d')
            
            

        glPushMatrix()
        glLoadIdentity()
        glTranslate(10, -6, -15)
        glRotate(180, 0, 0, 1)
        glRotate(90, 1, 0, 0)
        glScale(0.5, 0.5, 0.5)
        pygame.mixer.stop()
        if pygame.mouse.get_pressed()[0]:
            fire = True
        if fire:
            effect1.play()
            moving()
            glCallList(guna[i].gl_list)
            i += 1
            if i == 8:
                fire, i = False, 0
        else:
            moving()
            glCallList(guna[0].gl_list)
        glPopMatrix()




        pygame.display.flip()

main()


