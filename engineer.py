# -*- coding:utf-8 -*-
from pygame import surfarray
from package import numpy as np
from package import pygame as pg
from package import numba
jit,njit = numba.jit,numba.njit
surfarray = pg.surfarray
import time
from itertools import combinations
from tool import vector2
L=0.65
R=0.3
G=0.59
B=0.11
ITER=3



def scalx_array(array,sx):
    '''scalx array as scalx'''
    return np.repeat(np.repeat(array,sx,axis=1),sx,axis=0)

@njit
def subarray(array,pos,rect):
    return array[pos.x:pos.x+rect.x,pos.y:pos.y+rect.y]

@njit
def bloom(image):
    start=time.time()
    image_array = surfarray.array3d(image)
    # 获得亮度图
    brightness=(image_array[:,:,0]*G +image_array[:,:,1]*B + image_array[:,:,2] * B) / ((R+G+B)*256)
    # 获得亮区
    brightarea = image_array.copy()
    brightarea[brightness <= L] = (0,0,0)
    
    factor = np.array((8,), np.int32)
    # 卷积可分解
    last_soften = cloud_array.copy()
    for _ in range(ITER):
        soften = np.array(last_soften, np.int32) *factor
        soften[1:,:]  += last_soften[:-1,:] * factor
        soften[:-1,:] += last_soften[1:,:] * factor
        soften[:,1:]  += last_soften[:,:-1] * factor
        soften[:,:-1] += last_soften[:,1:] * factor
        last_soften = soften
    
    #soften = scipy.ndimage.gaussian_filter(image_array, sigma=ITER)    
    #image_array= (soften*0.5 + image_array*0.5)
    #image=surfarray.make_surface(image_array)
    print("用时",(time.time()-start),'ms')
    return image

@njit
def blomm2_operation(nia,access,radius,image_array):
    for acc in access:
        new_image_array[acc[0]:acc[0]+radius,acc[1]:acc[1]+radius]+=image_array
    new_image_array/=radius**2
@jit
def blomm2(image,radius):
    start=time.time()
    image_array = surfarray.array3d(image)
    newshape = (image_array.shape[0]+radius,image_array.shape[1]+radius,image_array.shape[2])
    access = combinations(range(radius),2)
    new_image_array = np.zeros(shape=newshape)
    blomm2_operation(new_image_array,access,radius,image_array)
    return surfarray.make_surface(new_image_array)
    
if __name__ == '__main__':
    arr = np.array([[1,2,3,4],[5,6,7,8]])