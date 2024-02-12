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
#     hbo='#C91111',
#     hbt= '#5B324B',
#     hbr='#004E7C',
    
    hbo='#C91111',
    hbt= '#A4C210',
    hbr='#135181',
  )

logging.basicConfig(filename="log_runtime.txt", format="%(asctime)s %(message)s", filemode="w", level=logging.INFO)

fnirs_dir = "/mnt/diskus/fNIRS data ME_MI_TS_TI_SA"
for items in DIRS_TO_SAVE_STUFF.values():
    os.makedirs(items, exist_ok=True)
    
DICT_OF_SUBJ_RECORDS = subject_records_dict(fnirs_dir=fnirs_dir)
subjects = list(DICT_OF_SUBJ_RECORDS.keys())

for subj in subjects:
    records = DICT_OF_SUBJ_RECORDS[subj]
    max_norms_in_records = []
    min_norms_in_records = []

    
    for filename in records:
        max_norm, min_norm = subject_norms_getter(filename=filename)
        max_norms_in_records.append(max_norm)
        min_norms_in_records.append(min_norm)

    max_norm = max(max_norms_in_records)
    min_norm = min(min_norms_in_records)
    
    for filename in records:
        subj_and_cond = os.path.split(filename)[-1]
        print(subj_and_cond)
        CONDITION = subj_and_cond.split('_')[1]
        SUBJECT = subj_and_cond.split('_')[0]

        epochs, smr_epochs, rest_epochs, info_hbo_total, info_hbr_total, \
        info_left_smz, info_right_smz, bad_channels = epochs_preparation(filename, SUBJECT, CONDITION)
        
        evokeds_SMR_list, evokeds_REST_list = evokeds_preparation(smr_epochs, 
                                                                  rest_epochs,
                                                                  max_norm,
                                                                  min_norm,
                                                                  info=info_hbo_total)

        M1_evoked_SMR_left = evokeds_SMR_list[0]
        S1_evoked_SMR_left = evokeds_SMR_list[1]
        SMZ_evoked_SMR_left = evokeds_SMR_list[2]
        M1_evoked_SMR_right = evokeds_SMR_list[3]
        S1_evoked_SMR_right =  evokeds_SMR_list[4]
        SMZ_evoked_SMR_right = evokeds_SMR_list[5]

        M1_evoked_REST_left = evokeds_REST_list[0]
        S1_evoked_REST_left = evokeds_REST_list[1]
        SMZ_evoked_REST_left = evokeds_REST_list[2]
        M1_evoked_REST_right = evokeds_REST_list[3]
        S1_evoked_REST_right =  evokeds_REST_list[4]
        SMZ_evoked_REST_right = evokeds_REST_list[5]


        if curves_hb == 'hbo':
                evoked_SMR, evoked_REST = make_evokeds_roi(
                                                                smr_epochs=smr_epochs, 
                                                                rest_epochs=rest_epochs,
                                                                pick=info_hbo_total['ch_names'],
                                                                averaging_method='median')
                
                evoked_SMR = norm_minmax(evoked_SMR, max_norm, min_norm)
                evoked_REST = norm_minmax(evoked_REST, max_norm, min_norm)
                
        if curves_hb == 'hbr':
                evoked_SMR, evoked_REST = make_evokeds_roi(
                                                                smr_epochs=smr_epochs, 
                                                                rest_epochs=rest_epochs,
                                                                pick=info_hbr_total['ch_names'],
                                                                averaging_method='median')
                evoked_SMR = norm_minmax(evoked_SMR, max_norm, min_norm)
                evoked_REST = norm_minmax(evoked_REST, max_norm, min_norm)
        ### RELATIVE MEASURE ERD-STYLE ###      
                
        # ##RELATION LEFT###
        # relation_M1_left = relative_measure(M1_evoked_SMR_left.mean(axis=0),
        #                                         M1_evoked_REST_left.mean(axis=0), SFREQ)
        # relation_S1_left = relative_measure(S1_evoked_SMR_left.mean(axis=0),
        #                                         S1_evoked_REST_left.mean(axis=0), SFREQ)
        # relation_SMZ_left = relative_measure(SMZ_evoked_SMR_left.mean(axis=0),
        #                                         SMZ_evoked_REST_left.mean(axis=0), SFREQ)

        # ###RELATION RIGHT###
        # relation_M1_right = relative_measure(M1_evoked_SMR_right.mean(axis=0),
        #                                         M1_evoked_REST_right.mean(axis=0), SFREQ)
        # relation_S1_right = relative_measure(S1_evoked_SMR_right.mean(axis=0),
        #                                         S1_evoked_REST_right.mean(axis=0), SFREQ)
        # relation_SMZ_right = relative_measure(SMZ_evoked_SMR_right.mean(axis=0),
        #                                         SMZ_evoked_REST_right.mean(axis=0), SFREQ)

        ## RELATIVE MEASURE OTHER STLYE ###
        relation_M1_left = np.median(M1_evoked_SMR_left - np.median(M1_evoked_REST_left, axis=0), axis=0)
        relation_S1_left = np.median(S1_evoked_SMR_left - np.median(S1_evoked_REST_left, axis=0), axis=0)
        relation_SMZ_left = np.median(SMZ_evoked_SMR_left - np.median(SMZ_evoked_REST_left, axis=0), axis=0)
        relation_M1_right = np.median(M1_evoked_SMR_right - np.median(M1_evoked_REST_right, axis=0), axis=0)
        relation_S1_right = np.median(S1_evoked_SMR_right - np.median(S1_evoked_REST_right, axis=0), axis=0)
        relation_SMZ_right = np.median(SMZ_evoked_SMR_right - np.median(SMZ_evoked_REST_right, axis=0), axis=0)



        conditions_roi_dict = dict(
                ME_LEFT=M1_evoked_SMR_left.mean(axis=0),
                ME_RIGHT=M1_evoked_SMR_right.mean(axis=0),
                MI_LEFT=M1_evoked_SMR_left.mean(axis=0),
                MI_RIGHT=M1_evoked_SMR_right.mean(axis=0),
                TS_LEFT=S1_evoked_SMR_left.mean(axis=0),
                TS_RIGHT=S1_evoked_SMR_right.mean(axis=0),
                TI_LEFT=S1_evoked_SMR_left.mean(axis=0),
                TI_RIGHT=S1_evoked_SMR_right.mean(axis=0),
                SA_LEFT=SMZ_evoked_SMR_left.mean(axis=0),
                SA_RIGHT=SMZ_evoked_SMR_right.mean(axis=0),
                
                rel_ME_LEFT=relation_M1_left,
                rel_ME_RIGHT=relation_M1_right,
                rel_MI_LEFT=relation_M1_left,
                rel_MI_RIGHT=relation_M1_right,
                rel_TS_LEFT=relation_S1_left,
                rel_TS_RIGHT=relation_S1_right,
                rel_TI_LEFT=relation_S1_left,
                rel_TI_RIGHT=relation_S1_right,
                rel_SA_LEFT=relation_SMZ_left,
                rel_SA_RIGHT=relation_SMZ_right,
                )
        
        concatenated_smr_left = np.concatenate([
        M1_evoked_SMR_left,
        S1_evoked_SMR_left,
        SMZ_evoked_SMR_left,
    
        ], axis=0)
        concatenated_smr_right = np.concatenate([
        M1_evoked_SMR_right,
        S1_evoked_SMR_right,
        SMZ_evoked_SMR_right,
        ], axis=0)
        
        concatenated_rest_left = np.concatenate([
        M1_evoked_REST_left,
        S1_evoked_REST_left,
        SMZ_evoked_REST_left,
    
        ], axis=0)
        concatenated_rest_right = np.concatenate([
        M1_evoked_REST_right,
        S1_evoked_REST_right,
        SMZ_evoked_REST_right,
        ], axis=0)
        
        np.save(f'{DIRS_TO_SAVE_STUFF["haemo_folder_path_np"]}/{SUBJECT}_{CONDITION}_smr_left.npy', concatenated_smr_left)
        np.save(f'{DIRS_TO_SAVE_STUFF["haemo_folder_path_np"]}/{SUBJECT}_{CONDITION}_smr_right.npy', concatenated_smr_right )
        np.save(f'{DIRS_TO_SAVE_STUFF["haemo_folder_path_np"]}/{SUBJECT}_{CONDITION}_rest_left.npy',concatenated_rest_left )
        np.save(f'{DIRS_TO_SAVE_STUFF["haemo_folder_path_np"]}/{SUBJECT}_{CONDITION}_rest_right.npy', concatenated_rest_right)
        
        
        concatenated_rel_left = np.concatenate([
        relation_M1_left,
        relation_S1_left,
        relation_SMZ_left,
        ], axis=0)
        concatenated_rel_right = np.concatenate([
        relation_M1_right,
        relation_S1_right,
        relation_SMZ_right,
        ], axis=0)
        
        np.save(f'{DIRS_TO_SAVE_STUFF["relation_path_np"]}/{SUBJECT}_{CONDITION}_rel_left.npy', concatenated_rel_left)
        np.save(f'{DIRS_TO_SAVE_STUFF["relation_path_np"]}/{SUBJECT}_{CONDITION}_rel_right.npy', concatenated_rel_right )

        m1_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['M1'][0] ]
        s1_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['S1'][0] ]
        smz_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['REMAINING'][0]]

        m1_group_right = [info_right_smz.ch_names.index(ch) for ch in different_roi['M1'][2] ]
        s1_group_right = [info_right_smz.ch_names.index(ch) for ch in different_roi['S1'][2] ]
        smz_group_right = [info_right_smz.ch_names.index(ch) for ch in different_roi['REMAINING'][2]]



        ###PLOT RELATION###
        fig, axes = plt.subplots(1, 2, figsize=(20, 12))
        times = np.arange(TMIN, TMAX, 1/SFREQ)
        linewidth = 1.5
        # ylims=(0, 100)
        ylims = (-0.2, 0.5)
        tmin, tmax = TMIN, TMAX
        topo_linewidth = 1
        pointsize = 20
        topo_width = topo_height = '30%'



        ### RELATION LEFT ####

        rel_line_m1_smr, = axes[0].plot(times, relation_M1_left, label=f'M1/{curves_hb} SMR', 
                color=fnirs_colors['hbr'])
        rel_line_s1_smr, = axes[0].plot(times, relation_S1_left, label=f'S1/{curves_hb} SMR', 
                color=fnirs_colors['hbo'])
        rel_line_smz_smr, = axes[0].plot(times, relation_SMZ_left, label=f'SMA/{curves_hb} SMR', 
                color=fnirs_colors['hbt'])

        fill_1 = filler_between(axes[0], ylims)

        set_axis_properties(
                                axes[0],
                                ylims=ylims, 
                                tlims=(tmin, tmax), 
                                title=f'Hb difference in LEFT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='Hb difference SMR-REST, a.u.',  
                                linewidth=1.5, 
                                fontsize=14, 
                                title_size=18,
                                legend_flag=False
                                )

        ### TOPO FOR LEFT RELATION PICTURE ###
        inset_ax1 = inset_axes(axes[0], 
                                width=topo_width, 
                                height=topo_height, 
                                loc="lower right")

        mne.viz.plot_sensors(
                                info_left_smz.info, 
                                ch_groups=[
                                                m1_group_left, 
                                                smz_group_left,
                                                s1_group_left
                                ],
                                axes=inset_ax1,
                                pointsize=pointsize, 
                                linewidth=topo_linewidth
        )

        ### RELATION RIGHT ###

        axes[1].plot(times, relation_M1_right, label=f'M1/{curves_hb} SMR', 
                color=fnirs_colors['hbr'])
        axes[1].plot(times, relation_S1_right, label=f'S1/{curves_hb} SMR', 
                color=fnirs_colors['hbo'])
        axes[1].plot(times, relation_SMZ_right, label=f'SMA/{curves_hb} SMR', 
                color=fnirs_colors['hbt'])


        fill_1 = filler_between(axes[1], ylims)

        set_axis_properties(
                                axes[1],
                                ylims=ylims, 
                                tlims=(tmin, tmax), 
                                title=f'Hb difference in RIGHT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='',  
                                linewidth=1.5, 
                                fontsize=14, 
                                title_size=18,
                                legend_flag=False
        )

        ### TOPO FOR RIGHT RELATION PICTURE ###
        inset_ax2 = inset_axes(axes[1], width=topo_width, height=topo_height, loc="lower right")
        mne.viz.plot_sensors(info_right_smz.info, 
                                ch_groups=[m1_group_right, 
                                        smz_group_right,
                                        s1_group_right],
                                axes=inset_ax2, 
                                pointsize=pointsize, 
                                linewidth=topo_linewidth)
                        
        ### LEGEND PARAMS ###
        ax_legend = fig.add_axes([0.25, 0.25, 0.5, 0.25])
        ax_legend.legend([rel_line_m1_smr, rel_line_s1_smr, rel_line_smz_smr, fill_1], 
                        [f'M1 {curves_hb} relation', 
                        f'S1 {curves_hb} relation', 
                        f'SMA {curves_hb} relation', 
                        'Task duration'], 
                        **legend_params_dict) 

        ax_legend.set_frame_on(False)
        ax_legend.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        plt.subplots_adjust(**curves_subplot_params)

        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"relation_path"]}/{SUBJECT}_{CONDITION}_rel.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig)



        ### PLOT HEMODYNAMICS PER SE ###

        fig, axes = plt.subplots(1, 2, figsize=(20, 12))

        ylims=(0.2, 0.8)
        ### LEFT PART ###

        line_m1_smr, = axes[0].plot(times, M1_evoked_SMR_left.mean(axis=0), label=f'M1/{curves_hb} SMR', 
                color=fnirs_colors['hbr'])
        line_s1_smr, = axes[0].plot(times, S1_evoked_SMR_left.mean(axis=0), label=f'S1/{curves_hb} SMR', 
                color=fnirs_colors['hbo'])
        line_smz_smr, = axes[0].plot(times, SMZ_evoked_SMR_left.mean(axis=0), label=f'SMA/{curves_hb} SMR', 
                color=fnirs_colors['hbt'])
        line_m1_rest, = axes[0].plot(times, M1_evoked_REST_left.mean(axis=0), label=f'M1/{curves_hb} REST', 
                color=fnirs_colors['hbr'], linestyle='--')
        line_s1_rest, = axes[0].plot(times, S1_evoked_REST_left.mean(axis=0), label=f'S1/{curves_hb} REST', 
                color=fnirs_colors['hbo'], linestyle='--')
        line_smz_rest, = axes[0].plot(times, SMZ_evoked_REST_left.mean(axis=0), label=f'SMA/{curves_hb} REST', 
                color=fnirs_colors['hbt'], linestyle='--')

        fill_1 = filler_between(axes[0], ylims)

        set_axis_properties(axes[0],
                                ylims=ylims, 
                                tlims=(tmin, tmax), 
                                title=f'HbO response in LEFT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='Hb concentration, Δ a.u.',  
                                linewidth=1.5, 
                                fontsize=14, 
                                title_size=18,
                                legend_flag=False
                                )
        ### LEFT HEMO TOPOMAP ###
        inset_ax1 = inset_axes(axes[0], width=topo_width, height=topo_height, loc="lower right")
        mne.viz.plot_sensors(info_left_smz.info, 
                                ch_groups=[  m1_group_left, 
                                        smz_group_left,
                                        s1_group_left],
                                axes=inset_ax1,
                                pointsize=pointsize, 
                                linewidth=topo_linewidth)

        ### RIGHT PART ###
        axes[1].plot(times, M1_evoked_SMR_right.mean(axis=0), label=f'M1/{curves_hb} SMR', 
                color=fnirs_colors['hbr'])
        axes[1].plot(times, S1_evoked_SMR_right.mean(axis=0), label=f'S1/{curves_hb} SMR', 
                color=fnirs_colors['hbo'])
        axes[1].plot(times, SMZ_evoked_SMR_right.mean(axis=0), label=f'SMA/{curves_hb} SMR', 
                color=fnirs_colors['hbt'])
        axes[1].plot(times, M1_evoked_REST_right.mean(axis=0), label=f'M1/{curves_hb} REST', 
                color=fnirs_colors['hbr'], linestyle='--')
        axes[1].plot(times, S1_evoked_REST_right.mean(axis=0), label=f'S1/{curves_hb} REST', 
                color=fnirs_colors['hbo'], linestyle='--')
        axes[1].plot(times, SMZ_evoked_REST_right.mean(axis=0), label=f'SMA/{curves_hb} REST', 
                color=fnirs_colors['hbt'], linestyle='--')

        fill_2 = filler_between(axes[1], ylims)


        set_axis_properties(axes[1],
                                ylims=ylims, 
                                tlims=(tmin, tmax), 
                                title=f'HbO response in RIGHT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                                xlabel='Time, s', 
                                ylabel='',  
                                linewidth=1.5, 
                                fontsize=14, 
                                title_size=18,
                                legend_flag=False,
                                )

        ### RIGHT HEMO TOPOMAP ###
        inset_ax2 = inset_axes(axes[1], width=topo_width, height=topo_height, loc="lower right")
        mne.viz.plot_sensors(
                                info_right_smz.info, 
                                ch_groups=[
                                        m1_group_right, 
                                        smz_group_right,
                                        s1_group_right],
                                axes=inset_ax2, 
                                pointsize=pointsize, 
                                linewidth=topo_linewidth)
                                

        ### LEGENDS PARAMS ###
        ax_legend = fig.add_axes([0.25, 0.25, 0.5, 0.25])
        ax_legend.legend([line_m1_smr, line_s1_smr, line_smz_smr,
                        line_m1_rest, line_s1_rest, line_smz_rest, fill_1], 
                        [f'M1/{curves_hb} SMR', f'S1/{curves_hb} SMR', f'SMA/{curves_hb} SMR', 
                        f'M1/{curves_hb} REST', f'S1/{curves_hb} REST',f'SMA/{curves_hb} REST',
                        'Task duration'], 
                        **legend_params_dict) 

        ax_legend.set_frame_on(False)
        ax_legend.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        plt.subplots_adjust(**curves_subplot_params)
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"haemo_folder_path"]}/{SUBJECT}_{CONDITION}_haemo.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig) 


        def get_max_time(cond_left, cond_right):
                mean_left_cond = conditions_roi_dict[cond_left]
                mean_right_cond = conditions_roi_dict[cond_right]

                peak_timestamp_left = np.argmax(mean_left_cond)
                peak_timestamp_right = np.argmax(mean_right_cond)
                
                max_value_left = mean_left_cond[peak_timestamp_left]
                max_value_right = mean_right_cond[peak_timestamp_right]

                prevalent_side = 'left' if max_value_left > max_value_right else 'right'
                final_timestamp = peak_timestamp_left if max_value_left > max_value_right else peak_timestamp_right
                
                return final_timestamp, prevalent_side


        final_timestamp, prevalent_side = get_max_time(f'{CONDITION}_LEFT', f'{CONDITION}_RIGHT')
        rel_final_timestamp, rel_prevalent_side = get_max_time(f'rel_{CONDITION}_LEFT', 
                                                                f'rel_{CONDITION}_RIGHT')
        # smr_in_peak_timestamp = evoked_SMR[:, final_timestamp]
        # rest_in_peak_timestamp = evoked_REST[:, final_timestamp]
        
        top_n_chans = 10
        
        TIME_RANGE = [int((4-TMIN)*SFREQ), int((12-TMIN)*SFREQ)]
        smr_in_peak_timestamp = np.median(evoked_SMR[:, TIME_RANGE[0]:TIME_RANGE[1]], axis=1)
        rest_in_peak_timestamp = np.median(evoked_REST[:, TIME_RANGE[1]:TIME_RANGE[1]], axis=1)

        mask_SMR, top_dict_SMR = get_top_channels_mask(smr_in_peak_timestamp, 
                                                        info_hbo_total, 
                                                        top_n_chans)
        mask_REST, top_dict_REST = get_top_channels_mask(rest_in_peak_timestamp, 
                                                        info_hbo_total, 
                                                        top_n_chans)






        # min1, max1 = min(smr_in_peak_timestamp*1e6), max(smr_in_peak_timestamp*1e6)
        # min2, max2 = min(rest_in_peak_timestamp*1e6), max(rest_in_peak_timestamp*1e6)
        # ylims = (min(min1, min2), max(max1, max2))
        ylims = (-8, 12)

        fig, axes = plt.subplots(1, 2, figsize=(20, 12))

        ### LEFT SMR TOPO ###
        a = mne.viz.plot_topomap(data=smr_in_peak_timestamp,
                                pos=info_hbo_total,
                                axes=axes[0],
                                vlim=ylims,
                                contours=6,
                                extrapolate='local',
                                image_interp='linear',
                                cmap=custom_cmap, 
                                mask=mask_SMR,
                                mask_params=mask_params,
                                show=False)
        ### RIGHT REST TOPO ###
        a = mne.viz.plot_topomap(data=rest_in_peak_timestamp,
                                pos=info_hbo_total,
                                axes=axes[1],
                                vlim=ylims,
                                contours=6,
                                extrapolate='local',
                                image_interp='linear',
                                cmap=custom_cmap,
                                mask=mask_REST,
                                mask_params=mask_params, 
                                show=False)

        ### TITLES ###
        axes[0].set_title(
                f'Topography of {curves_hb} in subject {SUBJECT}\n in {CONDITION} in time range{TIME_RANGE[0]}:{TIME_RANGE[1]}s',
        fontsize=18)

        axes[1].set_title(
                f'Topography of {curves_hb} in subject {SUBJECT}\n in REST  in time range{TIME_RANGE[0]}:{TIME_RANGE[1]}s',
        fontsize=18)

        ### COLORBAR SETTINGS ###
        sm = plt.cm.ScalarMappable(cmap=custom_cmap, 
                                norm=matplotlib.colors.Normalize(vmin=ylims[0], vmax=ylims[1]))

        cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5]) # setup colorbar axes. 
        cbar = plt.colorbar(mappable=sm, cax=cbaxes, pad=0.15, orientation='vertical')
        cbar.set_label(' Hb concentration, Δ μM\L', loc='center', size=12)
        cbar.ax.yaxis.set_label_coords(-0.5, 0.5)
        plt.subplots_adjust(**two_topomaps_subplot_params)
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"topo_path"]}/{SUBJECT}_{CONDITION}_smr_rest_topo.png', bbox_inches='tight')
        fig.clear()
        plt.close(fig)
 

        
        topo_nps = np.concatenate([smr_in_peak_timestamp,
                                   rest_in_peak_timestamp,
        ], axis=0)
        np.save(f'{DIRS_TO_SAVE_STUFF["topo_path_np"]}/{SUBJECT}_{CONDITION}_smr_rest_topo.npy', topo_nps)
        np.save(f'{DIRS_TO_SAVE_STUFF["evokeds_"]}/{SUBJECT}_{CONDITION}_evoked_smr.npy', evoked_SMR)
        np.save(f'{DIRS_TO_SAVE_STUFF["evokeds_"]}/{SUBJECT}_{CONDITION}_evoked_rest.npy', evoked_REST)




        fig, ax = plt.subplots(figsize=(10, 8))
        top_n_chans = 10
        rel_evoked = evoked_SMR - evoked_REST
        # topo_rel = relative_measure_topo(evoked_SMR, evoked_REST, SFREQ)
        rel_smr_in_peak_timestamp = np.median(rel_evoked[:, TIME_RANGE[0]:TIME_RANGE[1]], axis=1)
        rel_mask_SMR, rel_top_dict_SMR = get_top_channels_mask(rel_smr_in_peak_timestamp, 
                                                        info_hbo_total, 
                                                        top_n_chans)


        # min1, max1 = min(rel_smr_in_peak_timestamp), max(rel_smr_in_peak_timestamp)
        # ylims = (min(rel_smr_in_peak_timestamp), max(rel_smr_in_peak_timestamp))
        ylims = (-6, 10)

        ### LEFT SMR TOPO ###
        a = mne.viz.plot_topomap(
                                data=rel_smr_in_peak_timestamp,
                                pos=info_hbo_total,
                                vlim=ylims,
                                axes=ax,
                                contours=6,
                                extrapolate='local',
                                image_interp='linear',
                                cmap=custom_cmap,
                                mask=rel_mask_SMR,
                                mask_params=mask_params,
                                show=False
        )


        ### TITLES ###
        ax.set_title(
                f'Topography of {curves_hb} in subject {SUBJECT}\n in {CONDITION} in time range{TIME_RANGE[0]}:{TIME_RANGE[1]}s',
        fontsize=18)


        ### COLORBAR SETTINGS ###
        sm = plt.cm.ScalarMappable(cmap=custom_cmap, 
                                norm=matplotlib.colors.Normalize(vmin=ylims[0], vmax=ylims[1]))

        cbaxes = fig.add_axes([0.075, 0.25, 0.03, 0.5]) # setup colorbar axes. 
        cbar = plt.colorbar(mappable=sm, cax=cbaxes, pad=0.15, orientation='vertical')
        cbar.set_label('Hb relation, %', loc='center', size=12)
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
        T_MAX_HEMO=(final_timestamp+TMIN)/SFREQ,
        T_MAX_REL=(rel_final_timestamp+TMIN)/SFREQ,
        PREVALENCE_HEMO=prevalent_side,
        PREVALENCE_REL=rel_prevalent_side
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
