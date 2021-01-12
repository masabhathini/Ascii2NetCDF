from __future__ import (absolute_import, division, print_function)

import numpy as np
import xarray as xr

def makeDataSet(wrfin):
      ds = xr.Dataset({'PRECIP': (("lat","lon"), wrfin.data)}, coords={"lat": wrfin.XLAT.data[:,0], "lon": wrfin.XLONG.data[0,:]})
      return ds

def makeArraytoDataSet(wrfin):
      dd = wrfin.to_dataset()
      ds = xr.Dataset({wrfin.name: (("lat","lon"), dd[wrfin.name])}, coords={"lat": wrfin.XLAT.data[:,0], "lon": wrfin.XLONG.data[0,:]})
      return ds
