# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 14:25:51 2023

@author: wmy
"""

import numpy as np
import matplotlib.pyplot as plt
from bvh import BVH

class Model(object):
    
    def __init__(self, vertices, triangles):
        self.bvh = BVH()
        self.vertices = vertices
        self.triangles, bounding_boxes = self.bvh.build(vertices, triangles)
        self.bounding_boxes = np.array(bounding_boxes)
        pass
    
    def transform(self, M):
        v = np.concatenate([self.vertices, np.ones((self.vertices.shape[0], 1))], axis=1)
        b = np.concatenate([self.bounding_boxes, np.ones((self.bounding_boxes.shape[0], 1))], axis=1)
        v = np.dot(M, v.T).T
        b = np.dot(M, b.T).T
        self.vertices = v[:, :3]
        self.bounding_boxes = b[:, :3]
        pass
    
    def hit(self, ray_origin, ray_direction):
        triangle, distance = self.bvh.hit(ray_origin, ray_direction, self.vertices, \
                                          self.triangles, self.bounding_boxes, self.bvh)
        return triangle, distance
    
    pass
        
        

    