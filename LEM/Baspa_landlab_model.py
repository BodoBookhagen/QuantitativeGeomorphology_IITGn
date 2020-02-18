#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 17:34:25 2017

@author: bodo
Install Landlab with conda:
    conda create -n landlab spyder ipython gdal landlab -c landlab
    source activate landlab
"""
#%% Prepare Baspa Model with:
gdalwarp -ot Int16 -r bilinear -tr 500 500 -tap Baspa_SRTM1_30m_UTM44N_WGS84.tif Baspa_SRTM1_500m_UTM44N_WGS84.tif
gdal_translate -of AAIGrid Baspa_SRTM1_500m_UTM44N_WGS84.tif Baspa_SRTM1_500m_UTM44N_WGS84.asc

#%%Setting up Baspa model with 500-m DEM resolution
from landlab.io import read_esri_ascii
from landlab.components import LinearDiffuser
from landlab.plot import imshow_grid
from landlab import RasterModelGrid
from matplotlib.pyplot import figure, show, plot, xlabel, ylabel, title, loglog, legend, scatter, grid
import matplotlib.pyplot as plt
import numpy as np
from landlab.components import FlowRouter, FastscapeEroder, FlowDirectorSteepest, SteepnessFinder, ChiFinder
from landlab import load_params
from landlab.plot import channel_profile as prf
from landlab.components.uniform_precip import PrecipitationDistribution
from landlab.components import FlowAccumulator
from landlab.plot import drainage_plot, channel_profile
import landlab

#%% Import data
(mg, z) = read_esri_ascii('Baspa_SRTM1_500m_UTM44N_WGS84.asc', name='topographic__elevation')
#verify if borders of DEM looks ok:
ncols = 141
nrows = 101
plt.imshow(z.reshape(nrows, ncols))
#slice out the first row and last column, because they are zero
z = z.reshape(nrows,ncols)[1::, 0:-1].ravel()
nrows = 101 - 1
ncols = 141 - 1
#verify by looking at DEM with matplotlib
#plt.imshow(z.reshape(nrows, ncols))
cellsize = 500

mg = landlab.RasterModelGrid((nrows,ncols), spacing=(cellsize))
mg.at_node['topographic__elevation'] = z

#for edge in (mg.nodes_at_left_edge, mg.nodes_at_right_edge):
#    mg.status_at_node[edge] = CLOSED_BOUNDARY
for edge in (mg.nodes_at_top_edge, mg.nodes_at_bottom_edge, mg.nodes_at_left_edge, mg.nodes_at_right_edge):
    mg.status_at_node[edge] = FIXED_VALUE_BOUNDARY

figure(1)
im = imshow_grid(mg, 'topographic__elevation', grid_units = ['m','m'], var_name='Elevation (m)')

#%% model Setup
(mg, z) = read_esri_ascii('Baspa_SRTM1_500m_UTM44N_WGS84.asc', name='topographic__elevation')
ncols = 141
nrows = 101
z = z.reshape(nrows,ncols)[1::, 0:-1].ravel()
nrows = 101 - 1
ncols = 141 - 1
cellsize = 500
mg = landlab.RasterModelGrid((nrows,ncols), spacing=(cellsize))
mg.at_node['topographic__elevation'] = z
for edge in (mg.nodes_at_top_edge, mg.nodes_at_bottom_edge, mg.nodes_at_left_edge, mg.nodes_at_right_edge):
    mg.status_at_node[edge] = FIXED_VALUE_BOUNDARY

input_file = './landlab_Baspa_parameters1.txt'
inputs = load_params(input_file) # load the data into a dictionary
#or directly import from string

uplift_rate = inputs['uplift_rate']
total_t = inputs['total_time']
dt = inputs['dt']
figure('Baspa: topo before modeling')
im = imshow_grid(mg, 'topographic__elevation', grid_units = ['m','m'], var_name='Elevation (m)')

nt = int(total_t // dt) #this is how many loops we'll need
uplift_per_step = uplift_rate * dt

fr = FlowRouter(mg, **inputs)
sp = FastscapeEroder(mg, **inputs)
lin_diffuse = LinearDiffuser(mg, **inputs)

for i in range(nt):
    lin_diffuse.run_one_step(dt)
    fr.run_one_step() # route_flow isn't time sensitive, so it doesn't take dt as input
    #sp.run_one_step(dt)
    mg.at_node['topographic__elevation'][mg.core_nodes] += uplift_per_step # add the uplift
    if i % 10 == 0:
        print ('made it to time %d' % (i*dt))
        figure("long_profiles-Baspa")
        profile_IDs = prf.channel_nodes(mg, mg.at_node['topographic__steepest_slope'],
                                        mg.at_node['drainage_area'],
                                        mg.at_node['flow__receiver_node'])
        dists_upstr = prf.get_distances_upstream(
            mg, len(mg.at_node['topographic__steepest_slope']),
            profile_IDs, mg.at_node['flow__link_to_receiver_node'])
        plot(dists_upstr[0], z[profile_IDs[0]], label=i*dt)

figure("long_profiles-Baspa")
xlabel('Distance upstream (m)')
ylabel('Elevation (m)')
title('Long profiles evolving through time')
grid
legend()

figure('Baspa: topo after modeling')
imshow_grid(mg, 'topographic__elevation', grid_units=['m','m'], var_name='Elevation (m)')

