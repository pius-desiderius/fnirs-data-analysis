from matplotlib.colors import LinearSegmentedColormap

fnirs_colors = dict(
    hbo='#C91111',
    hbt= '#5B324B',
    hbr='#004E7C',
  )

legend_params_dict = dict(
                            loc='center', 
                            fontsize=11,       
                            borderpad=1.5, 
                            labelspacing=1.5,
                            markerscale=10, 
                            framealpha=0
)

curves_subplot_params = dict(
 top=0.92,
 bottom=0.11,
 left=0.065,
 right=0.945,
 hspace=0.2,
 wspace=0.35
)

two_topomaps_subplot_params = dict(top=0.89,
bottom=0.21,
left=0.115,
right=0.98,
hspace=0.175,
wspace=0.0)

one_topomap_subplot_params = dict(top=0.92,
bottom=0.075,
left=0.105,
right=0.98,
hspace=0.105,
wspace=0.0)


mask_params = dict(marker='o', 
                   markerfacecolor='black', 
                   markeredgecolor='white',
                   linewidth=0, 
                   markersize=6
                   )

color_list = [(0, fnirs_colors['hbr']), (0.5, '#FFFFE4'), (1, fnirs_colors['hbo'])]
custom_cmap = LinearSegmentedColormap.from_list('Custom_cmap', color_list, )
