# https://pyresample.readthedocs.io/en/latest/grid.html
# https://podaac.jpl.nasa.gov/forum/viewtopic.php?f=83&t=432
import os,sys,glob
import numpy as np
from datetime import datetime, timedelta, date
from netCDF4 import Dataset, date2num
from pyresample import image, geometry
import xarray as xr
from matplotlib import pyplot as plt
import pyresample as pr
from pyresample import load_area, create_area_def, area_def2basemap
from pyresample.utils import load_cf_area
import yaml


filestamp = datetime.strptime('20200516', '%Y%m%d')
####################
msg_area = geometry.AreaDefinition('msg_full', 'Full globe MSG1 image 41.5 degrees',
                                'msg_full',
                                {'a': '6378137.000000', 'b': '6356752.300000',
                                 'h': '35785863.000000', 'lon_0': '41.500000',
                                 'proj': 'geos'},
                                3712, 3712,
                                [-5570248.477339261, -5567248.074173444,
                                 5567248.074173444, 5570248.477339261])
area_def = create_area_def('my_area',
                            {'proj': 'latlong', 'lon_0': 0},
                            area_extent=[-180, -90, 180, 90],
                            resolution=0.1,
                            units='degrees',
                            description='Global 1x1 degree lat-lon grid')

#area_def = load_area('/home/NCMRWFTEMP/vsprasad/EXP_HY2B/validation/crr/areas.yaml', 'IndianOcean_latlon_SC300')
##########
########## Basemap
#area_def = pr.utils.load_area('areas.cfg', 'pc_world')
#####bmap = pr.plot.area_def2basemap(area_def)
###################
#area_def, cf_info = load_cf_area('/home/NCMRWFTEMP/vsprasad/EXP_HY2B/validation/crr/xxx.nc')
#x = xr.open_dataset('/home/NCMRWFTEMP/vsprasad/EXP_HY2B/validation/crr/xxx.nc')
#llon = x.lon.values
#llat = x.lat.values
#xgrid = x.lat.values.shape[0]
#ygrid = x.lon.values.shape[0]
area_def, cf_info = load_cf_area('/home/NCMRWFTEMP/vsprasad/EXP_HY2B/validation/diagStat/prodAOH/prodAOHdiagstat2020040200-scat.nc')
x = xr.open_dataset('/home/NCMRWFTEMP/vsprasad/EXP_HY2B/validation/diagStat/prodAOH/prodAOHdiagstat2020040200-scat.nc')
llon = x.longitude.values
llat = x.latitude.values
ygrid = x.latitude.values.shape[0]
xgrid = x.longitude.values.shape[0]
s = xr.open_dataset('/home/NCMRWFTEMP/vsprasad/EXP_HY2B/validation/crr/S_NWC_CRR_MSG1_global-VISIR_20200517T070000Z.nc')
data = s.crr.data
lats = s.lat.values
lons = s.lon.values
###############
swath_def = geometry.SwathDefinition(lons=lons, lats=lats)
swath_con = image.ImageContainerNearest(data, swath_def, radius_of_influence=5000)
area_con = swath_con.resample(area_def)
result = area_con.image_data
variable = 'crr'
######## Create Netcdf
mydata = Dataset('sate.nc', 'w', format='NETCDF3_CLASSIC')
mydata.description = 'CF netcdf regridding '
mydata.history = 'M. Sateesh; NCMRWF; Noida.'

# dimensions
mydata.createDimension("time",1)
mydata.createDimension('longitude', xgrid)
mydata.createDimension('latitude', ygrid)
lat = mydata.createVariable('latitude', 'f8',('latitude',))
lat.long_name = "latitude"
lat.units = "degrees_north"
lat.standard_name = "latitude"
lon = mydata.createVariable('longitude', 'f8',('longitude',))
lon.long_name = "longitude"
lon.units = "degrees_east"
lon.standard_name = "longitude"
times = mydata.createVariable("time","f8",("time",))
times.long_name="time"
#times.units = "hours since " + filestamp.strftime("%Y-%m-%d %H:%M:%S")
times.units = "hours since 0001-01-01 00:00:00.0"
times.calendar = "gregorian"
times.axis = 'T'
### Create Variable

PRODUCT = mydata.createVariable(variable, 'f8', ('time','latitude','longitude',))
PRODUCT.long_name= s.crr.attrs['long_name']
PRODUCT.units= s.crr.attrs['units']
## SATEESH for 30 minute file contains 2 X 15 ##
#var = var * 2
PRODUCT[:,:] = result[:,:]
#cma = mydata.createVariabLe('cma', 'f8', ('time','latitude','longitude',))
#cma.units = 'm/s'
#cma[:,:] = var[:,:].data
xii = llon
yii = llat
lon[:] = xii[:]
lat[:] = yii[:]
times[:] = date2num(filestamp,units=times.units,calendar=times.calendar)
mydata.close()
