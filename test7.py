# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 19:18:41 2023

@author: wmy
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri
import PIL
from PIL import Image
from multiprocessing import Pool
from tqdm import tqdm

import camera
import utils
import transform
import fio
import utils
from model import Model
from sampling import cosine_weighted_hemisphere_sample, uniform_hemisphere_sample

o = fio.OBJ(r"test.obj")
m = Model(o.v, o.f_v)

M = transform.Mtrans(x=-np.mean(o.v[:, 0]), y=-np.mean(o.v[:, 1]), z=-np.min(o.v[:, 2]))
M = np.dot(transform.Mrx(-np.pi/2), M)
M = np.dot(transform.Mtrans(z=-60), M)

m.transform(M)

lv = np.array([[1, 0, 1], \
               [-1, 0, 1], \
               [-1, 0, -1], \
               [1, 0, -1]])
lt = np.array([[0, 1, 2], [0, 2, 3]], dtype=int)
l = Model(lv, lt)

M = transform.Mscale(50, 50, 50)
#M = np.dot(transform.Mrz(-np.pi/4), M)
M = np.dot(transform.Mtrans(x=np.mean(m.vertices[:, 0]), y=70, z=np.mean(m.vertices[:, 2])), M)
l.transform(M)

c = camera.Camera(fov=np.pi/3)
c.eye_position = np.array([0, 25, 0])
c.resize((1024, 1024))

z_neg = utils.normalize(c.gaze_direction)
y = utils.normalize(c.view_up_vector)
x = np.cross(z_neg, y)

w, h = int(c.width), int(c.height)

dhcomp = 2 * np.tan(c.fov/2) / h
dwcomp = dhcomp * c.aspect

hcomp0 = - np.tan(c.fov/2)
wcomp0 = hcomp0 * c.aspect

pixels = [(ph, pw) for ph in range(h) for pw in range(w)]
    
sample = 32
def shoot_ray(pixel):
    ph, pw = pixel
    pixel_val = np.array([0]*3)
    for i in range(sample):
        rh, rw = np.random.uniform(0, 1), np.random.uniform(0, 1)
        hcomp = hcomp0 + dhcomp * (ph + rh)
        wcomp = wcomp0 + dwcomp * (pw + rw)
        ray_direction = z_neg + hcomp * y + wcomp * x
        ltri, ldis = l.hit(c.eye_position, ray_direction)
        mtri, mdis = m.hit(c.eye_position, ray_direction)
        color = np.array([0]*3)
        if ldis < mdis:
            color = np.array([1]*3)
            pass
        elif mdis != np.inf:
            mvtri = m.vertices[mtri]
            normal = np.cross(mvtri[2]-mvtri[1], mvtri[1]-mvtri[0])
            if np.inner(normal, ray_direction) > 0:
                normal = -normal
                pass
            origin = c.eye_position + ray_direction * mdis
            wi, pdf_wi = cosine_weighted_hemisphere_sample(normal)
            pt_color = np.array([0]*3)
            src_color = np.array([0.5]*3)
            l2tri, l2dis = l.hit(origin, wi)
            if l2dis != np.inf:
                m2tri, m2dis = m.hit(origin, wi)
                if l2dis < m2dis:
                    pt_color = np.array([1]*3)
                    pass
                pass
            color = pt_color * src_color
            color = color / pdf_wi / sample
            pass
        pixel_val = pixel_val + color
        pass
    return pixel_val
    
if __name__ == "__main__":
    with Pool(32) as p:
        screen = list(tqdm(p.imap(shoot_ray, pixels)))
        pass
    screen = np.clip(screen, 0, 1)
    screen = np.reshape(np.uint8(np.array(screen)*255), (h, w, 3))
    screen = screen[::-1, :, :]
    img = Image.fromarray(screen)
    img.show()
