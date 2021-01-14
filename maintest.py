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

#bxyz = []
line = False
dm = 0
coll = False
fres = 0
sres = 0
cam = [0, 0, 0]
move = pygame.math.Vector3(0, 0, 0)

class rocket():

    def __init__(self, sh):

        obj2 = os.path.join(scriptDIR,"Game Objects\\Robots\\4\\rocketleft.obj")
        self.rocketleft = point(obj2)
        glPushMatrix()
        glTranslate(self.rocketleft[0], self.rocketleft[2], self.rocketleft[1])
        self.m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
        glPopMatrix()
        self.x, self.y, self.z = self.m[12], self.m[13], self.m[14]
        self.s = 5
        self.h = sqrt((self.x**2)+(self.y**2)+(self.z**2))
        self.xn = -(self.x/self.h)
        self.yn = -(self.y/self.h)
        self.zn = -(self.z/self.h)
        self.shot = sh

    def update(self):
        f = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
        xa, ya, za = f[12], f[13], f[14]
        if self.h < 400 :
            if xa < 0:
                glTranslate(self.s*self.xn, 0, 0)
            else:
                glTranslate(-self.s*self.xn, 0, 0)

            if ya < 0:
                glTranslate(0, self.s*self.yn, 0)
            else:
                glTranslate(0, -self.s*self.yn, 0)

            if za < 0:
                glTranslate(0, 0, self.s*self.zn)
            else:
                glTranslate(0, 0, -self.s*self.zn)

    def draw(self):

        keys = pygame.key.get_pressed()
        glPushMatrix()
        if self.shot:
            glTranslate(self.rocketleft[0], self.rocketleft[2], self.rocketleft[1])
        self.update()
        k = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
        gluSphere(gluNewQuadric(),20,100,20)
        glPopMatrix()

def distance(x1, y1, z1, x2, y2, z2):
    dist = sqrt(((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1)) + ((z2-z1)*(z2-z1)))
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
    global coll,line,cam,bxyz,move
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

    '''
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
    '''

    obj1 = os.path.join(scriptDIR,"Game Objects\\Weapon\\Animated\\gun_000001.obj")
    gun = OBJ(obj1,swapyz = True)

    obj1 = os.path.join(scriptDIR,"Game Objects\\Platform\\1\\plat2.obj")
    world = OBJ(obj1,swapyz = True)
    
    obj2 = os.path.join(scriptDIR,"Game Objects\\Robots\\4\\boss.obj")
    rob1 = OBJ(obj2,swapyz = True)
    rob1mid = objcenter(obj2)


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
        if coll:
            move = (move[0]*2, 0, move[2]*2)
        glTranslate(-200+move[0], 0, 0+move[2])
        glTranslate(0, -40, 0)
        glRotate(-90, 1, 0, 0)
        glScale(0.3, 0.3, 0.3)
        glCallList(rob1.gl_list)

        glTranslate(rob1mid[0], rob1mid[2], rob1mid[1])

        if pygame.mouse.get_pressed()[0]:
            mv = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
            origin = pygame.math.Vector3()
            origin = gluUnProject(hx, hy, 0.0)
            
            target = pygame.math.Vector3()
            target = gluUnProject(hx, hy, 1)
            
            c = pygame.math.Vector3(rob1mid[0]*0.3, rob1mid[2]*0.3, rob1mid[1]*0.3)

            direction = pygame.math.Vector3(target[0] - origin[0], target[1] - origin[1], target[2] - origin[2])
            direction = pygame.math.Vector3.normalize(direction)

            Length = distance(origin[0], origin[1], origin[2], c[0], c[1], c[2])
            L = pygame.math.Vector3(c[0] - origin[0], c[1] - origin[1], c[2] - origin[2])
            move = L.normalize()

            glBegin(GL_LINES)
            glVertex(origin[0], origin[1], origin[2])
            glVertex(c[0], c[1], c[2])
            glEnd()

            tc = pygame.math.Vector3.dot(L, direction)

            if not (tc < 0):
                d = sqrt((Length*Length) - (tc*tc))
                if not (d > 100*1/0.3):
                    coll = True
                else: coll = False
            else: coll = False
        else: coll = False

        '''
        hit = False
        
        while not hit:
            end = (rob1mid[0] - oxyz[0])/drx
            t = abs((cx - oxyz[0])/drx)
            d = distance(cx, cy, cz, rob1mid[0], rob1mid[2], rob1mid[1])
            if d <= 100:
                coll = True
                hit = True
            else:
                t += 1
                cx = oxyz[0] + drx*t
                cy = oxyz[1] + dry*t
                cz = oxyz[2] + drz*t
            if t >= abs(end): hit = True
        '''   


        



         
        if colcheck(20.5, 100): 
            coll = True
        if coll: glColor(1, 0, 0, 0.5)
        else: glColor(0, 0, 0, 0.2)
        gluSphere(gluNewQuadric(),100*1/0.3,100,20)
        glColor(1, 1, 1, 1)
        glPopMatrix()

        
        fire = False  
        mov = FPSM.Spectator()
        if coll and False: colhandler()
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
            glCallList(gun.gl_list)
            i += 1
            if i == 8:
                fire, i = False, 0
        else:
            moving()
            glCallList(gun.gl_list)
        glPopMatrix()




        pygame.display.flip()

main()


