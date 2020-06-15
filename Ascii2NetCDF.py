### http://chris35wills.github.io/gridding_data/
### https://stackoverflow.com/questions/44191373/ascii-to-netcdf-conversion
import numpy as np
import pandas as pd
from netCDF4 import Dataset, date2num
from datetime import datetime, timedelta, date
### Ascii read
hdstr1='YEAR MNTH DAYS HOUR MINU CLAT CLON SAID WD10 WS10 SWVQ NWVA ISWV SPRR'
s = pd.read_csv('ncep_2020060906_oscatw-bufrDump.csv',delimiter=',',header=None)
s.columns = hdstr1.split()
### gridding with weight
ws, yi, xi = np.histogram2d(s['CLAT'], s['CLON'], bins=(720,1440), weights=s['WS10'], normed=False)
wd, yi, xi = np.histogram2d(s['CLAT'], s['CLON'], bins=(720,1440), weights=s['WD10'], normed=False)
### gridding with count
count, y, x = np.histogram2d(s['CLAT'], s['CLON'], bins=(720,1440))
### filtering of multiple values in single grid
## count = count[count <=1] ## Maybe implimented
ws = ws / count
ws = np.ma.masked_invalid(ws)
wd = wd / count
wd = np.ma.masked_invalid(wd)

### NetCDF
mydata = Dataset('HY2Bascci2nc.nc', 'w', format='NETCDF3_CLASSIC')
mydata.description = 'ncep bufr_d ascii data to netcdf'
mydata.history = 'M. Sateesh; NCMRWF; Noida.'

# dimensions
mydata.createDimension("time",1)
mydata.createDimension('longitude', 1440)
mydata.createDimension('latitude', 720)
lat = mydata.createVariable('latitude', 'f8',('latitude',))
lat.long_name = "latitude"
lat.units = "degrees_north"
lat.standard_name = "latitude"
lon = mydata.createVariable('longitude', 'f8',('longitude',))
lon.long_name = "longitude"
lon.units = "degrees_east"
lon.standard_name = "longitude"
times = mydata.createVariable("time","f8",("time",))
times.units = "hours since 0001-01-01 00:00:00.0"
times.calendar = "gregorian"
### Create Variable
ws10 = mydata.createVariable('ws10', 'f8', ('time','latitude','longitude',))
ws10.units = 'm/s'
wd10 = mydata.createVariable('wd10', 'f8', ('time','latitude','longitude',))
wd10.units = 'degree'

ws10[:,:] = ws[:,:].data
wd10[:,:] = wd[:,:].data
xii = xi[0:-1]
yii = yi[0:-1]
lon[:] = xii[:]
lat[:] = yii[:]
#dates = [datetime(2020,3,1,0,0)+n*timedelta(hours=12) for n in range(ws10.shape[0])]
times[:] = date2num(datetime(2020,6,15,0,15),units=times.units,calendar=times.calendar)
mydata.close()
