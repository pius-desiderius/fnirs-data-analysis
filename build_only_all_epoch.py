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

        smr_epochs = replace_with_median(smr_epochs, N=10)
        rest_epochs = replace_with_median(rest_epochs, N=10)
        
        epochs_evokeds_SMR_list, epochs_evokeds_REST_list = evokeds_preparation(smr_epochs, 
                                                                  rest_epochs,
                                                                  max_norm=1,
                                                                  min_norm=2,
                                                                  info=info_hbo_total,
                                                                  normalize=False,
                                                                  general_use=False)

        #how do we average channels, means or medians
        evokeds_SMR_list = [np.mean(i*1e6, axis=1) for i in epochs_evokeds_SMR_list]
        evokeds_REST_list = [np.mean(i*1e6, axis=1) for i in epochs_evokeds_REST_list]

        M1_evoked_SMR_left = evokeds_SMR_list[0]
        S1_evoked_SMR_left = evokeds_SMR_list[1]
        SMZ_evoked_SMR_left = evokeds_SMR_list[2]

        M1_evoked_REST_left = evokeds_REST_list[0]
        S1_evoked_REST_left = evokeds_REST_list[1]
        SMZ_evoked_REST_left = evokeds_REST_list[2]

        
        pochs_M1_evoked_SMR_left = epochs_evokeds_SMR_list[0]
        pochs_S1_evoked_SMR_left = epochs_evokeds_SMR_list[1]
        pochs_SMZ_evoked_SMR_left = epochs_evokeds_SMR_list[2]


        pochs_M1_evoked_REST_left = epochs_evokeds_REST_list[0]
        pochs_S1_evoked_REST_left = epochs_evokeds_REST_list[1]
        pochs_SMZ_evoked_REST_left = epochs_evokeds_REST_list[2]

        
        if curves_hb == 'hbo':
                evoked_SMR, evoked_REST = make_evokeds_roi(
                                                                smr_epochs=smr_epochs, 
                                                                rest_epochs=rest_epochs,
                                                                pick=info_hbo_total['ch_names'],
                                                                averaging_method='median')
                
        if curves_hb == 'hbr':
                evoked_SMR, evoked_REST = make_evokeds_roi(
                                                                smr_epochs=smr_epochs, 
                                                                rest_epochs=rest_epochs,
                                                                pick=info_hbr_total['ch_names'],
                                                                averaging_method='median')
                                
        evoked_SMR = evoked_SMR*1e6
        evoked_REST = evoked_REST*1e6
        ### RELATIVE MEASURE ERD-STYLE ###      
        
        
        # print('M1_evoked_rest', M1_evoked_REST_left.shape)
        ##RELATION LEFT###
        relation_M1_left = relative_measure(M1_evoked_SMR_left,
                                                M1_evoked_REST_left, SFREQ)
        relation_S1_left = relative_measure(S1_evoked_SMR_left,
                                                S1_evoked_REST_left, SFREQ)
        relation_SMZ_left = relative_measure(SMZ_evoked_SMR_left,
                                                SMZ_evoked_REST_left, SFREQ)


        
        z_relation_M1_left = relative_measure(pochs_M1_evoked_SMR_left,
                                                M1_evoked_REST_left, SFREQ)
        z_relation_S1_left = relative_measure(pochs_S1_evoked_SMR_left,
                                                S1_evoked_REST_left, SFREQ)
        z_relation_SMZ_left = relative_measure(pochs_SMZ_evoked_SMR_left,
                                                SMZ_evoked_REST_left, SFREQ)
        
        conditions_roi_dict = dict(
                ME_LEFT=np.median(M1_evoked_SMR_left, axis=0),
                MI_LEFT=np.median(M1_evoked_SMR_left, axis=0),
                TS_LEFT=np.median(S1_evoked_SMR_left, axis=0),
                TI_LEFT=np.median(S1_evoked_SMR_left, axis=0),
                SA_LEFT=np.median(SMZ_evoked_SMR_left, axis=0),
                
                rel_ME_LEFT=relation_M1_left,
                rel_MI_LEFT=relation_M1_left,
                rel_TS_LEFT=relation_S1_left,
                rel_TI_LEFT=relation_S1_left,
                rel_SA_LEFT=relation_SMZ_left,
                )
        
        concatenated_smr_left = np.concatenate([
        M1_evoked_SMR_left,
        S1_evoked_SMR_left,
        SMZ_evoked_SMR_left,
    
        ], axis=0)
        concatenated_rest_left = np.concatenate([
        M1_evoked_REST_left,
        S1_evoked_REST_left,
        SMZ_evoked_REST_left,
    
        ], axis=0)

        
        np.save(f'{DIRS_TO_SAVE_STUFF["haemo_folder_path_np"]}/{SUBJECT}_{CONDITION}_smr_left.npy', concatenated_smr_left)
        np.save(f'{DIRS_TO_SAVE_STUFF["haemo_folder_path_np"]}/{SUBJECT}_{CONDITION}_rest_left.npy',concatenated_rest_left )        
        
        concatenated_rel_left = np.concatenate([
        relation_M1_left,
        relation_S1_left,
        relation_SMZ_left,
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

        rel_line_m1_smr, = axes.plot(times, ez_median(relation_M1_left), label=f'M1/{curves_hb} SMR', 
                color=fnirs_colors['hbr'])
        make_ci(ax=axes,
                to_plot_around=ez_median(relation_M1_left), 
                epochs_data=relation_M1_left, 
                alpha=0.2,  
                color=fnirs_colors['hbr'],
                multiply=False
                )

        rel_line_s1_smr, = axes.plot(times, ez_median(relation_S1_left), label=f'S1/{curves_hb} SMR', 
                color=fnirs_colors['hbo'])
        make_ci(ax=axes, 
                to_plot_around=ez_median(relation_S1_left), 
                epochs_data=relation_S1_left, 
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

        rel_line_smz_smr, = axes.plot(times, ez_median(relation_SMZ_left), label=f'SMA/{curves_hb} SMR', 
                color=fnirs_colors['hbt'])
        make_ci(ax=axes, 
                to_plot_around=ez_median(relation_SMZ_left), 
                epochs_data=relation_SMZ_left, 
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

        ######################################################################
        
        
        ### PLOT HEMODYNAMICS PER SE ###

        fig, axes = plt.subplots(1, 1, figsize=(20, 18))

        ylims=(-6, 18)
        ### LEFT PART ###

        # print('pochs', M1_evoked_SMR_left.shape)
        line_m1_smr, = axes.plot(times, ez_median(M1_evoked_SMR_left), label=f'M1/{curves_hb} SMR', 
                color=fnirs_colors['hbr'])
        make_ci(ax=axes, to_plot_around=ez_median(M1_evoked_SMR_left), epochs_data=pochs_M1_evoked_SMR_left, alpha=0.2,  color=fnirs_colors['hbr'])

        line_s1_smr, = axes.plot(times, ez_median(S1_evoked_SMR_left), label=f'S1/{curves_hb} SMR', 
                color=fnirs_colors['hbo'])
        make_ci(ax=axes, to_plot_around=ez_median(S1_evoked_SMR_left), epochs_data=pochs_S1_evoked_SMR_left, alpha=0.2,  color=fnirs_colors['hbo'])
        
        line_m1_rest, = axes.plot(times, ez_median(M1_evoked_REST_left), label=f'M1/{curves_hb} REST', 
                color=fnirs_colors['hbr'], linestyle='--')
        make_ci(ax=axes, to_plot_around=ez_median(M1_evoked_REST_left), epochs_data=pochs_M1_evoked_REST_left, alpha=0.1,  color=fnirs_colors['hbr'])

        line_s1_rest, = axes.plot(times, ez_median(S1_evoked_REST_left), label=f'S1/{curves_hb} REST', 
                color=fnirs_colors['hbo'], linestyle='--')
        make_ci(ax=axes, to_plot_around=ez_median(S1_evoked_REST_left), epochs_data=pochs_S1_evoked_REST_left, alpha=0.1,  color=fnirs_colors['hbo'])


        set_axis_properties(
                                axes,
                                ylims=ylims, 
                                tlims=(tmin, tmax-1/SFREQ), 
                                title=f'HbO relation in M1 and S1 in LEFT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='Hb concentration, Δ μM\L',  
                                linewidth=2, 
                                fontsize=16, 
                                title_size=18,
                                legend_flag=False
                                )
        fill_1 = filler_between(axes, ylims)
        ### LEGENDS PARAMS ###
        ax_legend = fig.add_axes([0.75, 0.10, 0.25, 0.25])
        ax_legend.legend([line_m1_smr, 
                          line_s1_smr, 
                          line_m1_rest, 
                          line_s1_rest, 
                          fill_1], 
                        [f'M1 {curves_hb} SMR', 
                         f'S1 {curves_hb} SMR', 
                        f'M1 {curves_hb} REST', 
                        f'S1 {curves_hb} REST',
                        'Task duration'], 
                        **legend_params_dict) 
        

        ax_legend.set_frame_on(False)
        ax_legend.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        plt.subplots_adjust(**curves_subplot_params)
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"haemo_folder_path"]}/{SUBJECT}_{CONDITION}_M1_S1_haemo.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig) 
        
        
        fig, axes = plt.subplots(1, 1, figsize=(20, 18))

        line_smz_smr, = axes.plot(times, ez_median(SMZ_evoked_SMR_left), label=f'SMA/{curves_hb} SMR', 
                color=fnirs_colors['hbt'])
        make_ci(ax=axes, to_plot_around=ez_median(SMZ_evoked_SMR_left), epochs_data=pochs_SMZ_evoked_SMR_left, alpha=0.2,  color=fnirs_colors['hbt'])
  
          
        line_smz_rest, = axes.plot(times, ez_median(SMZ_evoked_REST_left), label=f'SMA/{curves_hb} REST', 
                color=fnirs_colors['hbt'], linestyle='--')
        make_ci(ax=axes, to_plot_around=ez_median(SMZ_evoked_REST_left), epochs_data=pochs_SMZ_evoked_REST_left, alpha=0.1,  color=fnirs_colors['hbt'])

        set_axis_properties(
                                axes,
                                ylims=ylims, 
                                tlims=(tmin, tmax-1/SFREQ), 
                                title=f'HbO relation in SMA in LEFT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='Hb concentration, Δ μM\L',  
                                linewidth=2, 
                                fontsize=16, 
                                title_size=18,
                                legend_flag=False
                                )
        fill_1 = filler_between(axes, ylims)
        ### LEGENDS PARAMS ###
        ax_legend = fig.add_axes([0.75, 0.10, 0.25, 0.25])
        ax_legend.legend([
                          line_smz_smr,
                          line_smz_rest, 
                          fill_1], 
                        [
                         f'SMA {curves_hb} SMR', 
                        f'SMA {curves_hb} REST',
                        'Task duration'], 
                        **legend_params_dict) 
        

        ax_legend.set_frame_on(False)
        ax_legend.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        plt.subplots_adjust(**curves_subplot_params)
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"haemo_folder_SMA_path"]}/{SUBJECT}_{CONDITION}_SMA_haemo.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig) 

        def get_max_time(cond_left, time_limits=[int((4-TMIN)*SFREQ), int((12-TMIN)*SFREQ)], median=False):
                if median:
                        mean_left_cond_limited = np.median(conditions_roi_dict[cond_left], axis=0)[time_limits[0]:time_limits[1]]
                else:
                        mean_left_cond_limited = conditions_roi_dict[cond_left][time_limits[0]:time_limits[1]]
                peak_timestamp_left = np.argmax(mean_left_cond_limited)
                
                max_value_left = np.median(mean_left_cond_limited[peak_timestamp_left-1*SFREQ : peak_timestamp_left+1*SFREQ])
                
                return peak_timestamp_left

        WINDOW_LOW, WINDOW_HIGH = 3, 13

        TIME_RANGE = [int((WINDOW_LOW-TMIN)*SFREQ), int((WINDOW_HIGH-TMIN)*SFREQ)]
        final_timestamp = get_max_time(f'{CONDITION}_LEFT')
        rel_final_timestamp = get_max_time(f'rel_{CONDITION}_LEFT', median=True)
        LOWER_TIME, UPPER_TIME = final_timestamp-1*SFREQ, final_timestamp+1*SFREQ
        peak_time = final_timestamp/SFREQ + WINDOW_LOW
        rel_peak_time = rel_final_timestamp/SFREQ + WINDOW_LOW



        
        # smr_in_peak_timestamp = np.mean(evoked_SMR[:, LOWER_TIME+TIME_RANGE[0] : UPPER_TIME+TIME_RANGE[0]], axis=1)
        # rest_in_peak_timestamp = np.mean(evoked_REST[:, LOWER_TIME+TIME_RANGE[0] : UPPER_TIME+TIME_RANGE[0]], axis=1)
        
        smr_in_peak_timestamp = np.median(evoked_SMR[:, TIME_RANGE[0]:TIME_RANGE[1]], axis=1)
        rest_in_peak_timestamp = np.median(evoked_REST[:, TIME_RANGE[0]:TIME_RANGE[1]], axis=1)
        
        
        top_n_chans = 10
        mask_SMR, top_dict_SMR = get_top_channels_mask(smr_in_peak_timestamp, 
                                                        info_hbo_total, 
                                                        top_n_chans)
        mask_REST, top_dict_REST = get_top_channels_mask(rest_in_peak_timestamp, 
                                                        info_hbo_total, 
                                                        top_n_chans)






        # min1, max1 = min(smr_in_peak_timestamp*1e6), max(smr_in_peak_timestamp*1e6)
        # min2, max2 = min(rest_in_peak_timestamp*1e6), max(rest_in_peak_timestamp*1e6)
        # ylims = (min(min1, min2), max(max1, max2))
        ylims = (-7, 7)

        fig, axes = plt.subplots(1, 2, figsize=(20, 12))

        ### LEFT SMR TOPO ###
        a = mne.viz.plot_topomap(data=smr_in_peak_timestamp,
                                pos=info_hbo_total,
                                axes=axes[0],
                                vlim=ylims,
                                contours=3,
                                extrapolate='local',
                                image_interp='linear',
                                cmap=custom_cmap,
                                sphere=sphere,

                                # mask=mask_SMR,
                                # mask_params=mask_params,
                                # names=info_hbo_total['ch_names']
                                
                                show=False
                                )
        ### RIGHT REST TOPO ###
        a = mne.viz.plot_topomap(data=rest_in_peak_timestamp,
                                pos=info_hbo_total,
                                axes=axes[1],
                                vlim=ylims,
                                contours=3,
                                extrapolate='local',
                                image_interp='linear',
                                cmap=custom_cmap,
                                sphere=sphere,
                                # mask=mask_REST,
                                # mask_params=mask_params,
                                # names=info_hbo_total['ch_names']
                                show=False
                                )

        ### TITLES ###
        # axes[0].set_title(
        #         f'Topography of {curves_hb} in subject {SUBJECT}\n in {CONDITION} in time range {np.round(peak_time-1, decimals=1)}:{np.round(peak_time+1, decimals=1)}s',
        # fontsize=18)

        # axes[1].set_title(
        #         f'Topography of {curves_hb} in subject {SUBJECT}\n in REST  in time range {np.round(peak_time-1, decimals=1)}:{np.round(peak_time+1, decimals=1)}s',
        # fontsize=18)
        
        axes[0].set_title(
                f'Topography of {curves_hb} in subject {SUBJECT}\n in {CONDITION} in time range {TIME_RANGE[0]/SFREQ+TMIN}:{TIME_RANGE[1]/SFREQ+TMIN}s',
        fontsize=18)

        axes[1].set_title(
                f'Topography of {curves_hb} in subject {SUBJECT}\n in REST  in time range {TIME_RANGE[0]/SFREQ+TMIN}:{TIME_RANGE[1]/SFREQ+TMIN}s',
        fontsize=18)
        ### COLORBAR SETTINGS ###
        sm = plt.cm.ScalarMappable(cmap=custom_cmap, 
                                norm=matplotlib.colors.Normalize(vmin=ylims[0], vmax=ylims[1]))

        cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5]) # setup colorbar axes. 
        cbar = plt.colorbar(mappable=sm, cax=cbaxes, pad=0.15, orientation='vertical')
        cbar.set_label(' Hb concentration, Δ μM\L', loc='center', size=12)
        cbar.ax.yaxis.set_label_coords(-0.5, 0.5)
        plt.subplots_adjust(**two_topomaps_subplot_params)
        # fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"topo_path"]}/{SUBJECT}_{CONDITION}_smr_rest_topo.png', bbox_inches='tight')
        # fig.clear()
        # plt.close(fig)
 

        
        topo_nps = np.concatenate([smr_in_peak_timestamp,
                                   rest_in_peak_timestamp,
        ], axis=0)
        np.save(f'{DIRS_TO_SAVE_STUFF["topo_path_np"]}/{SUBJECT}_{CONDITION}_smr_rest_topo.npy', topo_nps)
        np.save(f'{DIRS_TO_SAVE_STUFF["evokeds_"]}/{SUBJECT}_{CONDITION}_evoked_smr.npy', evoked_SMR)
        np.save(f'{DIRS_TO_SAVE_STUFF["evokeds_"]}/{SUBJECT}_{CONDITION}_evoked_rest.npy', evoked_REST)




        fig, ax = plt.subplots(figsize=(10, 8))
        top_n_chans = 10
        rel_evoked = np.median(smr_epochs - np.median(rest_epochs, axis=0), axis=0)*1e6
        
        # print('SHIT', rel_evoked.shape)
        # topo_rel = relative_measure_topo(evoked_SMR, evoked_REST, SFREQ)
        LOWER_TIME, UPPER_TIME = rel_final_timestamp-1*SFREQ, rel_final_timestamp+1*SFREQ
        

        # rel_smr_in_peak_timestamp = np.mean(rel_evoked[:, LOWER_TIME+TIME_RANGE[0] : UPPER_TIME+TIME_RANGE[0]], axis=1)
                
        rel_smr_in_peak_timestamp = np.median(rel_evoked[:, TIME_RANGE[0]:TIME_RANGE[1]], axis=1)

        
        rel_mask_SMR, rel_top_dict_SMR = get_top_channels_mask(rel_smr_in_peak_timestamp, 
                                                        info_hbo_total, 
                                                        top_n_chans)


        # min1, max1 = min(rel_smr_in_peak_timestamp), max(rel_smr_in_peak_timestamp)
        # ylims = (min(rel_smr_in_peak_timestamp), max(rel_smr_in_peak_timestamp))
        ylims = (-7, 7)

        ### LEFT SMR TOPO ###
        a = mne.viz.plot_topomap(
                                data=rel_smr_in_peak_timestamp,
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
        
        np.save(f'{DIRS_TO_SAVE_STUFF["topo_rel_path_np"]}/{SUBJECT}_{CONDITION}_rel_topo_np.npy', rel_smr_in_peak_timestamp)
        np.save(f'{DIRS_TO_SAVE_STUFF["evokeds_rel"]}/{SUBJECT}_{CONDITION}_evoked_rel.npy', rel_evoked)



        logging_info = dict(
        SUBJECT=SUBJECT,
        CONDITION=CONDITION,
        BAD_CHANNELS=bad_channels,
        # T_MAX_HEMO=(final_timestamp+TMIN)/SFREQ,
        # T_MAX_REL=(rel_final_timestamp+TMIN)/SFREQ,
        # PREVALENCE_HEMO=prevalent_side,
        # PREVALENCE_REL=rel_prevalent_side
        )
        from collections import OrderedDict

        def get_sorted_ordered_dict(your_dict):
                sorted_items = sorted(your_dict.items(), key=lambda item: item[1], reverse=True)
                sorted_ordered_dict = OrderedDict(sorted_items)
                return sorted_ordered_dict
        
        top_dict_SMR_sorted = get_sorted_ordered_dict(top_dict_SMR)
        top_dict_REST_sorted = get_sorted_ordered_dict(top_dict_REST)
        rel_top_dict_SMR_sorted = get_sorted_ordered_dict(rel_top_dict_SMR)
        
        logging.info("SUBJ_NAME: " + logging_info['SUBJECT'])
        logging.info("CONDITION: " + logging_info['CONDITION'])
        logging.info(logging_info['BAD_CHANNELS'])
        # logging.info(logging_info['T_MAX_HEMO'])
        # logging.info(logging_info['PREVALENCE_HEMO'])
        # logging.info(logging_info['T_MAX_REL'])
        # logging.info(logging_info['PREVALENCE_REL'])
        

        logging.info(top_dict_SMR_sorted)
        logging.info(top_dict_REST_sorted)
        logging.info(rel_top_dict_SMR_sorted)
        logging.info('#'*10)


