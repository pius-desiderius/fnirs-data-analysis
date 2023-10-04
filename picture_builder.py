import os.path as op
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from itertools import compress
from scipy import stats as st
import time
import logging

import mne
import mne_nirs
from mne.preprocessing.nirs import optical_density, beer_lambert_law

from mne.preprocessing.nirs import (optical_density,
                                    temporal_derivative_distribution_repair,
                                    scalp_coupling_index)
from mne import Epochs, events_from_annotations
from functions_fnirs import (fast_scandir, 
                             topomaps_plotter, 
                             clean_epochs)
from meta import *

start = time.time()
logging.basicConfig(filename="log_one_channel.txt", format="%(asctime)s %(message)s", filemode="w", level=logging.INFO)

fnirs_dir = r"C:\Users\Admin\Desktop\IMAGERY-FNIRS"
subfolders = fast_scandir(fnirs_dir)
subj_names = sorted([(i.split('\\')[-1]) for i in subfolders if len(i.split('\\')[-1])==2])
recordings_names = sorted([i for i in subfolders if '_' in i and '.' not in i])

for items in dirs_to_save_stuff.values():
    os.makedirs(items, exist_ok=True)

filename = recordings_names[1]

#########################################################
for filename in recordings_names:
#########################################################
    splitting_slash = '\\'
    CONDITION = filename.split(splitting_slash)[-1].split('_')[-1]
    SUBJECT = filename.split(splitting_slash)[-1].split('_')[0]
    
    raw_intensity = mne.io.read_raw_nirx(
        filename,
        verbose=True
    )
    raw_od = mne.preprocessing.nirs.optical_density(raw_intensity) #from row wavelength data
    
    try:
        raw_od_shorts = mne_nirs.channels.get_short_channels(raw_od)
        sci_shorts = scalp_coupling_index( 
                                    raw_od_shorts, 
                                    h_freq=1.35, 
                                    h_trans_bandwidth=0.1
                                    )
        bad_sci_shorts = list(compress(raw_od_shorts.ch_names, sci_shorts < 0.6))
        raw_od.drop_channels(bad_sci_shorts)
        raw_od = mne_nirs.signal_enhancement.short_channel_regression(raw_od)

    except ValueError:
        pass
    
    try:
       raw_od.drop_channels(special_drop_chans)
    except:
        pass
    
    raw_od.drop_channels(drop_chans) #we had a non-existent channel
    raw_od = mne_nirs.channels.get_long_channels(raw_od)
    sci = scalp_coupling_index( 
                            raw_od, 
                            )
    bad_sci = list(compress(raw_od.ch_names, sci < 0.6))
    bad_sci = [i.replace('760', 'hbr') for i in bad_sci]
    bad_sci = [i.replace('850', 'hbr') for i in bad_sci]
    raw_od.resample(1.0)
    raw_od = temporal_derivative_distribution_repair(raw_od) #repairs movement artifacts
    
    raw_haemo = mne.preprocessing.nirs.beer_lambert_law(raw_od, ppf=0.1) #from wavelength to HbO\HbR
    # low_f_border, high_f_border = 0.05, 0.1
    low_f_border, high_f_border = 0.05, 0.1
    # h_trans_bandwidth, l_trans_bandwidth = 0.2, 0.015

    raw_haemo = raw_haemo.filter(low_f_border, high_f_border,
                                # h_trans_bandwidth=h_trans_bandwidth,
                                # l_trans_bandwidth=l_trans_bandwidth, 
                                n_jobs=-1)
    raw_haemo = mne_nirs.signal_enhancement.enhance_negative_correlation(raw_haemo)

    channel_std = np.std(raw_haemo.get_data(), axis=(1))
    threshold = 1.3*10**-5
    
    outlier_channels = list(np.where(channel_std > threshold)[0])
    channels_to_fix = [raw_haemo.ch_names[i] for i in outlier_channels]
    channels_to_interpolate_hbr = list(set([i.replace('hbo', 'hbr') 
                                            for i in channels_to_fix] + bad_sci))
    
    channels_to_interpolate_hbo = [i.replace('hbr', 'hbo') for i in channels_to_interpolate_hbr]
    channels_to_interpolate = channels_to_interpolate_hbr + channels_to_interpolate_hbo
    print(channels_to_interpolate, '\n', len(channels_to_interpolate))
    raw_haemo.info['bads'] = channels_to_interpolate
    
    # with open(r"C:\Users\Admin\Desktop\logs.txt", 'w') as f:
    #     f.writelines(f'{SUBJECT} {CONDITION} rejected channels: {len(channels_to_interpolate)}\n{channels_to_interpolate}\n')
    logging.info(f'{SUBJECT} {CONDITION} interpolated channels N={len(channels_to_interpolate)}: {channels_to_interpolate}')
    
    raw_haemo = raw_haemo.interpolate_bads()
    chnames = raw_haemo.ch_names
    
    events, ids = mne.events_from_annotations(raw_haemo)
    ids["Rest"] = 2
    ids["Sensorimotor"] = 1
    
    def popper(ids, ids_key):
        try:
            ids.pop(ids_key)
        except:
            pass
        
    ids_to_pop = ["2.0", "33.0", "1.0", "2", "1", "33",]
    for i in ids_to_pop:
        popper(ids, i)

    smr_epochs, rest_epochs, _, _ = clean_epochs(raw_haemo, events=events, ids=ids)
    
    #you can set condition and subject by hand or get it from file's name
    picks_hbo_left, picks_hbr_left = C3_chans_of_interest_hbo, C3_chans_of_interest_hbr
    picks_hbo_right, picks_hbr_right = C4_chans_of_interest_hbo, C4_chans_of_interest_hbr

    smr_epochs_left = smr_epochs.copy().pick_channels(picks_hbo_left + picks_hbr_left)
    smr_epochs_right = smr_epochs.copy().pick_channels(picks_hbo_right + picks_hbr_right)
    rest_epochs_left = rest_epochs.copy().pick_channels(picks_hbo_left + picks_hbr_left)
    rest_epochs_right = rest_epochs.copy().pick_channels(picks_hbo_right + picks_hbr_right)


    #top channel plotting
    smr_evoked_left = smr_epochs_left.copy().average(picks=picks_hbo_left)
    data_smr = smr_evoked_left.get_data()
    mode = st.mode(np.argmax(data_smr, axis=0)[5:12])[0][0]
    top_channel_C3_hbo = smr_evoked_left.ch_names[mode]
    top_channel_C3_hbr = [top_channel_C3_hbo.replace('o', 'r'),]
    top_channel_C3_hbo = [top_channel_C3_hbo, ]

    smr_evoked_right = smr_epochs_right.copy().average(picks=picks_hbo_right)
    data_smr = smr_evoked_right.get_data()
    mode = st.mode(np.argmax(data_smr, axis=0)[5:12])[0][0]
    top_channel_C4_hbo = smr_evoked_right.ch_names[mode]
    top_channel_C4_hbr = [top_channel_C4_hbo.replace('o', 'r'),]
    top_channel_C4_hbo = [top_channel_C4_hbo, ]
    
    logging.info(f'{SUBJECT} {CONDITION} top HbO channels left={top_channel_C3_hbo}')
    logging.info(f'{SUBJECT} {CONDITION} top HbO channels right={top_channel_C4_hbo}')


    evoked_dict_left = {f'{CONDITION}/HbO': smr_epochs_left.copy().average(picks=picks_hbo_left),
                f'{CONDITION}/HbR': smr_epochs_left.copy().average(picks=picks_hbr_left),
                'Rest/HbO': rest_epochs_left.copy().average(picks=picks_hbo_left),
                'Rest/HbR': rest_epochs_left.copy().average(picks=picks_hbr_left)}

    evoked_dict_right = {f'{CONDITION}/HbO': smr_epochs_right.copy().average(picks=picks_hbo_right),
                f'{CONDITION}/HbR': smr_epochs_right.copy().average(picks=picks_hbr_right),
                'Rest/HbO': rest_epochs_right.copy().average(picks=picks_hbo_right),
                'Rest/HbR': rest_epochs_right.copy().average(picks=picks_hbr_right)}
    
    
    # evoked_dict_left = {f'{CONDITION}/HbO': smr_epochs_left.copy().average(picks=top_channel_C3_hbo),
    #             f'{CONDITION}/HbR': smr_epochs_left.copy().average(picks=top_channel_C3_hbr),
    #             'Rest/HbO': rest_epochs_left.copy().average(picks=top_channel_C3_hbo),
    #             'Rest/HbR': rest_epochs_left.copy().average(picks=top_channel_C3_hbr)}

    # evoked_dict_right = {f'{CONDITION}/HbO': smr_epochs_right.copy().average(picks=top_channel_C4_hbo),  
    #             f'{CONDITION}/HbR': smr_epochs_right.copy().average(picks=top_channel_C4_hbr),  
    #             'Rest/HbO': rest_epochs_right.copy().average(picks=top_channel_C4_hbo),  
    #             'Rest/HbR': rest_epochs_right.copy().average(picks=top_channel_C4_hbr)}  

    a_right = evoked_dict_right[f'{CONDITION}/HbO'].get_data()
    b_right = evoked_dict_right[f'{CONDITION}/HbR'].get_data()
    c_right = evoked_dict_right['Rest/HbO'].get_data()
    d_right = evoked_dict_right['Rest/HbR'].get_data()
    right_np_array = np.mean(np.stack(arrays=[a_right, b_right, c_right, d_right]), axis=1).reshape(4, 1, 15)
    np.save(rf'{dirs_to_save_stuff["haemo_folder_path_np"]}\{SUBJECT} {CONDITION} right.npy', right_np_array)
    
    a_left= evoked_dict_left[f'{CONDITION}/HbO'].get_data()
    b_left= evoked_dict_left[f'{CONDITION}/HbR'].get_data()
    c_left= evoked_dict_left['Rest/HbO'].get_data()
    d_left= evoked_dict_left['Rest/HbR'].get_data()
    left_np_array = np.mean(np.stack(arrays=[a_left, b_left, c_left, d_left]), axis=1).reshape(4, 1, 15)
    np.save(rf'{dirs_to_save_stuff["haemo_folder_path_np"]}\{SUBJECT} {CONDITION} left.npy', left_np_array)


    for condition in evoked_dict_left:
        evoked_dict_left[condition].rename_channels(lambda x: x[:-4])
    for condition in evoked_dict_right:
        evoked_dict_right[condition].rename_channels(lambda x: x[:-4])

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    color_dict = dict(HbO='#AA3377', HbR='b')
    styles_dict = dict(Rest=dict(linestyle='dashed'))

    #this is made of scales unification
    y_min = min(evoked_dict_left[f'{CONDITION}/HbO'].get_data().min(),
                evoked_dict_right[f'{CONDITION}/HbO'].get_data().min(),()) * 1.5*10**6
    y_max = max(evoked_dict_left[f'{CONDITION}/HbO'].get_data().max(),
                evoked_dict_right[f'{CONDITION}/HbO'].get_data().max(),()) * 1.5*10**6
    ylim = {'hbo':[y_min, y_max],
            'hbr':[y_min, y_max]}

    mne.viz.plot_compare_evokeds(evoked_dict_left,
                                            combine="mean",
                                            ci=0.95,
                                            colors=color_dict,
                                            styles=styles_dict,
                                            title=f'{CONDITION} and Rest trials LEFT hemisphere\nSubject {SUBJECT}',
                                            axes=axes[0],
                                            ylim=ylim,
                                            truncate_xaxis=False, 
                                            show=False
                                            ) 

    mne.viz.plot_compare_evokeds(evoked_dict_right,
                                            combine="mean",
                                            ci=0.95,
                                            colors=color_dict,
                                            styles=styles_dict,
                                            title=f'{CONDITION} and Rest trials RIGHT hemisphere\nSubject {SUBJECT}',
                                            axes=axes[1],
                                            ylim=ylim,
                                            truncate_xaxis=False, 
                                            show=False 
                                            )

    fig.savefig(rf'{dirs_to_save_stuff["haemo_folder_path"]}\{SUBJECT} {CONDITION} haemodynamic response.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types
    fig.clear()
    
    topomaps_plotter('hbo', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)
    topomaps_plotter('hbr', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)

et = time.time()

elapsed_time = et - start
print('Execution time:', str(elapsed_time), 'seconds')
