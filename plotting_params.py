from matplotlib.colors import LinearSegmentedColormap

fnirs_colors = dict(
    hbo='#C91111',
    hbt= '#5B324B',
    hbr='#004E7C',
  )

def rgb(hex_color, alpha):
    """Converts a hex color code to RGBA format with specified alpha value."""
    # Remove '#' from hex color code and convert to integer
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # Convert RGB to RGBA format with specified alpha value
    rgba = (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha)
    return rgba
  
alpha = 0.5
transparent_blue, blue = rgb(fnirs_colors['hbr'], alpha), rgb(fnirs_colors['hbr'], 0.95)
transparent_red, red = rgb(fnirs_colors['hbo'], alpha), rgb(fnirs_colors['hbo'], 0.95)

legend_params_dict = dict(
                            loc='center', 
                            fontsize=13,       
                            borderpad=1.0, 
                            labelspacing=1.5,
                            markerscale=12, 
                            framealpha=.75
)

curves_subplot_params = dict(
 top=0.92,
 bottom=0.11,
 left=0.065,
 right=0.965,
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
