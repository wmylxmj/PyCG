# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 16:54:34 2023

@author: wmy
"""

import numpy as np
import matplotlib.pyplot as plt

class OBJ(object):
    
    def __init__(self, fp=None):
        
        self.v = None
        self.vt = None
        self.vn = None
        
        self.f_v = None
        self.f_vn = None
        self.f_vt = None
        
        if fp != None:
            self.read(fp)
            pass
        
        pass
    
    def read(self, fp):
        
        with open(fp, 'r') as f:
            lines = f.readlines()
            pass        
        
        v = []
        vt = []
        vn = []        
        
        f_v = []
        f_vt = []
        f_vn = []    
        
        for line in lines:            
            if line.startswith("v "):
                vertex = list(map(float, line.strip().split()[1:]))
                v.append(vertex)
                pass            
            elif line.startswith("vt"):
                texture_vertex = list(map(float, line.strip().split()[1:]))
                vt.append(texture_vertex)
                pass            
            elif line.startswith("vn"):
                vertex_normal = list(map(float, line.strip().split()[1:]))
                vn.append(vertex_normal)
                pass           
            elif line.startswith("f "):
                points = line.strip().split()[1:]
                p1 = points[0]
                p2 = points[1]
                sample = p1.split("/")
                # split into triangles
                for p3 in points[2:]:           
                    face_vertex = [int(x.split('/')[0])-1 for x in [p1, p2, p3]]
                    f_v.append(face_vertex)     
                    # has vt
                    if len(sample) > 1 and len(sample[1]) > 0:
                        face_texture_vertex = [int(x.split('/')[1])-1 for x in [p1, p2, p3]]
                        f_vt.append(face_texture_vertex)
                        pass             
                    # has vn
                    if len(sample) == 3:
                        face_vertex_normal = [int(x.split('/')[2])-1 for x in [p1, p2, p3]]
                        f_vn.append(face_vertex_normal)
                        pass
                    p2 = p3
                    pass
                pass
            pass
        
        if len(v) > 0:
            self.v = np.array(v)
            pass
        if len(vt) > 0:
            self.vt = np.array(vt)
            pass       
        if len(vn) > 0:
            self.vn = np.array(vn)
            pass       
        if len(f_v) > 0:
            self.f_v = np.array(f_v, dtype=int)
            pass        
        if len(f_vt) > 0:
            self.f_vt = np.array(f_vt, dtype=int)
            pass      
        if len(f_vn) > 0:
            self.f_vn = np.array(f_vn, dtype=int)
            pass       
        
        pass
    
    pass
                    