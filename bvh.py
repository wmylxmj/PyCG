# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 22:32:44 2023

@author: wmy
"""

import numpy as np

class BoundingBox(object):
    
    def __init__(self, aa, bb):
        self.aa = aa
        self.bb = bb
        pass
    
    def hit(self, ray_origin, ray_direction):
        t_aa = (self.aa - ray_origin) / ray_direction
        t_bb = (self.bb - ray_origin) / ray_direction
        t_before = np.minimum(t_aa, t_bb)
        t_after = np.maximum(t_aa, t_bb)
        t_in = np.max(t_before)
        t_out = np.min(t_after)
        # no intersection or behind the ray
        if t_in > t_out or t_out < 0:
            return False
        return True
        
    pass


class BVH(object):
    
    def __init__(self):
        self.childs = []
        self.bounding_box = BoundingBox(np.array([-np.inf]*3), np.array([np.inf]*3))
        self.triangles = []
        pass
    
    def build(self, vertices, triangles, maxntris=2):
        vtris = vertices[triangles]
        centers = np.array(np.sum(vtris, axis=1)/3, dtype=float)
        self.bounding_box.aa = np.array([np.min(vtris[:, :, 0]), \
                                         np.min(vtris[:, :, 1]), \
                                         np.min(vtris[:, :, 2])])
        self.bounding_box.bb = np.array([np.max(vtris[:, :, 0]), \
                                         np.max(vtris[:, :, 1]), \
                                         np.max(vtris[:, :, 2])])
        if len(triangles) <= maxntris:
            self.triangles = triangles
            return self
        axis = int(np.argmax(self.bounding_box.bb-self.bounding_box.aa))
        key = centers[:, axis].tolist()
        args = sorted(range(len(triangles)), key=lambda x: key[x])
        sorted_triangles = triangles[args]
        left_tris = sorted_triangles[:len(triangles)//2]
        right_tris = sorted_triangles[len(triangles)//2:]
        left, right = BVH(), BVH()
        left.build(vertices, left_tris)
        right.build(vertices, right_tris)
        self.childs = [left, right]
        return self
    
    pass


def normalize(x):
    return x / np.linalg.norm(x)

def hit_triangle(ray_origin, ray_direction, triangle):
    p0, p1, p2 = triangle[0], triangle[1], triangle[2]
    n = normalize(np.cross(p1-p0, p2-p1))
    # if parallel
    if np.inner(n, ray_direction) == 0:
        return np.inf
    # the triangle normal vector is opposite to the ray direction
    n = n * -np.sign(np.inner(n, ray_direction))
    # intersection point
    t = (np.inner(n, p0)-np.inner(ray_origin, n)) / np.inner(ray_direction, n)
    # if the triangle is behind the ray
    if t < 0:
        return np.inf
    p = ray_origin + ray_direction * t
    # determine whether the intersection point is in the triangle
    c1 = np.cross(p1-p0, p-p0)
    c2 = np.cross(p2-p1, p-p1)
    c3 = np.cross(p0-p2, p-p2)
    if np.inner(c1, n)>0 and np.inner(c2, n)>0 and np.inner(c3, n)>0:
        return t
    if np.inner(c1, n)<0 and np.inner(c2, n)<0 and np.inner(c3, n)<0:
        return t
    return np.inf

def hit_triangles(ray_origin, ray_direction, vertices, triangles):
    res = list(map(lambda x: hit_triangle(ray_origin, ray_direction, x), vertices[triangles]))
    arg = np.argmin(res)
    return triangles[arg], res[arg]
    
def hit_bvh(ray_origin, ray_direction, vertices, bvh:BVH):
    if len(bvh.triangles) > 0:
        return hit_triangles(ray_origin, ray_direction, vertices, bvh.triangles)
    triangle, distance = None, np.inf
    for child in bvh.childs:
        if child.bounding_box.hit(ray_origin, ray_direction):
            triangle_candidate, distance_candidate = hit_bvh(ray_origin, ray_direction, vertices, child)
            if distance_candidate < distance:
                distance = distance_candidate
                triangle = triangle_candidate
                pass
            pass
        pass
    return triangle, distance
        