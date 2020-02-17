import numpy as np
from matplotlib import pyplot as pl

def gaussian_hill_elevation(n, b = 2.5):
    x, y = np.meshgrid(np.linspace(-b,b,n),
                       np.linspace(-b,b,n))
    z = np.exp(-x*x-y*y)
    return (x, y, z)

def gaussian_hill_slope(n, b = 2.5):
    x, y = np.meshgrid(np.linspace(-b,b,n),
                       np.linspace(-b,b,n))
    r = np.sqrt(x*x+y*y)
    return 2*r*np.exp(-r*r)

def gaussian_hill_curvature(n, b = 2.5):
    x, y = np.meshgrid(np.linspace(-b,b,n),
                       np.linspace(-b,b,n))
    r = np.sqrt(x*x+y*y)
    return (1 - 2*r*r)*2*np.exp(-r*r)

def np_slope(x, y, z):
    d = y[1,0] - y[0,0]
    dy, dx = np.gradient(z, d)
    return np.sqrt(dx*dx+dy*dy)

def np_abs_curvature(x, y, z):
    d = y[1,0] - y[0,0]
    dy, dx = np.gradient(z, d)
    dz = np.sqrt(dx*dx+dy*dy)
    dy, dx = np.gradient(dz, d)
    return np.sqrt(dx*dx+dy*dy)

#Plot Analytical Solution of Gaussian Hill Elevation, Slope, and Curvature
n = 111
fg, ax = pl.subplots(1, 3)
x, y, z = gaussian_hill_elevation(n)
im = ax[0].imshow(z, cmap = pl.cm.cividis_r)
cb = fg.colorbar(im, ax = ax[0], orientation = 'horizontal')
cb.set_label('Elevation')
im = ax[1].imshow(gaussian_hill_slope(n), cmap = pl.cm.magma_r)
cb = fg.colorbar(im, ax = ax[1], orientation = 'horizontal')
cb.set_label('Slope')
v = gaussian_hill_curvature(n)
vmax = v.max()
im = ax[2].imshow(v, cmap = pl.cm.seismic, vmin = -vmax, vmax = vmax)
cb = fg.colorbar(im, ax = ax[2], orientation = 'horizontal')
cb.set_label('Curvature')
pl.show()

# Plot 3D view using elevation as color code
from mpl_toolkits.mplot3d import Axes3D  
fig = pl.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x.ravel(), y.ravel(), z.ravel(), s=5, c=z.ravel(), cmap='viridis', marker='o')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Plot 3D view using slope as color code
from mpl_toolkits.mplot3d import Axes3D  
fig = pl.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x.ravel(), y.ravel(), z.ravel(), s=5, c=gaussian_hill_slope(n).ravel(), cmap='magma_r', marker='o')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Plot Analytical and numerical Slope analysis
fg, ax = pl.subplots(1, 3)
im = ax[0].imshow(gaussian_hill_slope(n), cmap = pl.cm.magma_r)
cb = fg.colorbar(im, ax = ax[0], orientation = 'horizontal')
cb.set_label('Slope (analytic)')

im = ax[1].imshow(np_slope(x, y, z), cmap = pl.cm.magma_r)
cb = fg.colorbar(im, ax = ax[1], orientation = 'horizontal')
cb.set_label('Slope (numeric)')

v = gaussian_hill_slope(n) - np_slope(x, y, z)
vmax = v.max()
im = ax[2].imshow(v, cmap = pl.cm.seismic, vmin = -vmax, vmax = vmax)
cb = fg.colorbar(im, ax = ax[2], orientation = 'horizontal')
cb.set_label('Absolute difference (analytic - numeric)')
pl.show()

# Plot Analytical and numerical Curvature analysis
fg, ax = pl.subplots(1, 3)
v = gaussian_hill_curvature(n)
vmax = v.max()
im = ax[0].imshow(v, cmap = pl.cm.seismic, vmin = -vmax, vmax = vmax)
cb = fg.colorbar(im, ax = ax[0], orientation = 'horizontal')
cb.set_label('Curvature (analytic)')

v = np_abs_curvature(x, y, z)
vmax = v.max()
im = ax[1].imshow(v, cmap = pl.cm.seismic, vmin = -vmax, vmax = vmax)
cb = fg.colorbar(im, ax = ax[1], orientation = 'horizontal')
cb.set_label('Curvature (numeric)')

v = np.abs(gaussian_hill_curvature(n)) - np_abs_curvature(x, y, z)
vmax = np.percentile(v, 99)
im = ax[2].imshow(v, cmap = pl.cm.seismic, vmin = -vmax, vmax = vmax)
cb = fg.colorbar(im, ax = ax[2], orientation = 'horizontal')
cb.set_label('Absolute difference (analytic - numeric)')
pl.show()

# Slope Distributions
n=11
x, y, z = gaussian_hill_elevation(n)
G_grad = gaussian_hill_slope(n)
G_numerical_grad = np_slope(x, y, z)
G_grad_p = np.percentile(G_grad.ravel(), [5,10,25,50,75,90,95])
G_numerical_grad_p = np.percentile(G_numerical_grad.ravel(), [5,10,25,50,75,90,95])
G_grad_p-G_numerical_grad_p

fg, ax = pl.subplots(1, 1)
ax.hist(G_grad.ravel(), bins=10, color='b', histtype='step', label='Gaussian H. analytical gradient')
ax.set_xlabel('Slope', fontsize=16)
ax.set_ylabel('#', fontsize=16)
ax.set_xlim((0, 1))
ax.hist(G_numerical_grad.ravel(), bins=100, color='r', histtype='step', label='Gaussian H. numerical gradient')
ax.legend()
ax.set_title('Gaussian Hill with %d x %d elements'%(n,n), fontsize=24 )

n=111
x, y, z = gaussian_hill_elevation(n)
G_grad = gaussian_hill_slope(n)
G_numerical_grad = np_slope(x, y, z)
G_grad_p = np.percentile(G_grad.ravel(), [5,10,25,50,75,90,95])
G_numerical_grad_p = np.percentile(G_numerical_grad.ravel(), [5,10,25,50,75,90,95])
G_grad_p-G_numerical_grad_p

fg, ax = pl.subplots(1, 1)
ax.hist(G_grad.ravel(), bins=100, color='b', histtype='step', label='Gaussian H. analytical gradient')
ax.set_xlabel('Slope', fontsize=16)
ax.set_ylabel('#', fontsize=16)
ax.set_xlim((0, 1))
ax.hist(G_numerical_grad.ravel(), bins=100, color='r', histtype='step', label='Gaussian H. numerical gradient')
ax.legend()
ax.set_title('Gaussian Hill with %d x %d elements'%(n,n), fontsize=24 )

n=1111
x, y, z = gaussian_hill_elevation(n)
G_grad = gaussian_hill_slope(n)
G_numerical_grad = np_slope(x, y, z)
G_grad_p = np.percentile(G_grad.ravel(), [5,10,25,50,75,90,95])
G_numerical_grad_p = np.percentile(G_numerical_grad.ravel(), [5,10,25,50,75,90,95])
G_grad_p-G_numerical_grad_p

fg, ax = pl.subplots(1, 1)
ax.hist(G_grad.ravel(), bins=1000, color='b', histtype='step', label='Gaussian H. analytical gradient')
ax.set_xlabel('Slope', fontsize=16)
ax.set_ylabel('#', fontsize=16)
ax.set_xlim((0, 1))
ax.hist(G_numerical_grad.ravel(), bins=100, color='r', histtype='step', label='Gaussian H. numerical gradient')
ax.legend()
ax.set_title('Gaussian Hill with %d x %d elements'%(n,n), fontsize=24 )

#Subsampling/Resampling
n=111
x, y, z = gaussian_hill_elevation(n)
G_grad = gaussian_hill_slope(n)
xs = x[::2, ::2]
ys = y[::2, ::2]
zs = z[::2, ::2]

# Plot 3D view using elevation as color code and subsampled data
from mpl_toolkits.mplot3d import Axes3D  
fig = pl.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x.ravel(), y.ravel(), z.ravel(), s=25, c=z.ravel(), cmap='viridis', marker='o')
ax.scatter(xs.ravel(), ys.ravel(), zs.ravel(), s=15, c='k', marker='x')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

#Interpolate to surface with higher density
#scipy.interpolate.interp2d(x, y, z, kind='linear', copy=True, bounds_error=False, fill_value=nan)[source]
from scipy.interpolate import interp2d
b=2.5
x_elementsi = np.linspace(-b,b,n)[::2]
y_elementsi = np.linspace(-b,b,n)[::2]
zsi = interp2d(x_elementsi, y_elementsi, zs, kind='linear')

x_elementsi = np.linspace(-b,b,n)
y_elementsi = np.linspace(-b,b,n)
zi = zsi(x_elementsi, y_elementsi)

fg, ax = pl.subplots(2, 2)
vmin = 0
vmax = 1
im = ax[0,0].imshow(z, cmap = pl.cm.viridis, vmin = vmin, vmax = vmax)
ax[0,0].set_title('Full-resolution Gaussian Hill', fontsize=21)
cb = fg.colorbar(im, ax = ax[0,0], orientation = 'horizontal')
cb.set_label('Elevation')

im = ax[0,1].imshow(zs, cmap = pl.cm.viridis, vmin = vmin, vmax = vmax)
ax[0,1].set_title('Subsampled Gaussian Hill', fontsize=21)
cb = fg.colorbar(im, ax = ax[0,1], orientation = 'horizontal')
cb.set_label('Elevation')

im = ax[1,0].imshow(zi, cmap = pl.cm.viridis, vmin = vmin, vmax = vmax)
ax[1,0].set_title('Resampled Gaussian Hill', fontsize=21)
cb = fg.colorbar(im, ax = ax[1,0], orientation = 'horizontal')
cb.set_label('Elevation')

dh = z-zi
im = ax[1,1].imshow(dh, cmap = pl.cm.Spectral, vmin = np.percentile(dh.ravel(),5), vmax = np.percentile(dh.ravel(),95))
ax[1,1].set_title('dH of full-resolution and resampled Gaussian Hill', fontsize=21)
cb = fg.colorbar(im, ax = ax[1,1], orientation = 'horizontal')
cb.set_label('dH')


