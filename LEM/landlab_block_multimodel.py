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
#from landlab.plot import channel_profile as prf #functions, not objects
from matplotlib import pyplot as pl
import numpy as np

#%% Setup more complex modeling regime and analyse modeled streams
## Instantiate process components
n=100
mg = RasterModelGrid((n, n), 50.0)
z = mg.add_zeros('node', 'topographic__elevation')
mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)
#Create a diagonal fault across the grid
blockuplift_nodes = np.where( (mg.node_y < 1000) & (mg.node_y > 4000) &
                              (mg.node_x < 1000) & (mg.node_x > 4000) )
z[blockuplift_nodes] += 1000.0
z[blockuplift_nodes] += np.random.rand(len(blockuplift_nodes[0]))*100

pl.figure()
imshow_grid(mg, 'topographic__elevation', 
            plot_name='Initial Topography of Uplifted block', 
            allow_colorbar=True)


ld1 = LinearDiffuser(mg, linear_diffusivity=0.01)
fr1 = FlowAccumulator(mg, method='D8')
fse1 = FastscapeEroder(mg, K_sp = 1e-5, m_sp=0.5, n_sp=1.)
sf1 = SinkFiller(mg, routing='D8')

## instantiate helper components
chif = ChiFinder(mg)
steepf = SteepnessFinder(mg)

## Set some variables
rock_up_rate = 1e-3 #m/yr
dt = 1000 # yr
rock_up_len = dt*rock_up_rate # m

## Time loop where evolution happens
for i in range(500):
    z[mg.core_nodes] += rock_up_len #uplift only the core nodes
    ld1.run_one_step(dt) #linear diffusion happens.
    sf1.run_one_step() #sink filling happens, time step not needed
    fr1.run_one_step() #flow routing happens, time step not needed
    fse1.run_one_step(dt) #fluvial incision happens
    ## optional print statement
    print('i', i)
   
## to see what fields are created:
#mg.at_node.keys()    
    
## Plotting the topography
pl.figure(1)
imshow_grid(mg, 'topographic__elevation')

## More plotting...

## find the location of the largest channels
profile_IDs = prf.channel_nodes(mg, mg.at_node['topographic__steepest_slope'],
                                 mg.at_node['drainage_area'],
                                 mg.at_node['flow__receiver_node'],
                                 number_of_channels=2)

## find the distances upstream at each node along the profile
profile_upstream_dists = prf.get_distances_upstream(mg, 
                                                    len(mg.at_node['topographic__steepest_slope']),
                                                    profile_IDs, 
                                                    mg.at_node['flow__link_to_receiver_node'])


## plot elevation vs. distance
pl.figure(2)
pl.plot(profile_upstream_dists[0], z1[profile_IDs[0]],'b-', label='chan 1')
pl.plot(profile_upstream_dists[1], z1[profile_IDs[1]],'r-', label= 'chan 2')
pl.title('elevation profiles')
pl.ylabel('elevation [m]')
pl.xlabel('distance upstream [m]')

## plot slope vs. drainage area
pl.figure(3)
pl.loglog(mg.at_node['drainage_area'][profile_IDs[0]], 
           mg.at_node['topographic__steepest_slope'][profile_IDs[0]],'b*')
pl.loglog(mg.at_node['drainage_area'][profile_IDs[1]], 
           mg.at_node['topographic__steepest_slope'][profile_IDs[1]],'r*')
pl.title('slope area data')
pl.ylabel('drainage area [m^2]')
pl.xlabel('slope [.]')

## Calculate channel steepness index
steepf.calculate_steepnesses()

## plot channel steepness index across the grid
pl.figure(4)
imshow_grid(mg, 'channel__steepness_index')
pl.title('channel steepness')

## Calculate chi index
chif.calculate_chi()

## plot chi index across the grid
pl.figure(5)
imshow_grid(mg, 'channel__chi_index')
pl.title('chi index')

## plot channel steepness vs. distnace upstream
pl.figure(6)
pl.plot(profile_upstream_dists[0], mg.at_node['channel__steepness_index'][profile_IDs[0]], 'bx',
         label='channel 1')
pl.plot(profile_upstream_dists[1], mg.at_node['channel__steepness_index'][profile_IDs[1]], 'rx',
         label='channel 1')
pl.title('steepness along channel')
pl.ylabel('steepness [m]')
pl.xlabel('distance [m]')

## plot chi vs. elevation profile
pl.figure(7)
pl.plot(mg.at_node['channel__chi_index'][profile_IDs[0]], 
         mg.at_node['topographic__elevation'][profile_IDs[0]], 'bx',
         label='channel 1')
pl.plot(mg.at_node['channel__chi_index'][profile_IDs[1]], 
         mg.at_node['topographic__elevation'][profile_IDs[1]], 'rx',
         label='channel 1')
pl.title('chi-elevation plot')
pl.ylabel('elevation [m]')
pl.xlabel('chi index [m]')