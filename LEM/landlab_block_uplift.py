#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 07:48:13 2020

@author: Bodo Bookhagen
"""
import numpy as np
from matplotlib import pyplot as pl

from landlab import RasterModelGrid
from landlab.components.diffusion.diffusion import LinearDiffuser
from landlab.plot import imshow_grid
from pylab import show, figure

#%% Create an uplifted block in the center of model domain
#Create a raster grid with 100 rows, 100 columns, and cell spacing of 1 m
n=100
mg = RasterModelGrid((n, n), 1.0)
z = mg.add_zeros('node', 'topographic__elevation')
mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)
#Create a diagonal fault across the grid
blockuplift_nodes = np.where( (mg.node_y < 55) & (mg.node_y > 45) &
                              (mg.node_x < 55) & (mg.node_x > 45) )
z[blockuplift_nodes] += 10.0

# View the initial grid
figure()
imshow_grid(mg, 'topographic__elevation', cmap='viridis', grid_units=['m','m'])
show()

linear_diffusivity=0.01 #in m2 per year
ld = LinearDiffuser(grid=mg, linear_diffusivity=linear_diffusivity)

dt = 100.

#Evolve landscape
for i in range(25):
        ld.run_one_step(dt)

#Plot new landscape
figure()
imshow_grid(mg, 'topographic__elevation', cmap='viridis', grid_units=['m','m'])
show()

#%% Create an uplifted block in the center of model domain and continue to uplift this block - use only linear diffusion modeling
#Create a raster grid with 100 rows, 100 columns, and cell spacing of 1 m
n=100
mg = RasterModelGrid((n, n), 1.0)
z = mg.add_zeros('node', 'topographic__elevation')
mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)
#Create a diagonal fault across the grid
blockuplift_nodes = np.where( (mg.node_y < 55) & (mg.node_y > 45) &
                              (mg.node_x < 55) & (mg.node_x > 45) )
z[blockuplift_nodes] += 10.0

# View the initial grid
figure()
imshow_grid(mg, 'topographic__elevation', cmap='viridis', grid_units=['m','m'], plot_name='Initial Block uplift topography')
show()

linear_diffusivity=0.01 #in m2 per year
ld = LinearDiffuser(grid=mg, linear_diffusivity=linear_diffusivity)

dt = 100.

#Evolve landscape and continue to uplift block at every time step
rock_uplift_rate = 0.01 #m/yr
time_steps = 25
for i in range(time_steps):
    z[blockuplift_nodes] += rock_uplift_rate * dt #uplift the block nodes
    ld.run_one_step(dt)

#Plot new landscape
figure()
imshow_grid(mg, 'topographic__elevation', cmap='viridis', grid_units=['m','m'], plot_name='Block uplift with linear diffusion after %d time steps with uplift rate %02.3f m/yr'%(time_steps,rock_uplift_rate ) )
show()
