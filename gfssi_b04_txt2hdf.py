import os
import sys
import numpy as np
import h5py


ii = (lats - rminlat) / res
jj = (lons - rminlon) / res

values[ii, jj] = data