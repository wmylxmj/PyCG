# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 21:44:41 2023

@author: wmy
"""

import numpy as np
from transform import Mrodrigues

class Camera(object):
    
    def __init__(self, view_up_vector=np.array([0, 1, 0]), \
                 gaze_angle=[0, 0], eye_position=np.zeros((3)), \
                 z_near=1, z_far=100, aspect=1, fov=np.pi/3):
        
        self.__view_up_vector = view_up_vector
        self.__gaze_angle = gaze_angle
        self.__eye_position = eye_position
        
        self.__z_near = z_near
        self.__z_far = z_far
        self.__aspect = aspect
        self.__fov = fov
        
        self.update_coordinate_system()
        self.update_Mcam()
        self.update_Mper()
        self.update_Mview()
        pass
    
    @property
    def gaze_angle(self):
        return self.__gaze_angle
    
    @property
    def gaze_direction(self):
        theta_x, theta_y = self.gaze_angle
        y = np.sin(theta_y)
        x = np.cos(theta_y) * np.sin(theta_x)
        z = - np.cos(theta_y) * np.cos(theta_x)
        return np.array([x, y, z])
    
    @property
    def view_up_vector(self):
        return self.__view_up_vector
            
    @property
    def coordinate_system(self):
        return self.__coordinate_system
    
    def update_coordinate_system(self):
        g = self.gaze_direction
        t = self.view_up_vector
        w = - g / np.linalg.norm(g)
        u = np.cross(t, w) / np.linalg.norm(np.cross(t, w))
        v = np.cross(w, u)
        self.__coordinate_system = np.array([u, v, w]).T
        self.update_Mcam()
        pass
    
    @property
    def eye_position(self):
        return self.__eye_position
    
    @eye_position.setter
    def eye_position(self, eye_position):
        self.__eye_position = eye_position
        self.update_Mcam()
        pass
    
    def resize(self, size):
        width, height = size
        far_near_scale = self.z_far / self.z_near
        self.z_near = height / (2 * np.tan(self.fov/2))
        self.z_far = far_near_scale * self.z_near
        self.aspect = width / height
        pass
    
    def rotate_xy(self, dtheta_x=0, dtheta_y=0):
        theta_x, theta_y = self.gaze_angle
        theta_x = theta_x + dtheta_x
        theta_y = theta_y + dtheta_y
        self.__gaze_angle = [theta_x, theta_y]
        x, y, z = self.gaze_direction
        Mthetax = Mrodrigues(np.array([0, 1, 0]), dtheta_x)
        Mthetay = Mrodrigues(np.array([z, 0, x]), dtheta_y)
        Mvup = np.dot(Mthetay, Mthetax)
        v = np.array([self.__view_up_vector]).T
        self.__view_up_vector = np.squeeze(np.array(np.dot(Mvup, v), dtype=float).T)
        self.update_coordinate_system()
        pass
    
    @property
    def z_near(self):
        return self.__z_near
    
    @z_near.setter
    def z_near(self, z_near):
        self.__z_near = z_near
        self.update_Mper()
        self.update_Mview()
        pass
    
    @property
    def z_far(self):
        return self.__z_far
    
    @z_far.setter
    def z_far(self, z_far):
        self.__z_far = z_far
        self.update_Mper()
        self.update_Mview()
        pass
    
    @property
    def aspect(self):
        return self.__aspect
        
    @aspect.setter
    def aspect(self, aspect):
        self.__aspect = aspect
        self.update_Mper()
        self.update_Mview()
        pass
        
    @property
    def fov(self):
        return self.__fov
    
    @fov.setter
    def fov(self, fov):
        self.__fov = fov
        self.update_Mper()
        self.update_Mview()
        pass
    
    @property
    def height(self):
        return 2 * self.z_near * np.tan(self.fov/2)
    
    @property
    def width(self):
        return 2 * self.z_near * np.tan(self.fov/2) * self.aspect
    
    def update_Mcam(self):
        Mrot, Mtrans = np.eye(4), np.eye(4)
        Mrot[:3, :3] = np.matrix(self.coordinate_system).T
        Mtrans[:3, -1] = - self.eye_position
        self.__Mcam = np.dot(Mrot, Mtrans) 
        pass
    
    @property
    def Mcam(self):
        return self.__Mcam
    
    @property
    def Morth(self):
        n, f = self.z_near, self.z_far
        h, w = self.height, self.width
        Morth = [[2/w, 0, 0, 0], \
                 [0, 2/h, 0, 0], \
                 [0, 0, 2/(n-f), -(n+f)/(n-f)], \
                 [0, 0, 0, 1]]
        return np.array(Morth)
        
    def update_Mper(self):
        n, f = self.z_near, self.z_far
        M_z = np.eye(4)
        M_z[2, 2] = -1
        Mpersp_ortho = [[n, 0, 0, 0], \
                        [0, n, 0, 0], \
                        [0, 0, n+f, -f*n], \
                        [0, 0, 1, 0]]
        Mper = np.dot(self.Morth, np.array(Mpersp_ortho))
        self.__Mper = np.dot(Mper, M_z)
        pass     
    
    @property
    def Mper(self):
        return self.__Mper
    
    def update_Mview(self):
        h, w = self.height, self.width
        Mview = [[w/2, 0, 0, w/2], \
                 [0, h/2, 0, h/2], \
                 [0, 0, 1, 0], \
                 [0, 0, 0, 1]]
        self.__Mview = np.array(Mview)
        pass
    
    @property
    def Mview(self):
        return self.__Mview
    
    @property
    def M(self):
        return np.dot(self.Mview, np.dot(self.Mper, self.Mcam))
    
    pass