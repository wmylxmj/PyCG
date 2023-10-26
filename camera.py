# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 21:44:41 2023

@author: wmy
"""

import numpy as np
import transform

class Camera(object):
    
    def __init__(self, coordinate_system=np.eye(3), eye_position=np.zeros((3)), \
                 z_near=1, z_far=100, aspect=1, theta=np.pi/3):
        
        self.__coordinate_system = coordinate_system
        self.__eye_position = eye_position
        
        self.__z_near = z_near
        self.__z_far = z_far
        self.__aspect = aspect
        self.__theta = theta
        
        self.update_Mcam()
        self.update_Mper()
        self.update_Mview()
        pass
    
    @property
    def coordinate_system(self):
        return self.__coordinate_system
    
    @coordinate_system.setter
    def coordinate_system(self, coordinate_system):
        self.__coordinate_system = coordinate_system
        self.update_Mcam()
        pass
    
    def rotate(self, theta_x=0, theta_y=0, theta_z=0):
        Mrot = np.dot(transform.Mry(theta_y), transform.Mrx(theta_x))
        Mrot = np.dot(transform.Mrz(theta_z), Mrot)
        coord_sys_homo = np.concatenate([self.coordinate_system, np.ones((1, 3))], axis=0)
        coord_sys_homo = np.dot(Mrot, coord_sys_homo)
        self.coordinate_system = coord_sys_homo[:3, :3]
        pass
    
    @property
    def eye_position(self):
        return self.__eye_position
    
    @eye_position.setter
    def eye_position(self, eye_position):
        self.__eye_position = eye_position
        self.update_Mcam()
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
    
    def resize(self, size):
        width, height = size
        far_near_scale = self.z_far / self.z_near
        self.z_near = height / (2 * np.tan(self.theta/2))
        self.z_far = far_near_scale * self.z_near
        self.aspect = width / height
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
    def theta(self):
        return self.__theta
    
    @theta.setter
    def theta(self, theta):
        self.__theta = theta
        self.update_Mper()
        self.update_Mview()
        pass
    
    @property
    def gaze_direction(self):
        return - self.coordinate_system[:, 2]
    
    @property
    def view_up_vector(self):
        return self.coordinate_system[:, 1]
    
    @property
    def height(self):
        return 2 * self.z_near * np.tan(self.theta/2)
    
    @property
    def width(self):
        return 2 * self.z_near * np.tan(self.theta/2) * self.aspect
    
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