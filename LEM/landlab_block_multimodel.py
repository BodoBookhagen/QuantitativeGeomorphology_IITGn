#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 11:22:42 2020

@author: bodo
"""
## Import what is needed
from landlab import RasterModelGrid
from landlab.components import LinearDiffuser, FlowAccumulator
from landlab.components import FastscapeEroder, SinkFiller
from landlab.components import ChiFinder, SteepnessFinder
from landlab.plot import imshow_grid #function, not objects
from landlab.components import Profiler, ChannelProfiler
from matplotlib import pyplot as pl
import numpy as np

#%% Setup more complex modeling regime and analyse modeled streams
## Run model with a 100x100 grid (increasing to 200x200 will increase timing significantly). First step will be slower, because flow routing takes more time.
n=200
mg = RasterModelGrid((n, n), 100.0)
z = mg.add_zeros('node', 'topographic__elevation')
mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)

#Create an uplifted block
blockuplift_nodes = np.where( (mg.node_y < 17500) & (mg.node_y > 2500) &
                              (mg.node_x < 17500) & (mg.node_x > 2500) )
z[blockuplift_nodes] += 100.0
z[blockuplift_nodes] += np.random.rand(len(blockuplift_nodes[0]))*10

pl.figure()
imshow_grid(mg, 'topographic__elevation', 
            plot_name='Initial Topography of Uplifted block', 
            allow_colorbar=True)

ld = LinearDiffuser(mg, linear_diffusivity=0.01)
fr = FlowAccumulator(mg, flow_director='D8')
fse = FastscapeEroder(mg, K_sp = 5e-5, m_sp=0.5, n_sp=1.)
sf = SinkFiller(mg, routing='D8')

## instantiate helper components
chif = ChiFinder(mg)
steepnessf = SteepnessFinder(mg, reference_concavity=0.5)

## Set some variables
rock_up_rate = 1e-3 #m/yr
dt = 1000 # yr
rock_up_len = dt*rock_up_rate # m
nr_time_steps = 500
## Time loop where evolution happens
for i in range(nr_time_steps):
    z[mg.core_nodes] += rock_up_len #uplift only the core nodes
    ld.run_one_step(dt) #linear diffusion happens.
    sf.run_one_step() #sink filling happens, time step not needed
    fr.run_one_step() #flow routing happens, time step not needed
    fse.run_one_step(dt) #fluvial incision happens
    ## optional print statement
    if np.mod(i,10) == 0:
        print('i:', i)

steepnessf.calculate_steepnesses()  
chif.calculate_chi()
## to see what fields are created:
mg.at_node.keys()    

pl.figure()
imshow_grid(mg, 'topographic__elevation', 
            plot_name='Model Landscape with FSE and LD - Topography', 
            allow_colorbar=True)

pl.figure()
imshow_grid(mg, 'drainage_area', 
            plot_name='Model Landscape with FSE and LD - Drainage Area', 
            allow_colorbar=True, colorbar_label='DA', cmap='viridis')

pl.figure()
imshow_grid(mg, 'channel__steepness_index', 
            plot_name='Model Landscape with FSE and LD - Steepness Index', 
            allow_colorbar=True, colorbar_label='Steepness', cmap='magma', 
            vmin=np.percentile(mg.at_node['channel__steepness_index'][mg.at_node['channel__steepness_index'] > 0],5), 
            vmax=np.percentile(mg.at_node['channel__steepness_index'][mg.at_node['channel__steepness_index'] > 0],95) )
            
pl.figure()
imshow_grid(mg, 'channel__chi_index', 
            plot_name='Model Landscape with FSE and LD - Channel Chi Index', 
            allow_colorbar=True, colorbar_label='Chi Index', cmap='plasma', 
            vmin=np.percentile(mg.at_node['channel__chi_index'][mg.at_node['channel__chi_index'] > 0],5), 
            vmax=np.percentile(mg.at_node['channel__chi_index'][mg.at_node['channel__chi_index'] > 0],95) )


#%% Plotting profiles and log-slope-area plots

## find the location of the largest channels
profile1 = ChannelProfiler(mg, number_of_watersheds=1,
                                 minimum_channel_threshold=0,
                                 main_channel_only=True)
profile1.run_one_step()
pl.figure()
profile1.plot_profiles(field='topographic__elevation', ylabel='Elevation [m]',
                       title='Longitudinal River Profile of largest stream')

pl.figure()
profile1.plot_profiles(field='channel__steepness_index', ylabel='Channel Steepness Index (theta=0.5)',
                       title='channel__steepness_index')

pl.figure()
profile1.plot_profiles(field='channel__chi_index', ylabel='Channel Chi Index (theta=0.5)',
                       title='channel__chi_index')

area = mg.at_node['drainage_area']
slope = mg.at_node['topographic__steepest_slope']
pl.figure()
pl.loglog(area, slope, 'k+')
pl.grid()
pl.xlabel('Log Drainage Area [m^2]', fontsize=16)
pl.ylabel('Log Slope [m/m]', fontsize=16)
pl.title('Log-Area vs. Log-Slope plot for all channels')