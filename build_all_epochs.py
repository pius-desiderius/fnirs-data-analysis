import os
import logging
import matplotlib
from functions_fnirs import *
from ROI import different_hb, different_roi, SMZ_LEFT_ROI_HBO
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from plotting_params import *
from meta import DIRS_TO_SAVE_STUFF
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colorbar import ColorbarBase

plt.ioff()

fnirs_colors = dict(
    hbo='#C91111',
    hbt= '#A4C210',
    hbr='#135181',
  )

TMIN  = float(-2)
TMAX = float(14.0)
BASELINE = (-1., 0.5)
SFREQ = 3
curves_hb = 'hbo'
logging.basicConfig(filename="log_runtime.txt", format="%(asctime)s %(message)s", filemode="w", level=logging.INFO)

fnirs_dir = "/mnt/diskus/fNIRS data ME_MI_TS_TI_SA"
subfolders = fast_scandir(fnirs_dir)
subfolders = sorted(subfolders[20:])
print(subfolders)

for items in DIRS_TO_SAVE_STUFF.values():
    os.makedirs(items, exist_ok=True)
for filename in subfolders:
        subj_and_cond = os.path.split(filename)[-1]
        print(subj_and_cond)
        CONDITION = subj_and_cond.split('_')[1]
        SUBJECT = subj_and_cond.split('_')[0]



        epochs, smr_epochs, rest_epochs, info_hbo_total, info_hbr_total, \
        info_left_smz, info_right_smz, bad_channels = get_epochs(filename, TMIN, TMAX, BASELINE, SFREQ)
        
        
        smr_epochs = smr_epochs.get_data()
        rest_epochs = rest_epochs.get_data()
        
        smr_epochs, rest_epochs = correct_times(smr_epochs), correct_times(rest_epochs)

        
        print(smr_epochs.shape, rest_epochs.shape)
        np.save('./smr_shit', smr_epochs)
        np.save('./rest_fuck', rest_epochs)

        
        smr_epochs, rest_epochs = epochs_transfer(smr_epochs, rest_epochs, 
                                                  time_limits=(7, 14), 
                                                  picks=SMZ_LEFT_ROI_HBO,
                                                  info=info_hbo_total)
        smr_epochs, rest_epochs = epochs_transfer(smr_epochs, rest_epochs, 
                                                  time_limits=(7, 14), 
                                                  picks=SMZ_LEFT_ROI_HBO,
                                                  info=info_hbo_total)

        
        bool_mask_smr = epochs_rejector(epochs=smr_epochs, criterion='minimum', info=info_hbo_total,
                                        ch_pick=SMZ_LEFT_ROI_HBO, lower=0.25, upper=1.0, time_limits=(7, 14))
        bool_mask_rest = epochs_rejector(epochs=rest_epochs, criterion='maximum', info=info_hbo_total,
                                         ch_pick=SMZ_LEFT_ROI_HBO, lower=0.0, upper=0.75, time_limits=(7,14))


        smr_epochs = smr_epochs[~bool_mask_smr]
        rest_epochs = rest_epochs[~bool_mask_rest]
 
        smr_epochs = smr_epochs[:, get_channel_indices(SMZ_LEFT_ROI, info_hbo_total), :]
        rest_epochs = rest_epochs[:, get_channel_indices(SMZ_LEFT_ROI, info_hbo_total), :]
        
        
        print(smr_epochs.shape, rest_epochs.shape)
        
        smr_data_averaged = smr_epochs.mean(axis=1)*1e6
        rest_data_averaged = rest_epochs.mean(axis=1)*1e6
       
       

        ### PLOT HEMODYNAMICS PER SE ###
        times = np.arange(TMIN, TMAX, 1/SFREQ)
        linewidth = 1.5
        ylims=(-12, 16)
        tmin, tmax = TMIN, TMAX
        topo_linewidth = 1
        pointsize = 20
        topo_width = topo_height = '30%'
        
        color_SMR_1, color_SMR_2 = '#FC1E38', '#7E00FC'
        color_REST_1, color_REST_2 = '#B3FC1E', '#FFC117'

        color_gradient_SMR = gradient(color_SMR_1, color_SMR_2, 17)
        color_gradient_REST = gradient(color_REST_1, color_REST_2, 17)

        cmap_SMR = LinearSegmentedColormap.from_list("cmap_SMR", color_gradient_SMR)
        cmap_REST = LinearSegmentedColormap.from_list("cmap_REST", color_gradient_REST)

                
        fig, axes = plt.subplots(1, 1, figsize=(20, 12))
        
        print(smr_data_averaged.shape)

        ### LEFT PART ###

        for i in range(smr_data_averaged.shape[0]):   
                color_smr = color_SMR_1
                aha = axes.plot(times, smr_data_averaged[i, :], color=color_smr, linewidth=2.5)
        for i in range(rest_data_averaged.shape[0]):
                color_rest = color_REST_1
                aha = axes.plot(times, rest_data_averaged[i, :], color=color_rest, linestyle='--', linewidth=2.5, )

        fill_1 = filler_between(axes, ylims)

        set_axis_properties(axes,
                                ylims=ylims, 
                                tlims=(tmin, tmax), 
                                title=f'HbO in LEFT HEMI in EACH EPOCH\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='Hb concentration, Δ μM\L',  
                                linewidth=1.5, 
                                fontsize=14, 
                                title_size=18,
                                legend_flag=False
                                )
        
        # cb_SMR_ax = fig.add_axes([0.90, 0.2, 0.015, 0.6])  # [left, bottom, width, height]
        # cb_REST_ax = fig.add_axes([0.95, 0.2, 0.015, 0.6])  # Adjust the position as needed

        # # Add colorbars
        # cb_SMR = ColorbarBase(ax=cb_SMR_ax, cmap=cmap_SMR, orientation='vertical', label='SMR')
        # cb_REST = ColorbarBase(ax=cb_REST_ax, cmap=cmap_REST, orientation='vertical', label='REST')


        ### LEGENDS PARAMS ###


        # plt.subplots_adjust(**curves_subplot_params)
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"all_epochs"]}/{SUBJECT}_{CONDITION}_all_epochs.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig) 
