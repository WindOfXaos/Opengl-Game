import os,sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from math import *
from objloader import *
import FPSM

viewport = (1920,1080)
hx = viewport[0]/2
hy = viewport[1]/2

'''
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
def pLine(x1 ,z1, x2, z2, px, pz):
    buffer = 1
    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
    d1 = distance(px, pz, m[12] + x1, m[14] +z1)
    d2 = distance(px, pz, m[12] + x2, m[14] +z2)
    dline = distance(m[12]+x1 ,m[14]+z1 ,m[12]+x2 ,m[14]+z2)
    if (d1+d2 >= dline - buffer) and (d1+d2 <= dline + buffer): return True
    else: False
'''

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

def distance(x1, y1, z1, x2, y2, z2):
    dist = sqrt(((x2-x1)*(x2-x1)) + ((y2-y1)*(y2-y1)) + ((z2-z1)*(z2-z1)))
    return dist

def init():
    global viewport,hx,hy

    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    pygame.init()
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

class World:
    def __init__(self, size = 50, angle = -90, x = 30, y = -170, z = 0):
        path = os.path.join(scriptDIR,"Game Objects\\Platform\\1\\plat2.obj")
        self.array = OBJ(path,swapyz = True)
        self.Size = [size*1, size*1, size*1]
        self.Angle = angle
        self.x = x
        self.y = y
        self.z = z

    def update(self):
        glPushMatrix()
        glTranslate(self.x, self.y, self.z)
        glRotate(self.Angle, 1, 0, 0) 
        glScale(self.Size[0], self.Size[1], self.Size[2]) 
        glCallList(self.array.gl_list)
        glPopMatrix()

class Gun:
    def __init__(self, x = 10, y = -6, z = -15, rotx = -90, roty = 0, rotz = 180, size = 0.5):
        self.gun = self.Load()
        path = os.path.join(scriptDIR,"Game Objects\\Weapon\\sfx\\laser.wav")
        self.effect = pygame.mixer.Sound(path)
        self.effect.set_volume(0.2)
        self.i = 0
        self.fire = False
        self.dm = 0
        self.x = x
        self.y = y
        self.z = z
        self.rot_x = rotx
        self.rot_y = roty
        self.rot_z = rotz
        self.Size = [size*1, size*1, size*1]
        
    def update(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslate(self.x, self.y, self.z)
        glRotate(self.rot_x, 1, 0, 0)
        glRotate(self.rot_z, 0, 0, 1)
        glScale(self.Size[0], self.Size[1], self.Size[2])
        pygame.mixer.stop()
        if pygame.mouse.get_pressed()[0]:
            self.fire = True
        if self.fire:
            self.effect.play()
            self.moving()
            glCallList(self.gun[self.i].gl_list)
            self.i += 1
            if self.i == 8:
                self.fire, self.i = False, 0
        else:
            self.moving()
            glCallList(self.gun[0].gl_list)
        glPopMatrix()

    def Load(self):
        i = 0
        direct = os.path.join(scriptDIR, "Game Objects\\Weapon\\Animated")
        gun = [None for _ in range(8)]
        for filename in os.listdir(direct):
            if filename.endswith(".obj"):
                obj1 = os.path.join(direct, filename)
                gun[i] = OBJ(obj1,swapyz = True)
                i = i + 1
            else:
                continue
        return gun

    def moving(self):
        m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
        keys = pygame.key.get_pressed()

        if keys[K_w] or keys[K_s] or keys[K_a] or keys[K_d]:
            fwd = 6*(keys[K_w]-keys[K_s])
            strafe = 6*(keys[K_a]-keys[K_d])
            if abs(fwd) or abs(strafe):
                glTranslate(fwd*m[2]*self.dm,0 ,fwd*m[10]*self.dm)
                glTranslate(strafe*m[0]*self.dm,0 ,strafe*m[8]*self.dm)
            if self.dm < 0.5: self.dm += 0.01
        else:
            self.dm = 0

class Robot:
    def __init__(self, x = -200, y = -40, z = 0, rotx = -90, roty = 0, rotz = 0,
     size = 0.3, r = 100, p = "Game Objects\\Robots\\4\\boss.obj"):
        path = os.path.join(scriptDIR, p)
        self.rob = OBJ(path,swapyz = True)
        self.robmid = OBJCenter(path, swapyz = True)

        self.x = x
        self.y = y
        self.z = z
        self.rot_x = rotx
        self.rot_y = roty
        self.rot_z = rotz
        self.Size = [size*1, size*1, size*1]
        self.rob_sphere_radius = r
        self.coll = False

        self.hit_direction = pygame.math.Vector3(0, 0, 0)
        self.origin = pygame.math.Vector3()
        self.target = pygame.math.Vector3()
        if size < 1 :
            self.c = pygame.math.Vector3(self.robmid.mid_x*self.Size[0], self.robmid.mid_y*self.Size[1], self.robmid.mid_z*self.Size[2])
        else:
            self.c = pygame.math.Vector3(self.robmid.mid_x*(1/self.Size[0]), self.robmid.mid_y*(1/self.Size[1]), self.robmid.mid_z*(1/self.Size[2]))

    def update(self):
        global hx,hy  
        glPushMatrix()
        glTranslate(self.x, self.y, self.z)
        glRotate(self.rot_x, 1, 0, 0)
        glScale(self.Size[0], self.Size[1], self.Size[2])
        glCallList(self.rob.gl_list)

        self.bullet_collision()

        if self.colcheck(20.5, self.rob_sphere_radius): 
            self.coll = True

        #Visual_Debugging
        if self.coll: glColor(1, 0, 0, 0.5)
        else: glColor(0, 0, 0, 0.2)
        gluSphere(gluNewQuadric(),self.rob_sphere_radius*(1/self.Size[0]),100,20)
        glColor(1, 1, 1, 1)

        glPopMatrix()

    def colcheck(self,r1,r2):
        m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
        distance = sqrt((m[12]) * (m[12]) +
                        (m[13]) * (m[13]) +
                        (m[14]) * (m[14]))
        return distance <= r1+r2

    def bullet_collision(self):
        glTranslate(self.robmid.mid_x, self.robmid.mid_y, self.robmid.mid_z)
        if pygame.mouse.get_pressed()[0]:
            self.origin = gluUnProject(hx, hy, 0.0)          
            self.target = gluUnProject(hx, hy, 1)
            #Dir => Bullet direction vector
            Dir = pygame.math.Vector3(self.target[0] - self.origin[0], self.target[1] - self.origin[1], self.target[2] - self.origin[2])
            Dir = pygame.math.Vector3.normalize(Dir)
            #L => Gun to robot center vector
            L = pygame.math.Vector3(self.c[0] - self.origin[0], self.c[1] - self.origin[1], self.c[2] - self.origin[2])
            Length = L.length()
            self.hit_direction = L.normalize()
            #tc => L vector projected on Dir
            tc = pygame.math.Vector3.dot(L, Dir)
            #Visual_Debugging
            glBegin(GL_LINES)
            glVertex(self.origin[0], self.origin[1], self.origin[2])
            glVertex(self.c[0], self.c[1], self.c[2])
            glEnd()
            if not (tc < 0):
                d = sqrt((Length*Length) - (tc*tc))
                if not (d > self.rob_sphere_radius*(1/self.Size[0])):
                    self.coll = True
                else: self.coll = False
            else: self.coll = False
        else: self.coll = False

class Game:
    def __init__(self):
        self.world = World()
        self.gun = Gun()
        self.robot = Robot()
        self.robot2 = Robot(p = "Game Objects\\Robots\\1\\rob1.obj", x = 200, r = 50)
        self.robot3 = Robot(p = "Game Objects\\Robots\\2\\red\\red.obj", z = -200, y = 0, r = 50, size = 10)
        self.coll = False
        self.fres = 0
        self.sres = 0
        
    def Load(self):

        #Loading objects

        '''
        path = os.path.join(scriptDIR,"Game Objects\\Weapon\\Animated\\gun_000001.obj")
        self.gun = OBJ(path,swapyz = True)
        '''
        
    def update(self):
        global hx,hy
        keys = pygame.key.get_pressed()

        #UP_DOWN
        mup = -1 * (keys[K_UP]-keys[K_DOWN])
        if abs(mup):
            glTranslatef(0, 5*mup, 0)

        self.world.update()

        self.robot.update()

        self.robot2.update()

        self.robot3.update()
        
        self.gun.update()

        mov = FPSM.Spectator()
        if self.coll and False: self.colhandler()
        else:
            mov.get_keys()
            mov.controls_3d(6, 0,'w','s','a','d')

    def colhandler(self):
        keys = pygame.key.get_pressed()
        fwd = 5*(keys[K_w]-keys[K_s])
        strafe = 5*(keys[K_a]-keys[K_d])
        if self.coll:
            if abs(fwd) or abs(strafe):
                if abs(fwd) and abs(strafe):
                    self.fres = -fwd
                    self.sres = -strafe
                    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                    glTranslate(-fwd*m[2],0 ,-fwd*m[10])
                    self.coll = False
                else:
                    self.fres = -fwd
                    self.sres = -strafe
                    m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                    glTranslate(-fwd*m[2],0 ,-fwd*m[10])
                    glTranslate(-strafe*m[0],0 ,-strafe*m[8])
                    self.coll = False
            else:
                m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
                glTranslate(self.fres*m[2],0 ,self.fres*m[10])
                glTranslate(self.sres*m[0],0 ,self.sres*m[8])
                self.coll = False

    def colcheck(self,r1,r2):
        m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
        distance = sqrt((m[12]) * (m[12]) +
                        (m[13]) * (m[13]) +
                        (m[14]) * (m[14]))
        return distance <= r1+r2

def main():

    init()
    clock = pygame.time.Clock()
    game = Game()

    while True:
        
        glLightfv(GL_LIGHT0, GL_POSITION, [1, -1, 1, 0])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 

        clock.tick(40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()  

        #EXIT GAME
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            quit()

        game.update()

        pygame.display.flip()

main()


