# Santa Cruz Island Point Cloud Processing
We are relying on the classified point cloud stored in `Pozo_USGS_UTM11_NAD83_all_color_cl.laz`.

## If you have no ground classification...
You can use the SMRF to perform the ground classification the Simple Morphological Filter ([SMRF](https://pdal.io/stages/filters.smrf.html?highlight=smrf)):

```bash
pdal translate \
   Pozo_USGS_UTM11_NAD83_all_color_cl.laz \
   -o Pozo_USGS_UTM11_NAD83_all_color_cl2.laz \
   outlier smrf range \
   --filters.outlier.method="statistical" \
   --filters.outlier.mean_k=8 \
   --filters.outlier.multiplier=3.0 \
   --filters.smrf.ignore="Classification[7:7]" \
   --filters.range.limits="Classification[2:2]" \
   --writers.las.compression=true --verbose 4
```

In Windows, you will need to replace `\` by `^` to continue writing on the next line:
```
pdal translate ^
   Pozo_USGS_UTM11_NAD83_all_color_cl.laz ^
   -o Pozo_USGS_UTM11_NAD83_all_color_cl2.laz ^
   outlier smrf range ^
   --filters.outlier.method="statistical" ^
   --filters.outlier.mean_k=8 ^
   --filters.outlier.multiplier=3.0 ^
   --filters.smrf.ignore="Classification[7:7]" ^
   --filters.range.limits="Classification[2:2]" ^
   --writers.las.compression=true --verbose 4
```

## Creating a file with only ground-classified points
It generally is a nice idea to have a file that only contains the ground points (it's smaller and easier to work with):
```bash
pdal translate \
   Pozo_USGS_UTM11_NAD83_all_color_cl.laz \
   -o Pozo_USGS_UTM11_NAD83_all_color_cl2.laz \
   range \
   --filters.range.limits="Classification[2:2]"
```

## Creating a DEM and saving a GeoTIFF
Let's create a `.json` control file for [writers.gdal](https://pdal.io/stages/writers.gdal.html?highlight=writers%20gdal). We will use the IDW interpolation.

Create the file `Pozo_USGS_UTM11_NAD83_all_color_cl2_idw.json`:
```json
{
   "pipeline": [
       "Pozo_USGS_UTM11_NAD83_all_color_cl2.laz",
       {
           "filename":"Pozo_USGS_UTM11_NAD83_all_color_cl2_DEM_1m.tif",
           "gdaldriver":"GTiff",
           "output_type":"idw",
           "resolution":"1.0",
           "window_size": "10",
           "type": "writers.gdal"
       }
   ]
 }
```

Run the pipeline on the command line with:

```
pdal pipeline Pozo_USGS_UTM11_NAD83_all_color_cl2_idw.json`
```

*Compiled with:*
```bash
pandoc --listings --variable papersize=a4paper \
    -H auto_linebreak_listings.tex \
    --variable urlcolor=blue \
    -V lang=en-GB \
    -s PC_pdal_for_SCI_from_USGS_Lidar.md \
    -o PC_pdal_for_SCI_from_USGS_Lidar.pdf
```
