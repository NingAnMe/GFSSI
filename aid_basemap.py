#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/8/5
@Author  : AnNing
"""
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

figsize = (2.748, 2.748)
dpi = 1000

fig = plt.figure(figsize=figsize, dpi=dpi)

m = Basemap(projection='ortho',
            lat_0=0, lon_0=104.5)

m.drawlsmask(land_color="#808080",
             ocean_color="#808080",
             resolution='l')

m.drawcoastlines(linewidth=0.2)
m.drawcountries(linewidth=0.2)

m.drawparallels(range(-90, 90, 10), linewidth=0.2)
m.drawmeridians(range(-180, 180, 10), linewidth=0.2)

plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
plt.margins(0, 0)
fig.patch.set_alpha(0)
plt.savefig('ditu.png', transparent=True)
