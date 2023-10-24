# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 20:50:48 2023

@author: wmy
"""

import numpy as np

def Mrx(theta):
    M = np.eye(4)
    core = [[np.cos(theta), -np.sin(theta)], \
            [np.sin(theta), np.cos(theta)]]
    M[1:3, 1:3] = core
    return M

def Mry(theta):
    M = np.eye(4)
    core = [[np.cos(theta), np.sin(theta)], \
            [-np.sin(theta), np.cos(theta)]]
    M[::2, ::2] = core
    return M

def Mrz(theta):
    M = np.eye(4)
    core = [[np.cos(theta), -np.sin(theta)], \
            [np.sin(theta), np.cos(theta)]]
    M[:2, :2] = core
    return M

def Mtrans(x=0, y=0, z=0):
    M = np.eye(4)
    M[:3, -1] = np.array([x, y, z])
    return M

def Mscale(x=1, y=1, z=1):
    M = np.eye(4)
    M[0, 0] = x
    M[1, 1] = y
    M[2, 2] = z
    return M
    
        