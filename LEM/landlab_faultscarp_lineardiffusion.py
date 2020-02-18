#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 19:00:19 2020

@author: Bodo Bookhagen
"""

import numpy as np
from matplotlib import pyplot as pl

from landlab import RasterModelGrid
from landlab.components.diffusion.diffusion import LinearDiffuser
from landlab.plot import imshow_grid
from pylab import show, figure

#%% Create simple fault scarp model with linear diffusion

#Create a raster grid with 25 rows, 40 columns, and cell spacing of 10 m
n=100
mg = RasterModelGrid((n, n), 1.0)

#Create a field of node data (an array) on the grid called topographic__elevation.
#Initially populate this array with zero values.
z = mg.add_zeros('node', 'topographic__elevation')

#Set boundary conditions
mg.set_closed_boundaries_at_grid_edges(right_is_closed=True, top_is_closed=False, \
                                       left_is_closed=True, bottom_is_closed=False)

#Check the size of the array
#len(z)

#Create a fault across the grid at the moddle of the array
fault_y = 50.0
upthrown_nodes = np.where(mg.node_y>fault_y)
#raise nodes by 10m
z[upthrown_nodes] += 10.0

#make cross section
crosssection_center_org = mg.node_vector_to_raster(z, flip_vertically=True)[:,np.int(np.round(n/2))].copy()
crosssection_center_ycoords = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))].copy()

#and plot
fg = pl.figure()
pl.plot(crosssection_center_ycoords, crosssection_center_org, 'k', \
        linewidth=3, label='Original Topography', figure=fg)
pl.grid()
pl.xlabel('Distance along profile [m]', fontsize=12)
pl.ylabel('Height [m]', fontsize=12)
pl.title('Profile across linear diffusion scarp', fontsize=16)

# View the grid
figure()
imshow_grid(mg, 'topographic__elevation', cmap='viridis', grid_units=['m','m'])
show()

#Instantiate the diffusion component:
kappa_linear_diffusivity=0.01 #in m2 per year L2/T
ld = LinearDiffuser(grid=mg, linear_diffusivity=kappa_linear_diffusivity)

#set a model timestep inyr
#(the component will subdivide this as needed to keep things stable)
dt = 100.

#Model landscape, here we do 25 time steps
for i in range(25):
        ld.run_one_step(dt)

#Plot new landscape
figure()
imshow_grid(mg, 'topographic__elevation', cmap='viridis', grid_units=['m','m'])
show()

# Plot profile across the fault
mg_ld1 = mg.node_vector_to_raster(z, flip_vertically=True)
crosssection_center_ld = mg.node_vector_to_raster(mg_ld1, flip_vertically=True)[:,np.int(np.round(n/2))]
crosssection_center_ycoords_ld = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))]
fg = pl.figure()
pl.plot(crosssection_center_ycoords, crosssection_center_org, 'k', \
        linewidth=3, label='Original Topography')
pl.grid()
pl.xlabel('Distance along profile [m]', fontsize=12)
pl.ylabel('Height [m]', fontsize=12)
pl.title('Profile across linear diffusion scarp', fontsize=16)
pl.plot(crosssection_center_ycoords_ld, crosssection_center_ld, 'b', \
        linewidth=1, label='ld after n*dt')

#%% Create tilted plan with scarp
mg['node']['topographic__elevation'] += (mg.node_y/10 + 
                                         mg.node_x/10 + np.random.rand(len(mg.node_y)) / 10)

#%% Create oblique fault scarp
#Create a raster grid with 25 rows, 40 columns, and cell spacing of 10 m
n=100
mg = RasterModelGrid((n, n), 1.0)

#Create a field of node data (an array) on the grid called elevation.
#Initially populate this array with zero values.
z = mg.add_zeros('node', 'topographic__elevation')
#Set boundary conditions
mg.set_closed_boundaries_at_grid_edges(right_is_closed=True, top_is_closed=False, \
                                       left_is_closed=True, bottom_is_closed=False)

#Check the size of the array
len(z)

#Create a diagonal fault across the grid
fault_y = 50.0 + 0.25*mg.node_x
upthrown_nodes = np.where(mg.node_y>fault_y)
z[upthrown_nodes] += 10.0 + 0.01*mg.node_x[upthrown_nodes]

# View the grid
figure()
imshow_grid(mg, 'topographic__elevation', cmap='jet', grid_units=['m','m'])
show()

#Instantiate the diffusion component:
linear_diffusivity=0.01 #in m2 per year
ld = LinearDiffuser(grid=mg, linear_diffusivity=linear_diffusivity)

#set a model timestep
#(the component will subdivide this as needed to keep things stable)
dt = 100.

#Evolve landscape
for i in range(25):
        ld.run_one_step(dt)

#Plot new landscape
figure()
imshow_grid(mg, 'topographic__elevation', cmap='jet', grid_units=['m','m'])
show()
