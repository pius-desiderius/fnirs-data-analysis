import os
import logging
import matplotlib
from functions_fnirs import *
from ROI import different_hb, different_roi
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from plotting_params import *



TMIN  = float(-1.)
TMAX = float(14.0)
BASELINE = (-1., 0.0)
SFREQ = 2
curves_hb = 'hbo'
logging.basicConfig(filename="log_.txt", format="%(asctime)s %(message)s", filemode="w", level=logging.INFO)


for i in range(100):
    filename = r"C:/Users/Admin/Desktop/IMAGERY-FNIRS/AM/AM_MI"
    subj_and_cond = os.path.split(filename)[-1]
    CONDITION = subj_and_cond.split('_')[1]
    SUBJECT = subj_and_cond.split('_')[0]



    epochs, smr_epochs, rest_epochs, info_hbo_total, info_hbr_total, \
    info_left_smz, info_right_smz, bad_channels = get_epochs(filename, TMIN, TMAX, BASELINE, SFREQ)

    evokeds_SMR_list = []
    evokeds_REST_list = []
    evokeds_info_list = []
    for i in range(6):
        evoked_smr, evoked_rest, info = make_evokeds_roi(smr_epochs=smr_epochs,
                                rest_epochs=rest_epochs,
                                pick=different_hb[curves_hb][i]
                                )
        evokeds_SMR_list.append(evoked_smr)
        evokeds_REST_list.append(evoked_rest)
        evokeds_info_list.append(info)
        
        
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

    info_m1_left = evokeds_info_list[0]
    info_s1_left = evokeds_info_list[1]
    info_smz_left = evokeds_info_list[2]
    info_m1_right = evokeds_info_list[3]
    info_s1_right = evokeds_info_list[4]
    info_smz_right = evokeds_info_list[5]

    if curves_hb == 'hbo':
        evoked_SMR, evoked_REST, info_evoked = make_evokeds_roi(
                                                            smr_epochs=smr_epochs, 
                                                            rest_epochs=rest_epochs,
                                                            pick=info_hbo_total['ch_names'])
    if curves_hb == 'hbr':
        evoked_SMR, evoked_REST, info_evoked = make_evokeds_roi(
                                                            smr_epochs=smr_epochs, 
                                                            rest_epochs=rest_epochs,
                                                            pick=info_hbr_total['ch_names'])
        
        
    ###RELATION LEFT###
    relation_M1_left = relative_measure(M1_evoked_SMR_left.mean(axis=0),
                                        M1_evoked_REST_left.mean(axis=0), SFREQ)
    relation_S1_left = relative_measure(S1_evoked_SMR_left.mean(axis=0),
                                        S1_evoked_REST_left.mean(axis=0), SFREQ)
    relation_SMZ_left = relative_measure(SMZ_evoked_SMR_left.mean(axis=0),
                                        SMZ_evoked_REST_left.mean(axis=0), SFREQ)

    ###RELATION RIGHT###
    relation_M1_right = relative_measure(M1_evoked_SMR_right.mean(axis=0),
                                        M1_evoked_REST_right.mean(axis=0), SFREQ)
    relation_S1_right = relative_measure(S1_evoked_SMR_right.mean(axis=0),
                                        S1_evoked_REST_right.mean(axis=0), SFREQ)
    relation_SMZ_right = relative_measure(SMZ_evoked_SMR_right.mean(axis=0),
                                        SMZ_evoked_REST_right.mean(axis=0), SFREQ)


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

    m1_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['M1'][0] ]
    s1_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['S1'][0] ]
    smz_group_left = [info_left_smz.ch_names.index(ch) for ch in different_roi['REMAINING'][0]]

    m1_group_right = [info_right_smz.ch_names.index(ch) for ch in different_roi['M1'][2] ]
    s1_group_right = [info_right_smz.ch_names.index(ch) for ch in different_roi['S1'][2] ]
    smz_group_right = [info_right_smz.ch_names.index(ch) for ch in different_roi['REMAINING'][2]]

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


    ###PLOT RELATION###
    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
    times = np.arange(TMIN, TMAX, 1/2)
    linewidth = 1.5
    ylims=(-1000, 1500)
    tmin, tmax = TMIN, TMAX
    topo_linewidth = 1
    pointsize = 20
    topo_width = topo_height = '30%'



    ### RELATION RIGHT ####

    rel_line_m1_smr, = axes[0].plot(times, relation_M1_left, label=f'M1/{curves_hb} SMR', 
            color=fnirs_colors['hbr'])
    rel_line_s1_smr, = axes[0].plot(times, relation_S1_left, label=f'S1/{curves_hb} SMR', 
            color=fnirs_colors['hbo'])
    rel_line_smz_smr, = axes[0].plot(times, relation_SMZ_left, label=f'SMR/{curves_hb} SMR', 
            color=fnirs_colors['hbt'])

    fill_1 = filler_between(axes[0], ylims)

    set_axis_properties(
                        axes[0],
                        ylims=ylims, 
                        tlims=(tmin, tmax), 
                        title=f'HbO relation in LEFT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                        xlabel='Time, s', 
                        ylabel='Hb relation SMR/REST, %',  
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
    axes[1].plot(times, relation_SMZ_right, label=f'SMR/{curves_hb} SMR', 
            color=fnirs_colors['hbt'])


    fill_1 = filler_between(axes[1], ylims)

    set_axis_properties(
                        axes[1],
                        ylims=ylims, 
                        tlims=(tmin, tmax), 
                        title=f'HbO relation in RIGHT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
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
                    f'SMZ {curves_hb} relation', 
                    'Task duration'], 
                    **legend_params_dict) 

    ax_legend.set_frame_on(False)
    ax_legend.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    plt.subplots_adjust(**curves_subplot_params)





    ### PLOT HEMODYNAMICS PER SE ###

    fig, axes = plt.subplots(1, 2, figsize=(20, 12))

    ylims=(-12, 16)


    ### LEFT PART ###

    line_m1_smr, = axes[0].plot(times, M1_evoked_SMR_left.mean(axis=0)*1e6, label=f'M1/{curves_hb} SMR', 
            color=fnirs_colors['hbr'])
    line_s1_smr, = axes[0].plot(times, S1_evoked_SMR_left.mean(axis=0)*1e6, label=f'S1/{curves_hb} SMR', 
            color=fnirs_colors['hbo'])
    line_smz_smr, = axes[0].plot(times, SMZ_evoked_SMR_left.mean(axis=0)*1e6, label=f'SMR/{curves_hb} SMR', 
            color=fnirs_colors['hbt'])
    line_m1_rest, = axes[0].plot(times, M1_evoked_REST_left.mean(axis=0)*1e6, label=f'M1/{curves_hb} REST', 
            color=fnirs_colors['hbr'], linestyle='--')
    line_s1_rest, = axes[0].plot(times, S1_evoked_REST_left.mean(axis=0)*1e6, label=f'S1/{curves_hb} REST', 
            color=fnirs_colors['hbo'], linestyle='--')
    line_smz_rest, = axes[0].plot(times, SMZ_evoked_REST_left.mean(axis=0)*1e6, label=f'SMR/{curves_hb} REST', 
            color=fnirs_colors['hbt'], linestyle='--')

    fill_1 = filler_between(axes[0], ylims)

    set_axis_properties(axes[0],
                        ylims=ylims, 
                        tlims=(tmin, tmax), 
                        title=f'HbO response in LEFT hemisphere\nSubject {SUBJECT} Condition {CONDITION}',
                        xlabel='Time, s', 
                        ylabel='Hb concentration, Δ μM\L',  
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
    axes[1].plot(times, M1_evoked_SMR_right.mean(axis=0)*1e6, label=f'M1/{curves_hb} SMR', 
            color=fnirs_colors['hbr'])
    axes[1].plot(times, S1_evoked_SMR_right.mean(axis=0)*1e6, label=f'S1/{curves_hb} SMR', 
            color=fnirs_colors['hbo'])
    axes[1].plot(times, SMZ_evoked_SMR_right.mean(axis=0)*1e6, label=f'SMR/{curves_hb} SMR', 
            color=fnirs_colors['hbt'])
    axes[1].plot(times, M1_evoked_REST_right.mean(axis=0)*1e6, label=f'M1/{curves_hb} REST', 
            color=fnirs_colors['hbr'], linestyle='--')
    axes[1].plot(times, S1_evoked_REST_right.mean(axis=0)*1e6, label=f'S1/{curves_hb} REST', 
            color=fnirs_colors['hbo'], linestyle='--')
    axes[1].plot(times, SMZ_evoked_REST_right.mean(axis=0)*1e6, label=f'SMR/{curves_hb} REST', 
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
                    [f'M1/{curves_hb} SMR', f'S1/{curves_hb} SMR', f'SMZ/{curves_hb} SMR', 
                    f'M1/{curves_hb} REST', f'S1/{curves_hb} REST',f'SMZ/{curves_hb} REST',
                    'Task duration'], 
                    **legend_params_dict) 

    ax_legend.set_frame_on(False)
    ax_legend.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    plt.subplots_adjust(**curves_subplot_params)





    final_timestamp, prevalent_side = get_max_time(f'{CONDITION}_LEFT', f'{CONDITION}_RIGHT')
    rel_final_timestamp, rel_prevalent_side = get_max_time(f'rel_{CONDITION}_LEFT', 
                                                        f'rel_{CONDITION}_RIGHT')
    top_n_chans = 10
    smr_in_peak_timestamp = evoked_SMR[:, final_timestamp]
    rest_in_peak_timestamp = evoked_REST[:, final_timestamp]

    mask_SMR, top_dict_SMR = get_top_channels_mask(smr_in_peak_timestamp, 
                                                info_hbo_total, 
                                                top_n_chans)
    mask_REST, top_dict_REST = get_top_channels_mask(rest_in_peak_timestamp, 
                                                info_hbo_total, 
                                                top_n_chans)






    min1, max1 = min(smr_in_peak_timestamp*1e6), max(smr_in_peak_timestamp*1e6)
    min2, max2 = min(rest_in_peak_timestamp*1e6), max(rest_in_peak_timestamp*1e6)
    ylims = (min(min1, min2), max(max1, max2))

    fig, axes = plt.subplots(1, 2, figsize=(20, 12))

    ### LEFT SMR TOPO ###
    mne.viz.plot_topomap(data=smr_in_peak_timestamp*1e6,
                            pos=info_hbo_total,
                            axes=axes[0],
                            vlim=ylims,
                            contours=6,
                            extrapolate='local',
                            image_interp='linear',
                            cmap=custom_cmap, 
                            mask=mask_SMR,
                            mask_params=mask_params)
    ### RIGHT REST TOPO ###
    mne.viz.plot_topomap(data=rest_in_peak_timestamp*1e6,
                            pos=info_hbo_total,
                            axes=axes[1],
                            vlim=ylims,
                            contours=6,
                            extrapolate='local',
                            image_interp='linear',
                            cmap=custom_cmap,
                            mask=mask_REST,
                            mask_params=mask_params, )

    ### TITLES ###
    axes[0].set_title(
        f'Topography of {curves_hb} in subject {SUBJECT}\n in {CONDITION} condititon, t={final_timestamp/SFREQ}s',
    fontsize=18)

    axes[1].set_title(
        f'Topography of {curves_hb} in subject {SUBJECT}\n in REST condititon, t={final_timestamp/SFREQ}s',
    fontsize=18)

    ### COLORBAR SETTINGS ###
    sm = plt.cm.ScalarMappable(cmap=custom_cmap, 
                            norm=matplotlib.colors.Normalize(vmin=ylims[0], vmax=ylims[1]))

    cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5]) # setup colorbar axes. 
    cbar = plt.colorbar(mappable=sm, cax=cbaxes, pad=0.15, orientation='vertical')
    cbar.set_label(' Hb concentration, Δ μM\L', loc='center', size=12)
    cbar.ax.yaxis.set_label_coords(-0.5, 0.5)
    plt.subplots_adjust(**two_topomaps_subplot_params)


    fig, ax = plt.subplots(figsize=(10, 8))

    top_n_chans = 10
    topo_rel = relative_measure_topo(evoked_SMR, evoked_REST, SFREQ)
    rel_smr_in_peak_timestamp = topo_rel[:, rel_final_timestamp]
    rel_mask_SMR, rel_top_dict_SMR = get_top_channels_mask(rel_smr_in_peak_timestamp, 
                                                info_hbo_total, 
                                                top_n_chans)


    # min1, max1 = min(rel_smr_in_peak_timestamp), max(rel_smr_in_peak_timestamp)
    # ylims = (min(rel_smr_in_peak_timestamp), max(rel_smr_in_peak_timestamp))
    ylims = (-2000, 2000)



    ### LEFT SMR TOPO ###
    mne.viz.plot_topomap(
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
    )


    ### TITLES ###
    ax.set_title(
        f'Topography of {curves_hb} in subject {SUBJECT}\n in {CONDITION} condititon, t={rel_final_timestamp/SFREQ}s',
    fontsize=18)


    ### COLORBAR SETTINGS ###
    sm = plt.cm.ScalarMappable(cmap=custom_cmap, 
                            norm=matplotlib.colors.Normalize(vmin=ylims[0], vmax=ylims[1]))

    cbaxes = fig.add_axes([0.075, 0.25, 0.03, 0.5]) # setup colorbar axes. 
    cbar = plt.colorbar(mappable=sm, cax=cbaxes, pad=0.15, orientation='vertical')
    cbar.set_label(' Hb concentration, Δ μM\L', loc='center', size=12)
    cbar.ax.yaxis.set_label_coords(-0.65, 0.5)
    plt.subplots_adjust(**one_topomap_subplot_params)



    logging_info = dict(
    SUBJECT=SUBJECT,
    CONDITION=CONDITION,
    BAD_CHANNELS=bad_channels,
    T_MAX_HEMO=final_timestamp/SFREQ,
    T_MAX_REL=rel_final_timestamp/SFREQ,
    PREVALENCE_HEMO=prevalent_side,
    PREVALENCE_REL=rel_prevalent_side
    )
    top_dict_SMR
    top_dict_REST
    rel_top_dict_SMR
    
    logging.info(logging_info['SUBJECT'])
    logging.info(logging_info['CONDITION'])
    logging.info(logging_info['BAD_CHANNELS'])
    logging.info(logging_info['T_MAX_HEMO'])
    logging.info(logging_info['T_MAX_REL'])
    logging.info(logging_info['PREVALENCE_HEMO'])
    logging.info(logging_info['PREVALENCE_REL'])
    
    logging.info(logging_info['T_MAX_REL'])
    logging.info(logging_info['PREVALENCE_HEMO'])
    logging.info(logging_info['PREVALENCE_REL'])
    [f'{i}, {v}' for i, v in top_dict_SMR.items()]