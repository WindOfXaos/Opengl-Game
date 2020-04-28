import pygame, math, numpy
from OpenGL.GL import *
from OpenGL.GLU import *

class Spectator:
    
    def get_keys(self):
        self.keys = dict((chr(i),int(v)) for i,v in \
        enumerate(pygame.key.get_pressed()) if i<256)

    def controls_3d(self,ms,mouse_button=1,w_key='w',s_key='s',a_key='a',\
                        d_key='d'):
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        """ The actual camera setting cycle """
        mouse_dx,mouse_dy = pygame.mouse.get_rel()
        #if pygame.mouse.get_pressed()[mouse_button]:, then indented block underneath
        look_speed = .2
        buffer = glGetDoublev(GL_MODELVIEW_MATRIX)
        c = (-1 * numpy.mat(buffer[:3,:3]) * \
            numpy.mat(buffer[3,:3]).T).reshape(3,1)
        # c is camera center in absolute coordinates, 
        # we need to move it back to (0,0,0) 
        # before rotating the camera
        glTranslate(c[0],c[1],c[2])
        m = buffer.flatten()
        glRotate(mouse_dx * look_speed, m[1],m[5],m[9])
        glRotate(mouse_dy * look_speed, m[0],m[4],m[8])
        
        # compensate roll
        glRotated(-math.atan2(-m[4],m[5]) * \
            57.295779513082320876798154814105 ,m[2],m[6],m[10])
        glTranslate(-c[0],-c[1],-c[2])

        # move forward-back or right-left
        # fwd =   .1 if 'w' is pressed;   -0.1 if 's'
        fwd = ms * (self.keys[w_key]-self.keys[s_key]) 
        strafe = ms * (self.keys[a_key]-self.keys[d_key])
        if abs(fwd) or abs(strafe):
            m = glGetDoublev(GL_MODELVIEW_MATRIX).flatten()
            glTranslate(fwd*m[2],0 ,fwd*m[10])
            glTranslate(strafe*m[0],0 ,strafe*m[8])

        buffer = glGetDoublev(GL_MODELVIEW_MATRIX)
        c = (-1 * numpy.mat(buffer[:3,:3]) * \
            numpy.mat(buffer[3,:3]).T).reshape(3,1)
        m = buffer.flatten()
        return c[0], c[1], c[2], m[0], m[1], m[2]
