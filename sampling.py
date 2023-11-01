# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 15:19:07 2023

@author: wmy
"""

import numpy as np
import matplotlib.pyplot as plt

def normalize(x):
    return x / np.linalg.norm(x)

def get_coordinate_axes(normal_vector):
    w = normalize(normal_vector)
    arg = np.argmin(w)
    u = w.copy()
    u[np.arange(3)!=arg] = np.array([1, -1]) * w[np.arange(3)!=arg][::-1]
    u[arg] = 0
    u = normalize(u)
    v = np.cross(w, u)
    return u, v, w

def uniform_hemisphere_sample(normal_vector):
    u, v, w = get_coordinate_axes(normal_vector)
    xi1, xi2 = np.random.uniform(0, 1, 2)
    x = np.cos(2*np.pi*xi2) * np.sqrt(1-(1-xi1)**2)
    y = np.sin(2*np.pi*xi2) * np.sqrt(1-(1-xi1)**2)
    z = 1 - xi1
    wi = x * u + y * v + z * w
    pdf_wi = 1 / (2*np.pi)
    return wi, pdf_wi

def cosine_weighted_hemisphere_sample(normal_vector):
    u, v, w = get_coordinate_axes(normal_vector)
    xi1, xi2 = np.random.uniform(0, 1, 2)
    x = np.cos(2*np.pi*xi2) * np.sqrt(xi1)
    y = np.sin(2*np.pi*xi2) * np.sqrt(xi1)
    z = np.sqrt(1-xi1)
    wi = x * u + y * v + z * w
    pdf_wi = (1/np.pi) * np.sqrt(1-xi1)
    return wi, pdf_wi
