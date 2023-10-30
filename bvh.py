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
    

class BVHTree(object):
    
    def __init__(self):
        self.childs = []
        self.aa = None
        self.bb = None
        self.index = 0
        self.ntris = 0
        pass
    
    def sah(self, vertices, triangles):
        vtris = vertices[triangles]
        centers = np.array(np.sum(vtris, axis=1)/3, dtype=float)
        costs = []
        mids = []
        for axis in range(3):
            # sort the triangles
            key = centers[:, axis].tolist()
            sorted_args = sorted(range(len(triangles)), key=lambda x: key[x])
            sorted_vtris = vtris[sorted_args]
            left_aa = [np.min(sorted_vtris[0], axis=0)]
            left_bb = [np.max(sorted_vtris[0], axis=0)]
            right_aa = [np.min(sorted_vtris[-1], axis=0)]
            right_bb = [np.max(sorted_vtris[-1], axis=0)]
            for left_i in range(1, len(triangles)-1):
                right_i = len(triangles) - left_i
                left_aa.append(np.minimum(left_aa[-1], np.min(sorted_vtris[left_i], axis=0)))
                left_bb.append(np.maximum(left_bb[-1], np.max(sorted_vtris[left_i], axis=0)))
                right_aa.insert(0, np.minimum(right_aa[0], np.min(sorted_vtris[right_i], axis=0)))
                right_bb.insert(0, np.maximum(right_bb[0], np.max(sorted_vtris[right_i], axis=0)))
                pass
            left_aa = np.array(left_aa)
            left_bb = np.array(left_bb)
            right_aa = np.array(right_aa)
            right_bb = np.array(right_bb)
            left_length = left_bb - left_aa
            a, b, c = left_length[:, 0], left_length[:, 1], left_length[:, 2]
            left_s = 2 * (a*b + b*c + a*c)
            left_cost = left_s * np.linspace(1, len(triangles)-1, len(triangles)-1)
            right_length = right_bb - right_aa
            a, b, c = right_length[:, 0], right_length[:, 1], right_length[:, 2]
            right_s = 2 * (a*b + b*c + a*c)
            right_cost = right_s * (len(triangles) - np.linspace(1, len(triangles)-1, len(triangles)-1))
            total_cost = left_cost + right_cost
            mid = np.argmin(total_cost) + 1
            costs.append(total_cost[mid-1])
            mids.append(mid)
            pass
        axis = np.argmin(np.array(costs))
        mid = mids[axis]
        # sort the triangles
        key = centers[:, axis].tolist()
        sorted_args = sorted(range(len(triangles)), key=lambda x: key[x])
        sorted_triangles = triangles[sorted_args]
        return sorted_triangles, mid
    
    def split(self, vertices, triangles):
        vtris = vertices[triangles]
        centers = np.array(np.sum(vtris, axis=1)/3, dtype=float)
        aa = np.min(vtris, axis=(0, 1))
        bb = np.max(vtris, axis=(0, 1))
        axis = int(np.argmax(bb-aa))
        key = centers[:, axis].tolist()
        sorted_args = sorted(range(len(triangles)), key=lambda x: key[x])
        sorted_triangles = triangles[sorted_args]
        mid = len(triangles) // 2
        return sorted_triangles, mid
    
    def build(self, vertices, triangles, bounding_boxes=[], index=0, maxntris=2, using_sah=False):
        vtris = vertices[triangles]
        aa = np.min(vtris, axis=(0, 1))
        bb = np.max(vtris, axis=(0, 1))
        self.aa = len(bounding_boxes)
        self.bb = len(bounding_boxes) + 1
        bounding_boxes.extend([aa, bb])
        if len(triangles) <= maxntris:
            self.index = index
            self.ntris = len(triangles)
            return triangles, bounding_boxes
        if using_sah:
            sorted_triangles, mid = self.sah(vertices, triangles)
            pass
        else:
            sorted_triangles, mid = self.split(vertices, triangles)
            pass
        left, right = BVHTree(), BVHTree()
        left_tris, bounding_boxes = left.build(vertices, sorted_triangles[:mid], \
                                               bounding_boxes, index, maxntris)
        triangles[:mid] = left_tris
        right_tris, bounding_boxes = right.build(vertices, sorted_triangles[mid:], \
                                                 bounding_boxes, index+mid, maxntris)
        triangles[mid:] = right_tris
        self.childs = [left, right]
        return triangles, bounding_boxes
    
    pass


class BVH(object):
    
    def __init__(self):
        self.triangles = []
        self.bounding_boxes = []
        self.tree = BVHTree()
        pass
    
    def build(self, vertices, triangles):
        self.triangles, self.bounding_boxes = self.tree.build(vertices, triangles)
        pass
    
    def __hit(self, ray_origin, ray_direction, vertices, triangles, bounding_boxes, tree:BVHTree):
        if tree.ntris > 0:
            return hit_triangles(ray_origin, ray_direction, vertices, \
                                 triangles[tree.index:tree.index+tree.ntris])
        triangle, distance = None, np.inf
        for child in tree.childs:
            if BoundingBox(bounding_boxes[child.aa], bounding_boxes[child.bb]).hit(ray_origin, ray_direction):
                triangle_candidate, distance_candidate = self.__hit(ray_origin, ray_direction, \
                                                                    vertices, triangles, bounding_boxes, child)
                if distance_candidate < distance:
                    distance = distance_candidate
                    triangle = triangle_candidate
                    pass
                pass
            pass
        return triangle, distance
            
    def hit(self, ray_origin, ray_direction, vertices):
        return self.__hit(ray_origin, ray_direction, vertices, self.triangles, self.bounding_boxes, self.tree)
    
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
    
