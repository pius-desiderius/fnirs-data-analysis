import os
import logging
import matplotlib
from functions_fnirs import *
from ROI import different_hb, different_roi, SMZ_LEFT_ROI_HBO
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from plotting_params import *
from meta import DIRS_TO_SAVE_STUFF

plt.ioff()

fnirs_colors = dict(
    hbo='#C91111',
    hbt= '#A4C210',
    hbr='#135181',
  )

TMIN  = float(-2)
TMAX = float(14.5)
BASELINE = (-1., 0.5)
SFREQ = 2
curves_hb = 'hbo'
logging.basicConfig(filename="../fnirs_infos/log_runtime.txt", format="%(message)s", filemode="w", level=logging.INFO)

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
        info_left_smz, info_right_smz, bad_channels = epochs_preparation(filename, SUBJECT, CONDITION)
        # np.save(f'{DIRS_TO_SAVE_STUFF["epochs_folder"]}/{SUBJECT}_{CONDITION}_REST_EPOCHS.npy', rest_epochs)
        # np.save(f'{DIRS_TO_SAVE_STUFF["epochs_folder"]}/{SUBJECT}_{CONDITION}_SMR_EPOCHS.npy', smr_epochs)
        # info_hbo_total.save('../info_hbo_total_info.fif')
        # info_hbr_total.save('../info_hbr_total_info.fif')
        # info_left_smz.save('../info_left_smz_info.fif')
        # info_right_smz.save('../info_right_smz_info.fif')

        total_epochs_number = 30
        

        smr_epochs = replace_with_median(smr_epochs, N=10)*1e6
        rest_epochs = replace_with_median(rest_epochs, N=10)*1e6
        delta_epochs = relative_measure(smr_epochs, rest_epochs)
        delta_epochs = replace_with_median(delta_epochs, 
                                           N=total_epochs_number - delta_epochs.shape[0])

        print('DEL', delta_epochs.shape)
        WINDOW_LOW, WINDOW_HIGH = 4, 12
        TIME_RANGE = [int((WINDOW_LOW-TMIN)*SFREQ), int((WINDOW_HIGH-TMIN)*SFREQ)]
        print(TIME_RANGE)
        topo_array = np.median(delta_epochs[:, :, TIME_RANGE[0]:TIME_RANGE[1] ], axis=(0,2))

        print(topo_array)
        # print(topo_array)
        indices_M1 = get_channel_indices(M1_LEFT_ROI_HBO, info_hbo_total) 
        indices_S1 = get_channel_indices(S1_LEFT_ROI_HBO, info_hbo_total) 
        indices_remaining = get_channel_indices(REMAINING_LEFT_ROI_HBO, info_hbo_total) 
        
        top_3_in_M1 = initial_indices(topo_array, indices_M1, )
        top_3_in_S1 = initial_indices(topo_array, indices_S1, ) 
        
        evoked_M1_top = np.mean(delta_epochs[:, top_3_in_M1, :] , axis=1)
        evoked_S1_top = np.mean(delta_epochs[:, top_3_in_S1, :] , axis=1)
        evoked_all = np.mean(delta_epochs , axis=1)
        
       
        
        conditions_roi_dict = dict(
                
                rel_ME_LEFT=evoked_M1_top,
                rel_MI_LEFT=evoked_M1_top,
                rel_TS_LEFT=evoked_S1_top,
                rel_TI_LEFT=evoked_S1_top,
                rel_SA_LEFT=evoked_all,
                )
        
        concatenated_rel_left = np.concatenate([
        evoked_M1_top,
        evoked_S1_top,
        evoked_all,
        ], axis=0)

        np.save(f'{DIRS_TO_SAVE_STUFF["relation_path_np"]}/{SUBJECT}_{CONDITION}_rel_left.npy', concatenated_rel_left)

        m1_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['M1'][0] ]
        s1_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['S1'][0] ]
        smz_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['REMAINING'][0]]

        ######################################################################

        ###PLOT RELATION###
        fig, axes = plt.subplots(1, 1, figsize=(20, 18))
        times = np.arange(TMIN, TMAX, 1/SFREQ)
        linewidth = 1.5
        # ylims=(-50, 70)
        ylims=(-5, 15)        
        tmin, tmax = TMIN, TMAX
        topo_linewidth = 1
        pointsize = 20
        topo_width = topo_height = '30%'


        #### RELATION LEFT ####

        rel_line_m1_smr, = axes.plot(times, ez_median(evoked_M1_top), label=f'M1/{curves_hb} SMR', 
                color=fnirs_colors['hbr'])
        make_ci(ax=axes,
                to_plot_around=ez_median(evoked_M1_top), 
                epochs_data=evoked_M1_top, 
                alpha=0.2,  
                color=fnirs_colors['hbr'],
                multiply=False
                )

        rel_line_s1_smr, = axes.plot(times, ez_median(evoked_S1_top), label=f'S1/{curves_hb} SMR', 
                color=fnirs_colors['hbo'])
        make_ci(ax=axes, 
                to_plot_around=ez_median(evoked_S1_top), 
                epochs_data=evoked_S1_top, 
                alpha=0.2,  
                color=fnirs_colors['hbo'],
                multiply=False
                )
        fill_1 = filler_between(axes, ylims)
        set_axis_properties(
                                axes,
                                ylims=ylims, 
                                tlims=(tmin, tmax-1/SFREQ), 
                                title=f'HbO relation in M1 and S1 in LEFT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='Hb difference SMR-REST, Δ μM\L',  
                                linewidth=2, 
                                fontsize=16, 
                                title_size=18,
                                legend_flag=False
                                )
        ### LEGEND PARAMS ###
        ax_legend = fig.add_axes([0.75, 0.10, 0.25, 0.25])
        ax_legend.legend([rel_line_m1_smr, 
                          rel_line_s1_smr, 
                          fill_1], 
                        [f'M1 {curves_hb} difference', 
                        f'S1 {curves_hb} difference', 
                        'Task duration'], 
                        **legend_params_dict) 

        ax_legend.set_frame_on(False)
        ax_legend.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        plt.subplots_adjust(**curves_subplot_params)

        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"relation_path"]}/{SUBJECT}_{CONDITION}_M1S1_rel.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig)

        fig, axes = plt.subplots(1, 1, figsize=(20, 18))

        rel_line_smz_smr, = axes.plot(times, ez_median(evoked_all), label=f'SMA/{curves_hb} SMR', 
                color=fnirs_colors['hbt'])
        make_ci(ax=axes, 
                to_plot_around=ez_median(evoked_all), 
                epochs_data=evoked_all, 
                alpha=0.2,  
                color=fnirs_colors['hbt'],
                multiply=False)

        fill_1 = filler_between(axes, ylims)
        set_axis_properties(
                                axes,
                                ylims=ylims, 
                                tlims=(tmin, tmax-1/SFREQ), 
                                title=f'HbO relation in SMA in LEFT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='Hb difference SMR-REST, Δ μM\L',  
                                linewidth=2, 
                                fontsize=16, 
                                title_size=18,
                                legend_flag=False
                                )
        ### LEGEND PARAMS ###
        ax_legend = fig.add_axes([0.75, 0.10, 0.25, 0.25])
        ax_legend.legend([
                          rel_line_smz_smr, 
                          fill_1], 
                        [
                        f'SMA {curves_hb} difference', 
                        'Task duration'], 
                        **legend_params_dict) 

        ax_legend.set_frame_on(False)
        ax_legend.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        plt.subplots_adjust(**curves_subplot_params)

        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"relation_SMA_path"]}/{SUBJECT}_{CONDITION}_SMA_rel.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig)



        fig, ax = plt.subplots(figsize=(10, 8))
        top_n_chans = 10

        rel_mask_SMR, rel_top_dict_SMR = get_top_channels_mask(topo_array, 
                                                        info_hbo_total, 
                                                        top_n_chans)


        ylims = (-5, 5)

        ### LEFT SMR TOPO ###
        a = mne.viz.plot_topomap(
                                data=topo_array,
                                pos=info_hbo_total,
                                vlim=ylims,
                                axes=ax,
                                contours=3,
                                extrapolate='local',
                                image_interp='linear',
                                cmap=custom_cmap,
                                sphere=(0.0, 0.03, 0.0, 0.095),

                                mask=rel_mask_SMR,
                                mask_params=mask_params,
                                show=False
        )


        ### TITLES ###
        ax.set_title(
                f'Topography of {curves_hb} in subject {SUBJECT}\n in {CONDITION}  in time range {TIME_RANGE[0]/SFREQ+TMIN}:{TIME_RANGE[1]/SFREQ+TMIN}s',
        fontsize=18)

        # ax.set_title(
        #         f'Topography of {curves_hb} in subject {SUBJECT}\n in {CONDITION}  in time range {np.round(rel_peak_time-1, decimals=1)}:{np.round(rel_peak_time+1, decimals=1)}s',
        # fontsize=18)

        ### COLORBAR SETTINGS ###
        sm = plt.cm.ScalarMappable(cmap=custom_cmap, 
                                norm=matplotlib.colors.Normalize(vmin=ylims[0], vmax=ylims[1]))

        cbaxes = fig.add_axes([0.075, 0.25, 0.03, 0.5]) # setup colorbar axes. 
        cbar = plt.colorbar(mappable=sm, cax=cbaxes, pad=0.15, orientation='vertical')
        cbar.set_label('Hb difference SMR-REST, Δ μM\L', loc='center', size=12)
        cbar.ax.yaxis.set_label_coords(-0.65, 0.5)
        plt.subplots_adjust(**one_topomap_subplot_params)
        
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"topo_rel_path"]}/{SUBJECT}_{CONDITION}_rel_topo.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig)
        
        np.save(f'{DIRS_TO_SAVE_STUFF["topo_rel_path_np"]}/{SUBJECT}_{CONDITION}_rel_topo_np.npy', topo_array)


        # logging_info = dict(
        # SUBJECT=SUBJECT,
        # CONDITION=CONDITION,
        # BAD_CHANNELS=bad_channels,
        # # T_MAX_HEMO=(final_timestamp+TMIN)/SFREQ,
        # # T_MAX_REL=(rel_final_timestamp+TMIN)/SFREQ,
        # # PREVALENCE_HEMO=prevalent_side,
        # # PREVALENCE_REL=rel_prevalent_side
        # )
        # from collections import OrderedDict

        # def get_sorted_ordered_dict(your_dict):
        #         sorted_items = sorted(your_dict.items(), key=lambda item: item[1], reverse=True)
        #         sorted_ordered_dict = OrderedDict(sorted_items)
        #         return sorted_ordered_dict
        
        # top_dict_SMR_sorted = get_sorted_ordered_dict(top_dict_SMR)
        # top_dict_REST_sorted = get_sorted_ordered_dict(top_dict_REST)
        # rel_top_dict_SMR_sorted = get_sorted_ordered_dict(rel_top_dict_SMR)
        
        # logging.info("SUBJ_NAME: " + logging_info['SUBJECT'])
        # logging.info("CONDITION: " + logging_info['CONDITION'])
        # logging.info(logging_info['BAD_CHANNELS'])
        # # logging.info(logging_info['T_MAX_HEMO'])
        # # logging.info(logging_info['PREVALENCE_HEMO'])
        # # logging.info(logging_info['T_MAX_REL'])
        # # logging.info(logging_info['PREVALENCE_REL'])
        

        # logging.info(top_dict_SMR_sorted)
        # logging.info(top_dict_REST_sorted)
        # logging.info(rel_top_dict_SMR_sorted)
        # logging.info('#'*10)


