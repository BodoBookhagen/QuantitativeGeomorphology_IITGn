# Required and suggested software for the workshop: Quantitative Geomorphology
## **Bodo Bookhagen, 17-Feb-2020**

This document briefly describes what Software to setup for performing analysis steps and working with gridded data (DEMs) and lidar pointclouds. **Please install this software on your laptop - it will allow you to use it without a computer pool. All software is open source.**

you can use Windows and most of the software will also be easily installed on a Mac. _We suggest to use Ubuntu or some other Linux-based distribution as these are the most flexible systems, but Windows OS will work as well_.

We will rely on the following python packages and environments as well as several tools for flexible programming and data analysis:
- [Python 3.x](https://www.python.org/), [PDAL](https://pdal.io/), [GDAL](https://gdal.org/), [landlab](https://landlab.readthedocs.io/en/master/), [RichDEM](https://richdem.readthedocs.io/en/latest/), [GMT](http://gmt.soest.hawaii.edu/), [cython](https://cython.org/), [scipy](https://www.scipy.org/), [numpy](https://numpy.org/), [pandas](https://pandas.pydata.org/), [pylidar](http://www.pylidar.org/en/latest/), [laspy](https://pypi.org/project/laspy/) and several other tools

Packages only used for Point-cloud data:
- [CloudCompare](https://www.danielgm.net/cc)
  - Point Cloud analysis and visualization. Includes many useful point-cloud analysis tools, but is slower on the visualization of large pointclouds
- [Displaz](http://c42f.github.io/displaz/)
  - Very fast and versatile viewer. Can be run from python.
  - _Ubuntu Users:_ This likely will need to be compiled on your machine - follow the instructions on the github page
  - _Mac users:_ Due to the recent updates for the X11 Server, this doesn't properly compile. You may end up using CloudCompare instead (which is slower for visualization).
- [LAStools](https://rapidlasso.com/lastools/)
  - Commercial Software. However, contains several useful and very fast tools for working with Point Cloud data.


## _Windows Users:_
One option is to install this via [Anaconda](https://www.anaconda.com/) and select the packages **gdal, pdal, Pylidar, pdal, lastools, numpy, pandas and matplotlib**. **Landlab** is installed via the `conda-forge` channel.

Unfortunately, Windows users will not be able to install **richDEM**.

You can install the required packages via the `anaconda shell`:

```
conda install python=3.* pip scipy pandas numpy matplotlib scikit-image gdal ipython spyder statsmodels jupyter pyproj pip pdal xarray packaging h5py lastools pykdtree
conda install -y -c conda-forge landlab
pip install laspy
```

If you want to create a separate conda environment dedicated to the analysis of DEMs (e.g. `Py3_DEM`):
```
conda create -y -n Py3_DEM python=3.* pip scipy pandas numpy matplotlib scikit-image gdal ipython spyder statsmodels jupyter pyproj
conda activate Py3_DEM
conda install -y -c conda-forge landlab
```

## _Alternative option Windows Users:_
Install [Linux Subsystem on Windows](https://docs.microsoft.com/en-us/windows/wsl/install-win10) and use miniconda (see next section). Installing the Linux subsystem (use Ubuntu 18.04) is generally a useful thing to do for Windows users.

**This will allow you to run richDEM on Windows machine (via the Ubuntu subsystem)**

## _Ubuntu and Mac Users:_
Install [miniconda3](https://docs.conda.io/en/latest/miniconda.html) and the packages via `conda install`. Download and install the required software via the command line:
```
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh ./Miniconda3-latest-Linux-x86_64.sh
```

You may have to include additional channels for installation:
```
conda config --prepend channels conda-forge/label/dev
conda config --prepend channels conda-forge
```

## Option for Ubuntu: Setting up the a conda/anaconda environment for DEM analysis
```
conda create -y -n Py3_DEM python=3.* pip scipy pandas numpy matplotlib scikit-image gdal pdal ipython spyder statsmodels jupyter pyproj
conda activate Py3_DEM
conda install -c conda-forge richdem landlab
```
We will be using a jupyter notebook and you are now ready to run the Jupyter notebook on your computer. Use the Anaconda Prompt to navigate to the folder that contains the `Gaussian_Hill_DEM.ipynb` and then type:
```
jupyter notebook
```
This will open the repository in your browser. Click on the notebook: `Gaussian_Hill_DEM.ipynb`. We will be working with this notebook during the workshop.

## Setting up the conda/anaconda requirements for working with point cloud (PC) data:
Install the conda packages (will take some time):
```
conda create -y -n Py3_PC python=3.* pip scipy pandas numpy matplotlib scikit-image gdal pdal xarray packaging ipython multiprocess h5py lastools pykdtree spyder
source activate Py3_PC
pip install laspy
```

Activate the environment `source activate PC_py3` and install laspy with `pip install laspy`

- Editor
  - We will be doing some coding and it may be useful to use an editor to take notes as well. Install your favorite editor - for example [Atom](https://atom.io/) or [Notepad++ on Windows](https://notepad-plus-plus.org/download/) or [Spyder](https://www.spyder-ide.org/). Spyder is included in the Windows Anaconda distribution and is installed via the command line above.
  - _Windows Users:_ There is no X-Windows interface in the Linux/Ubuntu subsystem and you will need to use Spyder from Windows


*Compiled with:*
```bash
pandoc --listings --variable papersize=a4paper \
    -H auto_linebreak_listings.tex \
    --variable urlcolor=blue \
    -V lang=en-GB \
    -s QGeomorph_Workshop_Required_Software.md \
    -o QGeomorph_Workshop_Required_Software.pdf
```
