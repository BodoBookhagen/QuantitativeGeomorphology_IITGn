#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 15:14:44 2020

@author: Bodo Bookhagen
"""
from landlab import RasterModelGrid
import numpy as np
from matplotlib import pyplot as pl
from landlab.plot import imshow_grid

#%% Setting up Gaussian Hill elevation data
n=111
dem_width = 5 * 100
node_spacing = dem_width/n
def gaussian_hill_elevation(n, b = 2.5):
    x, y = np.meshgrid(np.linspace(-b,b,n),
                       np.linspace(-b,b,n))
    z = np.exp(-x*x-y*y)
    return (x, y, z)

x,y,z = gaussian_hill_elevation(n)
z = z*100

mg = RasterModelGrid((n, n), node_spacing)
gh_org = mg.add_field('node', 'topographic__elevation', z, 
                      units='meters', copy=True, clobber=False)

fg1 = pl.figure(1)
imshow_grid(mg, 'topographic__elevation', plot_name='Gaissian Hill', 
            allow_colorbar=True)

fg2, ax = pl.subplots(2, 2)
crosssection_center = mg.node_vector_to_raster(gh_org, flip_vertically=True)[:,np.int(np.round(n/2))].copy()
crosssection_center_ycoords = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))].copy()
ax[0,0].plot(crosssection_center_ycoords, crosssection_center, 'k', linewidth=3, label='Org. Gaussian Hill')
ax[0,0].grid()
ax[0,0].set_xlabel('Distance along profile [m]', fontsize=12)
ax[0,0].set_ylabel('Height [m]', fontsize=12)
ax[0,0].set_title('Profile through center of Gaussian Hill at t=0', fontsize=16)

#%% Performing linear diffusion modeling

#apply linear diffusion modeling, see https://landlab.readthedocs.io/en/master/reference/components/diffusion.html
from landlab.components import LinearDiffuser
mg.set_closed_boundaries_at_grid_edges(True, True, True, True)
kappa_ld = 0.1 # m^2/yr [L^2/T]
ld = LinearDiffuser(mg, linear_diffusivity=kappa_ld)
dt = 1000 # time step in yr
ld.run_one_step(dt)

gh_ld1 = mg.node_vector_to_raster(gh_org, flip_vertically=True)

fg3 = pl.figure()
imshow_grid(mg, 'topographic__elevation', plot_name='Gaussian Hill after 1 and 10 time steps with dt=%d and kappa_ld=%f'%(dt, kappa_ld), 
            allow_colorbar=True)

#%%
fg4 = pl.figure()
pl.imshow( np.reshape(gh_org, (n,n)) - np.reshape(gh_ld1, (n,n)) )
pl.colorbar()

crosssection_center_d1 = mg.node_vector_to_raster(gh_ld1, flip_vertically=True)[:,np.int(np.round(n/2))]
crosssection_center_ycoords_d1 = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))]
ax[0,0].plot(crosssection_center_ycoords_d1, crosssection_center_d1, 'b', label='n=1, dt=%d x k=%02.2f'%(dt, kappa_ld))

#%% Repeat linear diffusion modeling in steps of dt=1000 for 10 times
dt = 1000 # time step in yr
for i in range(10):
    ld.run_one_step(dt)
    print('%d'%(i))

fg5 = pl.figure()
imshow_grid(mg, 'topographic__elevation', plot_name='Gaussian Hill after ten time step with dt=%d and kappa_ld=%f'%(dt, kappa_ld), 
            allow_colorbar=True)

gh_ld2 = mg.node_vector_to_raster(gh_org, flip_vertically=True)

crosssection_center_d2 = mg.node_vector_to_raster(gh_ld2, flip_vertically=True)[:,np.int(np.round(n/2))]
crosssection_center_ycoords_d2 = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))]
ax[0,0].plot(crosssection_center_ycoords_d2, crosssection_center_d2, 'r', label='n=10, dt=%d x k=%02.2f'%(dt, kappa_ld))
ax[0,0].legend()

#%% Record every profile for each of 20 linear diffusion steps (duration = 20ky)
x,y,z = gaussian_hill_elevation(n)
z = z*100

ax[0,1].plot(crosssection_center_ycoords, crosssection_center, 'k', linewidth=3, label='Org. Gaussian Hill')
ax[0,1].grid()
ax[0,1].set_xlabel('Distance along profile [m]', fontsize=12)
ax[0,1].set_ylabel('Height [m]', fontsize=12)
ax[0,1].set_title('Profiles at different timesteps through center of Gaussian Hill (Linear Diffusion)', fontsize=16)

mg = RasterModelGrid((n, n), node_spacing)
gh_org = mg.add_field('node', 'topographic__elevation', z, units='meters', copy=True, clobber=False)
kappa_ld = 0.1 # m^2/yr [L^2/T]
ld = LinearDiffuser(mg, linear_diffusivity=kappa_ld)
dt = 1000 # time step in yr
time_steps = 20 
crosssection_center_dt = np.empty((time_steps, len(crosssection_center_d1)))
crosssection_center_ycoords_dt = np.empty((time_steps, len(crosssection_center_ycoords_d1)))
colors = pl.cm.viridis(np.linspace(0,1,time_steps))
for i in range(time_steps):
    ld.run_one_step(dt)
    gh_ld = mg.node_vector_to_raster(gh_org, flip_vertically=True)
    
    crosssection_center_dt[i,:] = mg.node_vector_to_raster(gh_ld, flip_vertically=True)[:,np.int(np.round(n/2))]
    crosssection_center_ycoords_dt[i,:] = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))]
    ax[0,1].plot(crosssection_center_ycoords_dt[i,:], 
                 crosssection_center_dt[i,:], 
                 color=colors[i], label='dt=%d'%(dt))    
    print('%d'%(i))


#%% Repeat analysis, but add noise
#adding up to 10% noise to Gaussian Hill
x,y,z = gaussian_hill_elevation(n)
z = z*100
z = z + z * np.random.rand(n,n) * 0.1

mg = RasterModelGrid((n, n), node_spacing)
gh_noise = mg.add_field('node', 'topographic__elevation', z, units='meters', copy=True, clobber=False)
kappa_ld = 0.1 # m^2/yr [L^2/T]
ld = LinearDiffuser(mg, linear_diffusivity=kappa_ld)
dt = 1000 # time step in yr
time_steps = 20 

fg6 = pl.figure()
imshow_grid(mg, 'topographic__elevation', plot_name='Gaussian Hill with noise after time step with dt=%d and kappa_ld=%f'%(dt, kappa_ld), 
            allow_colorbar=True)

ghn_ld1 = mg.node_vector_to_raster(gh_noise, flip_vertically=True)

crosssection_center_noise_1 = mg.node_vector_to_raster(ghn_ld1, flip_vertically=True)[:,np.int(np.round(n/2))]
crosssection_center_ycoords_noise_1 = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))]
ax[1,0].plot(crosssection_center_ycoords, crosssection_center, 'k', linewidth=3, label='Org. Gaussian Hill')
ax[1,0].grid()
ax[1,0].set_xlabel('Distance along profile [m]', fontsize=12)
ax[1,0].set_ylabel('Height [m]', fontsize=12)
ax[1,0].set_title('Profiles at different timesteps through center of Gaussian Hill with noise (Linear Diffusion)', fontsize=16)
ax[1,0].plot(crosssection_center_ycoords_noise_1, crosssection_center_noise_1, 'r', label='noise')


crosssection_center_dt = np.empty((time_steps, len(crosssection_center_d1)))
crosssection_center_ycoords_dt = np.empty((time_steps, len(crosssection_center_ycoords_d1)))
colors = pl.cm.viridis(np.linspace(0,1,time_steps))
for i in range(time_steps):
    ld.run_one_step(dt)
    gh_ld = mg.node_vector_to_raster(gh_org, flip_vertically=True)
    
    crosssection_center_dt[i,:] = mg.node_vector_to_raster(gh_ld, flip_vertically=True)[:,np.int(np.round(n/2))]
    crosssection_center_ycoords_dt[i,:] = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))]
    ax[1,0].plot(crosssection_center_ycoords_dt[i,:], crosssection_center_dt[i,:], color=colors[i], label='dt=%d'%(dt))    
    print('%d'%(i))

#%% Add FastScape algorithm, see here: https://landlab.readthedocs.io/en/master/reference/components/stream_power.html
from landlab.components import FlowAccumulator, FastscapeEroder

x,y,z = gaussian_hill_elevation(n)
z = z*100

mg = RasterModelGrid((n, n), node_spacing)
gh_org = mg.add_field('node', 'topographic__elevation', z, units='meters', copy=True, clobber=False)

fr = FlowAccumulator(mg, flow_director='D8')
fse = FastscapeEroder(mg, K_sp = 1e-3, m_sp=0.5, n_sp=1.)
fr.run_one_step()
fse.run_one_step(dt=1000.)

fg7 = pl.figure()
imshow_grid(mg, 'topographic__elevation', plot_name='Gaussian Hill after one time step with K_sp=1e-5, m_sp=0.5, n_sp=1 (FastScape)', 
            allow_colorbar=True)

pl.figure()
pl.imshow(np.log10(np.reshape(fr.node_drainage_area, (n,n))))
cb=pl.colorbar()
cb.set_label('Log10 Flowaccumulation D8')

gh_fse = fse.grid.node_vector_to_raster(gh_org, flip_vertically=True)

crosssection_center_fse_1 = mg.node_vector_to_raster(gh_fse, flip_vertically=True)[:,np.int(np.round(n/2))]
crosssection_center_ycoords_fse_1 = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))]
ax[1,1].plot(crosssection_center_ycoords, crosssection_center, 'k', linewidth=3, label='Org. Gaussian Hill')
ax[1,1].grid()
ax[1,1].set_xlabel('Distance along profile [m]', fontsize=12)
ax[1,1].set_ylabel('Height [m]', fontsize=12)
ax[1,1].set_title('Profiles at different timesteps through center of Gaussian Hill (FastScape)', fontsize=16)
ax[1,1].plot(crosssection_center_ycoords_fse_1, crosssection_center_fse_1, 'r', label='noise')

#%% FastScape with time steps
from landlab.components import FlowAccumulator, FastscapeEroder

x,y,z = gaussian_hill_elevation(n)
z = z*100

mg = RasterModelGrid((n, n), node_spacing)
gh_org = mg.add_field('node', 'topographic__elevation', z, units='meters', copy=True, clobber=False)

fr = FlowAccumulator(mg, flow_director='D8')
fse = FastscapeEroder(mg, K_sp = 5e-4, m_sp=0.5, n_sp=1.)

fg2, ax2 = pl.subplots(1, 1)
ax2.plot(crosssection_center_ycoords, crosssection_center, 'k', linewidth=3, label='Org. Gaussian Hill')
ax2.grid()
ax2.set_xlabel('Distance along profile [m]', fontsize=12)
ax2.set_ylabel('Height [m]', fontsize=12)
ax2.set_title('Profile through center of Gaussian Hill at t=0..n', fontsize=16)

time_steps = 20
crosssection_center_dt = np.empty((time_steps, len(crosssection_center_d1)))
crosssection_center_ycoords_dt = np.empty((time_steps, len(crosssection_center_ycoords_d1)))
colors = pl.cm.magma(np.linspace(0,1,time_steps))
for i in range(time_steps):
    fr.run_one_step()
    fse.run_one_step(dt=1000.)
    gh_fse = mg.node_vector_to_raster(gh_org, flip_vertically=True)
    
    crosssection_center_dt[i,:] = mg.node_vector_to_raster(gh_fse, flip_vertically=True)[:,np.int(np.round(n/2))]
    crosssection_center_ycoords_dt[i,:] = mg.node_vector_to_raster(mg.node_y, flip_vertically=True)[:,np.int(np.round(n/2))]
    ax2.plot(crosssection_center_ycoords_dt[i,:], crosssection_center_dt[i,:], color=colors[i], label='i=%d'%(i))    
    print('%d'%(i))

