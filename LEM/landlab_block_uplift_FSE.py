#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 09:05:44 2020

@author: bodo
"""

from landlab.components import FlowAccumulator, FastscapeEroder
from landlab import RasterModelGrid
import numpy as np
from matplotlib import pyplot as pl
from landlab.plot import imshow_grid

#%% Stream Power-based FastScape erosion model for an uplifted block
n=100
mg = RasterModelGrid((n, n), 10.0)
z = mg.add_zeros('node', 'topographic__elevation')
mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)
#Create a diagonal fault across the grid
blockuplift_nodes = np.where( (mg.node_y < 850) & (mg.node_y > 150) &
                              (mg.node_x < 850) & (mg.node_x > 150) )
z[blockuplift_nodes] += 100.0
z[blockuplift_nodes] += np.random.rand(len(blockuplift_nodes[0]))*10

pl.figure()
imshow_grid(mg, 'topographic__elevation', 
            plot_name='Initial Topography of Uplifted block', 
            allow_colorbar=True, vmin=80, vmax=110)

#calculate inclined ramp with degree = 10 degree
#np.sin( np.deg2rad(10) )

# Setup Stream Power Erosion Law
fr = FlowAccumulator(mg, flow_director='D8')
fse = FastscapeEroder(mg, K_sp = 1e-3, m_sp=0.5, n_sp=1.)
fr.run_one_step()
fse.run_one_step(dt=10000.)

pl.figure()
imshow_grid(mg, 'topographic__elevation', 
            plot_name='Uplifted block eroded by Stream Power Erosion law with K_sp=1e-3, m_sp=0.5, n_sp=1 (FastScape)', 
            allow_colorbar=True, vmin=80, vmax=110)

pl.figure()
pl.imshow(np.log10(np.reshape(fr.node_drainage_area, (n,n))))
cb=pl.colorbar()
cb.set_label('Log10 Flowaccumulation D8')

#%% Iteration of several FastScape Erosion steps
dt = 1000.

#Evolve landscape and continue to uplift block at every time step
rock_uplift_rate = 0.01 #m/yr
time_steps = 100
for i in range(time_steps):
    z[blockuplift_nodes] += rock_uplift_rate * dt #uplift the block nodes
    fr.run_one_step()
    fse.run_one_step(dt)

pl.figure()
imshow_grid(mg, 'topographic__elevation', 
            plot_name='Uplifted block after ts=100 eroded by Stream Power Erosion law with K_sp=1e-5, m_sp=0.5, n_sp=1 (FastScape)', 
            allow_colorbar=True)

pl.figure()
pl.imshow(np.flipud(np.log10(np.reshape(fr.node_drainage_area, (n,n)))))
cb=pl.colorbar()
cb.set_label('Log10 Flowaccumulation D8 at final step')

#%% FSE of a 500x500 pixel domain with 50m grid cells
n=500
mg = RasterModelGrid((n, n), 50.0)
z = mg.add_zeros('node', 'topographic__elevation')
mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)
#Create a diagonal fault across the grid
blockuplift_nodes = np.where( (mg.node_y < 20000) & (mg.node_y > 5000) &
                              (mg.node_x < 20000) & (mg.node_x > 5000) )
z[blockuplift_nodes] += 1000.0
z[blockuplift_nodes] += np.random.rand(len(blockuplift_nodes[0]))*100

pl.figure()
imshow_grid(mg, 'topographic__elevation', 
            plot_name='Initial Topography of Uplifted block', 
            allow_colorbar=True)

#%% Evolve landscape and continue to uplift block at every time step
fr = FlowAccumulator(mg, flow_director='D8')
fse = FastscapeEroder(mg, K_sp = 1e-4, m_sp=0.5, n_sp=1.)
rock_uplift_rate = 0.001 #m/yr
dt = 100000.
time_steps = 50
for i in range(time_steps):
    z[blockuplift_nodes] += rock_uplift_rate * dt #uplift the block nodes
    fr.run_one_step()
    fse.run_one_step(dt)

pl.figure()
imshow_grid(mg, 'topographic__elevation', 
            plot_name='Uplifted block after ts=50,dt=100000 eroded by Stream Power Erosion law with K_sp=1e-4, m_sp=0.5, n_sp=1 (FastScape)', 
            allow_colorbar=True, vmin=np.percentile(z,10), 
            vmax=np.percentile(z,90))

pl.figure()
pl.imshow(np.flipud(np.log10(np.reshape(fr.node_drainage_area, (n,n)))))
cb=pl.colorbar()
cb.set_label('Log10 Flowaccumulation D8 at final step')

