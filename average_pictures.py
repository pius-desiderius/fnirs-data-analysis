import os
import numpy as np
from functions_fnirs import *


def averaged_array(arrays):
    arrays_list = []
    for i in arrays:
        arr = np.load(i)
        arrays_list.append(arr)
    array_shape = arrays_list[0].shape
    arr_concat = np.stack(arrays_list)
    averaged_array = np.mean(arr_concat, axis=0)
    return averaged_array

# times = np.arange(2, 14, 2)
# haemo_picks = 'hbo'

# if haemo_picks=='hbo':
#     topo_haemo = 'HbO'
# else:
#     topo_haemo = 'HbR'

# topomap_args = dict(extrapolate='local')

# smr_evoked = smr_epochs.average(picks=haemo_picks)
# rest_evoked = rest_epochs.average(picks=haemo_picks)

# vmin = min(smr_evoked.data.min(), rest_evoked.data.min())
# vmax = max(smr_evoked.data.max(), rest_evoked.data.max())
# vlim = (vmin*10**6, vmax*10**6)
# vlim_topo = (vmin, vmax)
# sm = plt.cm.ScalarMappable(cmap='RdBu_r', norm=matplotlib.colors.Normalize(vmin=vmin, vmax=vmax))

# fig, axes = plt.subplots(2, len(times), figsize=(14, 7))

# for idx, ax in enumerate(axes[0]):
#     mne.viz.plot_topomap( 
#                          data=smr_evoked.get_data()[:, times[idx]],
#                          pos=smr_evoked.info,
#                          axes=ax,
#                          vlim=vlim_topo,
#                          show=False
        
#     )

# for idx, ax in enumerate(axes[1]):
#     mne.viz.plot_topomap( 
#                          data=rest_evoked.get_data()[:, times[idx]],
#                          pos=rest_evoked.info,
#                          axes=ax,
#                          vlim=vlim_topo,
#                          show=False
        
#     )


# cbaxes = fig.add_axes([0.095, 0.25, 0.02, 0.5]) # setup colorbar axes. 

# cbar = plt.colorbar(mappable=sm, cax=cbaxes, pad=0.15, orientation='vertical')
# cbar.set_label(f'{topo_haemo} concentration, Δ μM\L', loc='center', size=12)

# fig.subplots_adjust( 
#                     top=0.910, 
#                     bottom=0.06,
#                     left=0.150, 
#                     right=0.950, 
#                     hspace=0.195, 
#                     wspace=0.0 
#                    )

# x_top, y_top = 0.55, 0.95
# x_bottom, y_bottom = 0.55, 0.5

# fig.text(
#          x=x_top, y=y_top, 
#          s=f'{CONDITION} {topo_haemo} changes timeline', 
#          fontsize='x-large', 
#          horizontalalignment='center', 
#          verticalalignment='center' 
#         )
# fig.text( 
#          x=x_bottom, y=y_bottom, 
#          s=f'Rest {topo_haemo} changes timeline', 
#          fontsize='x-large', 
#          horizontalalignment='center', 
#          verticalalignment='center'
#         )#we set a timeline for each epoch


if __name__ == '__main__':
    pathname = DIRS_TO_SAVE_STUFF['topo_hbo_path_np']

    files = fast_scanfiles_subjfiles(pathname, contains='MI')
    
    averaged_array(arrays=files)
    