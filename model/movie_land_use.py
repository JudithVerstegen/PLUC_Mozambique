"""Make an MP4 file of the output of the LUC model of Mozambique
Judith Verstegen, 2017-07-04

"""

from matplotlib import animation
from matplotlib import colors as cls
from matplotlib import pyplot as plt
import numpy as np
import os
from pcraster import *
import Parameters

##############
### inputs ###
##############

timesteps = Parameters.getNrTimesteps()
init_year = 2005
fn = 'landUse'
list_all_colors = {0:'White', 1:'Red', 2:'Yellow', 3:'Lime', \
                   4:'Cyan', 6:'Blue', 7:'Fuchsia', \
                   8:'Gainsboro', 9:'Green', 10:'Orange', \
                   98:'Purple', 99:'MidnightBlue'}
list_all_names = {1:'cropland', 2:'cropland with \ngrassland', \
                  3:'cropland with \npasture', 4:'forest', \
                   6:'grassland', 7:'pasture', \
                   8:'shrubland', 9:'preserved', 10:'urban',
                  98: 'deforested', 99: 'abandoned'}
legend_loc = (1.01,0.25)# Moz right bottom

############
### MAIN ###
############

# open the raster and read out the data in a numpy array
wd = os.getcwd()
if (8 - len(fn)) > 0: nr_zeros = 8 - len(fn)
else:  nr_zeros = 0
in_fn = os.path.join(wd, '1', fn + nr_zeros * '0' + '.001')
setclone(in_fn)
amap = readmap(in_fn)
data = pcr2numpy(amap, 0)

# create custom color map
colorlist = []
for i in range(0, np.max(np.array(list_all_names.keys())) + 1):
    if i in list_all_colors:
        colorlist.append(list_all_colors.get(i))     
    else:
        colorlist.append('None')

# create the figure
f, axarr = plt.subplots(1)
plt.axis('off')
# making color map
# and normalization scheme
cmap_long = cls.ListedColormap(colorlist, name='long')
norm_without_mv = cls.Normalize(vmin=0, \
                    vmax=np.max(np.array(list_all_names.keys())))
# create the legend
p = []
s = []
# loop over reversed list for ascending order
for nr in list_all_names.keys():#[::-1]:
  p.append(plt.Circle((0, 0), radius=3, lw=0, fc=list_all_colors[nr]))
  s.append(list_all_names[nr])
leg = axarr.legend(p, s, loc='right', bbox_to_anchor=legend_loc,\
          prop={'size':9}, ncol=1, fancybox=True, borderpad=0.2)
title = axarr.text(0.05, 1, '', transform=axarr.transAxes)
year = axarr.text(0.05, 0.95, '', transform=axarr.transAxes)

# use imshow to plot the raster over time
# in two functions for the animation
def init():
    im = axarr.imshow(data, norm=norm_without_mv, zorder=0,\
                            cmap=cmap_long, animated=True)
    return im, leg, year, title

def animate(i):
    t = i + 1
    if t < 10:
        fn = in_fn[:-3] + '00' + str(t)
    else:
        fn = in_fn[:-3] + '0' + str(t)
    ##print fn
    amap = readmap(fn)
    data = pcr2numpy(amap, 0)
    im = axarr.imshow(data, norm=norm_without_mv, zorder=0,\
                            cmap=cmap_long, animated=True)
    year.set_text('year = ' + str(init_year + t - 1))
    title.set_text('land use for Monte Carlo sample 1')
    return im, leg, year, title

im_ani = animation.FuncAnimation(f, animate, interval=300, \
                                   blit=True, frames = timesteps,\
                                   init_func=init)
im_ani.save('movie_' + fn + '.mp4', dpi=300, metadata={'artist':'Judith Verstegen'})
#plt.show()
