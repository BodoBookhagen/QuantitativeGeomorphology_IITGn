#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 17-Feb 2020

@author: Bodo Bookhagen
#setup landlab with conda:
conda create -n landlab spyder matplotlib landlab -c landlab

# now active the environment
source activate landlab
"""
#following: https://nbviewer.jupyter.org/github/landlab/tutorials/blob/master/component_tutorial/component_tutorial.ipynb

from landlab.components import LinearDiffuser
from landlab.plot import imshow_grid
from landlab import RasterModelGrid
import matplotlib.pyplot as pl
import numpy as np

#%% generate grid
mg = RasterModelGrid((80, 80), 5.)
z = mg.add_zeros('node', 'topographic__elevation')

#landlab stores this as an 1D array
mg.at_node['topographic__elevation'].shape
#spacing
mg.dy, mg.dx

#we want to run a simple linear diffusion. What do we need as input?
LinearDiffuser.input_var_names

#fix values at the bottom: closed edges on sides, open edges on top and bottom
mg.set_closed_boundaries_at_grid_edges(right_is_closed=True, top_is_closed=False, \
                                       left_is_closed=True, bottom_is_closed=False)

#setup
lin_diffuse = LinearDiffuser(mg, linear_diffusivity=0.2)

pl.figure(1)
im = imshow_grid(mg, 'topographic__elevation', grid_units = ['m','m'],
                 var_name='Elevation (m)')

#%% Run simple uplift model with linear diffusion
#units are in m and y
total_t = 200000. #200ky
dt = 1000. #1ky time steps
uplift_rate = 0.001
nt = int(total_t // dt)
for i in range(nt):
    lin_diffuse.run_one_step(dt)
    z[mg.core_nodes] += uplift_rate * dt  # add the uplift
    # add some output to let us see we aren't hanging:
    if i % 50 == 0:
        print(i*dt)

# Create a figure and plot the elevations
pl.figure(2)
im = imshow_grid(mg, 'topographic__elevation', grid_units = ['m','m'],
                 var_name='Elevation (m)')

#Plot profile
pl.figure(3)
elev_rast = mg.node_vector_to_raster(z)
ycoord_rast = mg.node_vector_to_raster(mg.node_y)
ncols = mg.number_of_node_columns
im = pl.plot(ycoord_rast[:, int(ncols // 2)], elev_rast[:, int(ncols // 2)])
pl.xlabel('horizontal distance (m)')
pl.ylabel('vertical distance (m)')
pl.title('topographic__elevation cross section')

#%% repeat with changes boundary conditions: open all edges and noise added
mg = RasterModelGrid((80, 80), 5.)
z = mg.add_zeros('node', 'topographic__elevation')
#add some noise
initial_roughness = np.random.rand(z.size)*10.
z += initial_roughness

pl.figure(4)
im = imshow_grid(mg, 'topographic__elevation', grid_units = ['m','m'],
                 var_name='Elevation (m)')

mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)
#run same model
lin_diffuse = LinearDiffuser(mg, linear_diffusivity=0.1)
total_t = 200000. #200ky
dt = 1000. #1ky time steps
uplift_rate = 0.0001
nt = int(total_t // dt)
for i in range(nt):
    lin_diffuse.run_one_step(dt)
    z[mg.core_nodes] += uplift_rate * dt  # add the uplift
    if i % 50 == 0:
        print(i*dt)

pl.figure(5)
im = imshow_grid(mg, 'topographic__elevation', grid_units = ['m','m'],
                 var_name='Elevation (m)')

# #%% repeat and plot cross profile for some timesteps
# # Careful, this is slow!

# mg = RasterModelGrid((80, 80), 1.)
# z = mg.add_zeros('node', 'topographic__elevation')
# #add some noise
# initial_roughness = np.random.rand(z.size)*10.
# z += initial_roughness
# mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
#                                        left_is_closed=False, bottom_is_closed=False)
# #run same model
# lin_diffuse = LinearDiffuser(mg, linear_diffusivity=0.2)
# total_t = 200000. #200ky
# dt = 1000. #1ky time steps
# uplift_rate = 0.001
# nt = int(total_t // dt)
# pl.figure(6)
# for i in range(nt):
#     lin_diffuse.run_one_step(dt)
#     z[mg.core_nodes] += uplift_rate * dt  # add the uplift
#     if i % 20 == 0:
#         print(i*dt)
#         elev_rast = mg.node_vector_to_raster(z)
#         ycoord_rast = mg.node_vector_to_raster(mg.node_y)
#         ncols = mg.number_of_node_columns
#         im = pl.plot(ycoord_rast[:, int(ncols // 2)], elev_rast[:, int(ncols // 2)], label=i)

# pl.xlabel('horizontal distance (m)')
# pl.ylabel('vertical distance (m)')
# pl.title('topographic__elevation cross section')
# pl.legend()

# #figure
# #im = imshow_grid(mg, 'topographic__elevation', grid_units = ['m','m'],
# #                 var_name='Elevation (m)')

