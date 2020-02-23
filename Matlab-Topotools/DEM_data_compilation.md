# Downloading DEM data
**Bodo Bookhagen**

There exist several sources of DEMs, with different quality and purposes. One of the most useful DEMs at a global scale is the SRTM DEM, because it is openly available and has seen lots of quality control.

## Radar-based DEMs
### Reprocessed SRTM - NASADEM
The SRTM data have been reprocessed and merged with ICESAT data for a continuous surface model. The Geoid has been adjusted and changed (so it aligns with the TanDEM-X DEM). This reprocessing has been initiated during the MEaSUREs project. The NASADEM is described [here](https://earthdata.nasa.gov/esds/competitive-programs/measures/nasadem) with a more detailed [Guide to NASADEM](https://lpdaac.usgs.gov/documents/592/NASADEM_User_Guide_V1.pdf).

#### HydroSHEDS
SRTM DEM has been adjusted and corrected for drainage networks and is available at the [HydroSHEDS](https://www.hydrosheds.org/) site. Vector files can be downloaded as well.

### ALOS 2 Palsar
[ALOS - PALSAR]([https://www.eorc.jaxa.jp/ALOS/en/about/palsar.htm) is an L-band radar. The 12.5 m historical datasets (2006-2011) processed into a high-resolution DEM is availably at the ASF Data Facility through EarthData.

```bash
cd AP_08149_FBD_F0610_RT1
gdaldem hillshade AP_08149_FBD_F0610_RT1.dem.tif AP_08149_FBD_F0610_RT1.dem_HS.tif
#making color relief maps
echo '1000 0 0 0
1500 110 220 110
2500 240 250 160
3000 230 220 170
3500 220 220 220
4000 250 250 250' > color-relief.txt
gdaldem color-relief -of PNG AP_08149_FBD_F0610_RT1.dem.tif color-relief.txt AP_08149_FBD_F0610_RT1.dem.png
```

### TanDEM-X
Commercial data. High quality, but not available for general use.

## Stereogrammetry from optical imagery
### ASTER GDEM
[ASTER GDEM V3](https://asterweb.jpl.nasa.gov/gdem.asp) has been made publicly available in August 2019.

### HMA high resolution
For some parts of the Himalaya, the (High Mountain Asia 8-meter Digital Elevation Models)[https://nsidc.org/the-drift/data-update/high-mountain-asia-8-meter-digital-elevation-models-now-available/] with (more detailed documentation)[https://nsidc.org/data/highmountainasia].


*Compiled with:*
```bash
pandoc --listings --variable papersize=a4paper \
    --variable urlcolor=blue \
    -V lang=en-GB \
    -s DEM_data_compilation.md \
    -o DEM_data_compilation.pdf
```
