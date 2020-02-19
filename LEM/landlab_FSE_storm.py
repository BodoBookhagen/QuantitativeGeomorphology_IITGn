#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 18:45:51 2020

@author: Bodo Bookhagen
"""

from landlab.components import LinearDiffuser
from landlab.plot import imshow_grid
from landlab import RasterModelGrid
import matplotlib.pyplot as plt
import numpy as np
from landlab.components import FlowAccumulator, FastscapeEroder, FlowDirectorSteepest, SteepnessFinder, ChiFinder
from landlab import load_params
#from landlab.plot import channel_profile as prf
from landlab.components.uniform_precip import PrecipitationDistribution
from landlab.components import FlowAccumulator
from landlab.plot import drainage_plot

#%% Fluvial erosion using Fastscape.
#create input file with the following parameters (e.g.: landlab_parameters1.txt)
#(do not include the three ')
'''

nrows:
100
ncols:
100
dx:
0.02
dt:
0.5
total_time:
100.
uplift_rate:
0.001
K_sp:
0.3
m_sp:
0.5
n_sp:
1.
rock_density:
2.7
sed_density:
2.7
linear_diffusivity:
0.0001

'''
#%% load and setup parameters:
#LENGTH UNITS ARE NOW KM!!!
input_file = './landlab_parameters1.txt'
inputs = load_params(input_file) # load the data into a dictionary

nrows = inputs['nrows']
ncols = inputs['ncols']
dx = inputs['dx']
uplift_rate = inputs['uplift_rate']
total_t = inputs['total_time']
dt = inputs['dt']

nt = int(total_t // dt) #this is how many loops we'll need
uplift_per_step = uplift_rate * dt

# illustrate what the MPD looks like:
print(inputs)

#Initiate model domain
mg = RasterModelGrid((nrows, ncols), dx)
z = mg.add_zeros('node', 'topographic__elevation')
# add some roughness, as this lets "natural" channel planforms arise
initial_roughness = np.random.rand(z.size)/100000.
z += initial_roughness
mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)

#Initiate model routines
fr = FlowAccumulator(mg, flow_director='D8')
sp = FastscapeEroder(mg, **inputs)
lin_diffuse = LinearDiffuser(mg, **inputs)

#run fastscape eroder (no diffusion)
for i in range(nt):
    # lin_diffuse.run_one_step(dt) no diffusion this time
    fr.run_one_step() # route_flow isn't time sensitive, so it doesn't take dt as input
    sp.run_one_step(dt)
    mg.at_node['topographic__elevation'][mg.core_nodes] += uplift_per_step # add the uplift
    if i % 20 == 0:
        print ('Completed loop %d' % i)
        
figure('topo without diffusion')
imshow_grid(mg, 'topographic__elevation', grid_units=['km','km'], var_name='Elevation (km)')
   
figure('slope-area plot for non-diffusive landscape')
loglog(mg.at_node['drainage_area'], mg.at_node['topographic__steepest_slope'],'.')
xlabel('Drainage area (km**2)')
ylabel('Local slope')
title('Slope-Area plot for whole landscape')
     
#%% rerun, this time with linear diffusion (hillslope)

#Initiate model routines
input_file = './landlab_parameters1.txt'
inputs = load_params(input_file) # load the data into a dictionary
nrows = inputs['nrows']
ncols = inputs['ncols']
dx = inputs['dx']
uplift_rate = inputs['uplift_rate']
total_t = inputs['total_time']
dt = inputs['dt']

nt = int(total_t // dt) #this is how many loops we'll need
uplift_per_step = uplift_rate * dt

mg = RasterModelGrid((nrows, ncols), dx)
z = mg.add_zeros('node', 'topographic__elevation')
initial_roughness = np.random.rand(z.size)/100000.
z += initial_roughness
mg.set_closed_boundaries_at_grid_edges(right_is_closed=False, top_is_closed=False, \
                                       left_is_closed=False, bottom_is_closed=False)

fr = FlowAccumulator(mg, flow_director='D8')
sp = FastscapeEroder(mg, **inputs)
lin_diffuse = LinearDiffuser(mg, **inputs)
figure('initial topography')
imshow_grid(mg, 'topographic__elevation', grid_units=['km','km'], var_name='Elevation (km)')
#%%
for i in range(nt):
    lin_diffuse.run_one_step(dt)
    fr.run_one_step() # route_flow isn't time sensitive, so it doesn't take dt as input
    sp.run_one_step(dt)
    mg.at_node['topographic__elevation'][mg.core_nodes] += uplift_per_step # add the uplift
    if i % 20 == 0:
        print ('Completed loop %d' % i)
        
figure('topo with diffusion')
imshow_grid(mg, 'topographic__elevation', grid_units=['km','km'], var_name='Elevation (km)')
#%%
figure('slope-area plot for diffusive landscape')
loglog(mg.at_node['drainage_area'], mg.at_node['topographic__steepest_slope'],'.')
xlabel('Drainage area (km**2)')
ylabel('Local slope')
title('Slope-Area plot for whole landscape')


#%% FANCY MODEL with storm parameters
#these are for the storm generator:
#create file called: landlab_parameters_storms.py
#and add:
'''
mean_storm_duration:
0.1
mean_storm_depth:
0.2
mean_interstorm_duration:
0.4
'''
#%% re-instantiate the FastscapeEroder, so we can 
input_file = './landlab_parameters1.txt'
inputs = load_params(input_file) # load the data into a dictionary
storm_inputs = load_params('./landlab_parameters_storms.txt')
precip = PrecipitationDistribution(total_t=total_t, delta_t=dt, **storm_inputs)
print(storm_inputs)
mg = RasterModelGrid((nrows, ncols), dx)
z = mg.add_zeros('node', 'topographic__elevation')
initial_roughness = np.random.rand(z.size)/100000.
z += initial_roughness
dt = 0.1
total_t = 250.
for edge in (mg.nodes_at_top_edge, mg.nodes_at_left_edge, mg.nodes_at_right_edge):
    mg.status_at_node[edge] = CLOSED_BOUNDARY
for edge in ( mg.nodes_at_bottom_edge):
    mg.status_at_node[edge] = FIXED_VALUE_BOUNDARY

fr = FlowRouter(mg, **inputs)
sp = FastscapeEroder(mg, **inputs)
lin_diffuse = LinearDiffuser(mg, **inputs)

out_interval = 10.
last_trunc = total_t # we use this to trigger taking an output plot
for (interval_duration, rainfall_rate) in precip.yield_storm_interstorm_duration_intensity():
    if rainfall_rate > 0.:
        # note diffusion also only happens when it's raining...
        fr.route_flow()
        sp.run_one_step(interval_duration)
        lin_diffuse.run_one_step(interval_duration)
    z[mg.core_nodes] += uplift_rate * interval_duration
    this_trunc = precip.elapsed_time // out_interval
    if this_trunc != last_trunc:  # time to plot a new profile!
        print ('made it to time %d' % (out_interval * this_trunc))
        last_trunc = this_trunc
        figure("long_profiles-storm_model")
        profile_IDs = prf.channel_nodes(mg, mg.at_node['topographic__steepest_slope'],
                                        mg.at_node['drainage_area'],
                                        mg.at_node['flow__receiver_node'])
        dists_upstr = prf.get_distances_upstream(
            mg, len(mg.at_node['topographic__steepest_slope']),
            profile_IDs, mg.at_node['flow__link_to_receiver_node'])
        plot(dists_upstr[0], z[profile_IDs[0]], label=out_interval * this_trunc)
    # no need to track elapsed time, as the generator will stop automatically
# make the figure look nicer:
figure("long_profiles-storm_model")
xlabel('Distance upstream (km)')
ylabel('Elevation (km)')
title('Long profiles evolving through time')
legend()

figure('topo with diffusion and storms')
imshow_grid(mg, 'topographic__elevation', grid_units=['km','km'], var_name='Elevation (km)')

figure('final slope-area plot')
loglog(mg.at_node['drainage_area'], mg.at_node['topographic__steepest_slope'],'.')
xlabel('Drainage area (km**2)')
ylabel('Local slope')
title('Slope-Area plot for whole landscape')

#%% re-instantiate the FastscapeEroder, so we can 
input_file = './landlab_parameters1.txt'
inputs = load_params(input_file) # load the data into a dictionary
storm_inputs = load_params('./landlab_parameters_storms.txt')
precip = PrecipitationDistribution(total_t=total_t, delta_t=dt, **storm_inputs)
print(storm_inputs)
mg = RasterModelGrid((nrows, ncols), dx)
z = mg.add_zeros('node', 'topographic__elevation')
initial_roughness = np.random.rand(z.size)/100000.
z += initial_roughness

input_file = './landlab_parameters1.txt'
inputs = load_params(input_file) # load the data into a dictionary
nrows = inputs['nrows']
ncols = inputs['ncols']
dx = inputs['dx']
uplift_rate = inputs['uplift_rate']
total_t = inputs['total_time']
dt = inputs['dt']

#dt = 0.1
#total_t = 250.

nt = int(total_t // dt) #this is how many loops we'll need
uplift_per_step = uplift_rate * dt

fr = FlowRouter(mg, **inputs)
sp = FastscapeEroder(mg, **inputs)
lin_diffuse = LinearDiffuser(mg, **inputs)

for i in range(nt):
    lin_diffuse.run_one_step(dt)
    fr.run_one_step() # route_flow isn't time sensitive, so it doesn't take dt as input
    sp.run_one_step(dt)
    mg.at_node['topographic__elevation'][mg.core_nodes] += uplift_per_step # add the uplift
    if i % 10 == 0:
        print ('made it to time %d' % (i))
        figure("long_profiles-no_storms")
        profile_IDs = prf.channel_nodes(mg, mg.at_node['topographic__steepest_slope'],
                                        mg.at_node['drainage_area'],
                                        mg.at_node['flow__receiver_node'])
        dists_upstr = prf.get_distances_upstream(
            mg, len(mg.at_node['topographic__steepest_slope']),
            profile_IDs, mg.at_node['flow__link_to_receiver_node'])
        plot(dists_upstr[0], z[profile_IDs[0]], label=out_interval * this_trunc)

# make the figure look nicer:
figure("long_profiles-no_storms")
xlabel('Distance upstream (km)')
ylabel('Elevation (km)')
title('Long profiles evolving through time')
legend()

figure('topo with diffusion and storms')
imshow_grid(mg, 'topographic__elevation', grid_units=['km','km'], var_name='Elevation (km)')
#
#figure('final slope-area plot')
#loglog(mg.at_node['drainage_area'], mg.at_node['topographic__steepest_slope'],'.')
#xlabel('Drainage area (km**2)')
#ylabel('Local slope')
#title('Slope-Area plot for whole landscape')

#%%fit:
a = mg.at_node['drainage_area']
g = mg.at_node['topographic__steepest_slope']

#figure the rest out yourself!
#use log binning or the following approach: https://github.com/keflavich/plfit
figure('final slope-area plot')
loglog(a,g, '.')
xlabel('Drainage area (k**2)')
ylabel('Local slope (m/m)')

#%% Steepness finder and Chi plots
fd = FlowDirectorSteepest(mg, 'topographic__elevation')
fd.run_one_step()
fa = FlowAccumulator(mg, 'topographic__elevation', flow_director='FlowDirectorSteepest')
fa.run_one_step()
sf = SteepnessFinder(mg, reference_concavity=0.45, 
                     min_drainage_area=1e3)
sf.calculate_steepnesses()
cf = ChiFinder(mg, reference_concavity=0.45, min_drainage_area=1.e3, reference_area=1., use_true_dx=False)
cf.calculate_chi()

imshow_grid(mg, 'channel__chi_index', plot_name='Channel steepness (theta = 0.45)', var_units='norm. steepness (m^0.9)', cmap='hot', limits=(0,300))

imshow_grid(mg, 'channel__chi_index', 
            plot_name='Chi finder', var_units='norm. steepness (m^0.9)', cmap='hot', limits=(0,300))

scatter(mg.x_of_node[da_outlet_idx], mg.y_of_node[da_outlet_idx], c='red', marker='x', label='outlet')
#plt.scatter(mg.x_of_node[endpoints_idx], mg.y_of_node[endpoints_idx], c='white', marker='.', label='drainage head')

ax = fig1.add_subplot(2,3,4)
imshow_grid(mg, 'channel__chi_index', plot_name='Channel Chi index (theta = 0.45)', var_units='chi ()', cmap='hot', limits=(np.floor(np.min(mg.at_node['channel__chi_index'][mg.at_node['channel__chi_index'] >0])), np.ceil(np.max(mg.at_node['channel__chi_index'][mg.at_node['channel__chi_index'] >0]))))
plt.scatter(mg.x_of_node[da_outlet_idx], mg.y_of_node[da_outlet_idx], c='red', marker='x', label='outlet')
