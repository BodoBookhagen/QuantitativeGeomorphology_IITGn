#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 11:52:01 2020

@author: Bodo Bookhagen
"""
from landlab.components import FlowAccumulator, FastscapeEroder
from landlab import RasterModelGrid
import numpy as np
from matplotlib import pyplot as pl
from landlab.plot import imshow_grid

#%% Setup initial topography
x = np.arange(0,100,1)
y = (-1)*np.power(x-50, 2.)
y = y - np.min(y)
y = y / np.max(y)
y = y *200

y_array = np.empty((100,100))
y_array = np.reshape(np.repeat(y,100), (100, 100) )

pl.clf()
pl.imshow(y_array)
pl.colorbar()

#%% FSE of a 100x100 pixel domain with 10m grid cells
n=100
node_spacing = 10
mg = RasterModelGrid((n, n), node_spacing)
z = mg.add_field('node', 'topographic__elevation', y_array, 
                 units='meters', copy=True, clobber=False)
z += np.random.rand(len(z))*5
mg.set_closed_boundaries_at_grid_edges(right_is_closed=True, top_is_closed=False, \
                                       left_is_closed=True, bottom_is_closed=False)

fg1 = pl.figure(1)
imshow_grid(mg, 'topographic__elevation', plot_name='Initional Topography', 
            allow_colorbar=True)


# #Setup varying uplift rate
x_uplift = np.arange(0,100,1)
y_uplift = (-1)*np.power(x_uplift-50, 2.)
y_uplift = y_uplift - np.min(y_uplift)
y_uplift = y_uplift / np.max(y_uplift)
y_uplift = y_uplift / 1000
y_uplift2d = np.empty((100,100))
y_uplift2d = np.reshape(np.repeat(y_uplift,100), (100, 100) )
pl.figure()
pl.imshow(y_uplift2d)
pl.colorbar()

fr = FlowAccumulator(mg, flow_director='D8')
fse = FastscapeEroder(mg, K_sp = 1e-5, m_sp=0.5, n_sp=1.)
dt = 10000.
time_steps = 50
for i in range(time_steps):
    z += np.reshape(y_uplift2d, n*n) * dt #uplift the block nodes
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

