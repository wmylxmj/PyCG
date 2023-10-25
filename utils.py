# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 15:03:29 2023

@author: wmy
"""

import numpy as np

def get_face_normals(vertices, face_vertices):
    face_vectors = vertices[face_vertices]
    face_normals = np.cross(face_vectors[:, 2]-face_vectors[:, 1], \
                            face_vectors[:, 1]-face_vectors[:, 0])
    return face_normals

def face_visible(face_normals, gaze_direction):
    norm = np.linalg.norm(face_normals, axis=1) * np.linalg.norm(gaze_direction)
    cos_angle = np.sum(face_normals*gaze_direction, axis=1) / norm
    return cos_angle > 0
    

                      