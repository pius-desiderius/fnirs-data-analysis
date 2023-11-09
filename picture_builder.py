import os.path as op
import matplotlib.pyplot as plt
from itertools import compress
import time
import logging
import mne
from mne import events_from_annotations
from collections import OrderedDict

from functions_fnirs import *
from meta import *
from file_scanning import *

start = time.time()
logging.basicConfig(filename="log_one_channel.txt", format="%(asctime)s %(message)s", filemode="w", level=logging.INFO)

splitting_slash = '\\'
fnirs_dir = r"C:\Users\Admin\Desktop\IMAGERY-FNIRS"
subfolders = fast_scandir(fnirs_dir)
subj_names = sorted([(i.split('\\')[-1]) for i in subfolders if len(i.split(splitting_slash)[-1])==2])
recordings_names = sorted([i for i in subfolders if len(i.split(splitting_slash)[-1])!=2])

print(recordings_names)
# for items in DIRS_TO_SAVE_STUFF.values():
#     os.makedirs(items, exist_ok=True)

#########################################################
for filename in recordings_names[0:2]:
    print (filename)
#########################################################
    CONDITION = filename.split(splitting_slash)[-1].split('_')[-1]
    SUBJECT = filename.split(splitting_slash)[-1].split('_')[0]
    
    threshold = 1.3*10**-5
    raw_haemo = get_raw_haemo(filename)
    
    # logging.info(f'{SUBJECT} {CONDITION} interpolated channels N={len(channels_to_interpolate)}: {channels_to_interpolate}')
    
    chnames = raw_haemo.ch_names

    ids_target= 'SMR'
    ids_rest = 'REST'
    
    events, ids = events_from_annotations(raw_haemo)
    ids[ids_target] = 1
    ids[ids_rest] = 2
    
        
    ids_to_pop = IDS_TO_POP
    for i in ids_to_pop:
        popper(ids, i)

    smr_epochs, rest_epochs = clean_epochs( 
                            raw_haemo, 
                            events=events, 
                            ids=ids, 
                            tmin=TMIN, 
                            tmax=TMAX, 
                            baseline=BASELINE 
                            )
    #reassign channels to pick
    picks_hbo_left, picks_hbr_left = C3_chans_of_interest_hbo, C3_chans_of_interest_hbr
    picks_hbo_right, picks_hbr_right = C4_chans_of_interest_hbo, C4_chans_of_interest_hbr

    #save epochs with selected channels
    smr_epochs_left = smr_epochs.copy().pick_channels(picks_hbo_left + picks_hbr_left)
    smr_epochs_right = smr_epochs.copy().pick_channels(picks_hbo_right + picks_hbr_right)
    rest_epochs_left = rest_epochs.copy().pick_channels(picks_hbo_left + picks_hbr_left)
    rest_epochs_right = rest_epochs.copy().pick_channels(picks_hbo_right + picks_hbr_right)

    evoked_dict_left = {f'{CONDITION}/HbO': smr_epochs_left.copy().average(picks=picks_hbo_left),
                f'{CONDITION}/HbR': smr_epochs_left.copy().average(picks=picks_hbr_left),
                'Rest/HbO': rest_epochs_left.copy().average(picks=picks_hbo_left),
                'Rest/HbR': rest_epochs_left.copy().average(picks=picks_hbr_left)}

    evoked_dict_right = {f'{CONDITION}/HbO': smr_epochs_right.copy().average(picks=picks_hbo_right),
                f'{CONDITION}/HbR': smr_epochs_right.copy().average(picks=picks_hbr_right),
                'Rest/HbO': rest_epochs_right.copy().average(picks=picks_hbo_right),
                'Rest/HbR': rest_epochs_right.copy().average(picks=picks_hbr_right)}
    
    evoked_info_hbo = smr_epochs_left.copy().average(picks=picks_hbo_left).info
    evoked_info_hbr = smr_epochs_left.copy().average(picks=picks_hbr_left).info

    # evoked_dict_left = {f'{CONDITION}/HbO': smr_epochs_left.copy().get_data().mean(axis=[0, 1]),
    #             f'{CONDITION}/HbR': smr_epochs_left.copy().get_data().mean(axis=[0, 1]),
    #             'Rest/HbO': rest_epochs_left.copy().get_data().mean(axis=[0, 1]),
    #             'Rest/HbR': rest_epochs_left.copy().get_data().mean(axis=[0, 1])}

    # evoked_dict_right = {f'{CONDITION}/HbO': smr_epochs_right.copy().get_data().mean(axis=[0, 1]),
    #             f'{CONDITION}/HbR': smr_epochs_right.copy().get_data().mean(axis=[0, 1]),
    #             'Rest/HbO': rest_epochs_right.copy().get_data().mean(axis=[0, 1]),
    #             'Rest/HbR': rest_epochs_right.copy().get_data().mean(axis=[0, 1])}
    

    target_right_hbo = evoked_dict_right[f'{CONDITION}/HbO'].get_data()
    target_right_hbr = evoked_dict_right[f'{CONDITION}/HbR'].get_data()
    target_right_hbt = hbt_total(target_right_hbr, target_right_hbo)
    target_right_oxy = oxy_level(target_right_hbo, target_right_hbr)
    
    rest_right_hbo = evoked_dict_right['Rest/HbO'].get_data()
    rest_right_hbr = evoked_dict_right['Rest/HbR'].get_data()
    rest_right_hbt = hbt_total(rest_right_hbr, rest_right_hbo)
    rest_right_oxy = oxy_level(rest_right_hbo, rest_right_hbr)
    
    target_left_hbo = evoked_dict_left[f'{CONDITION}/HbO'].get_data()
    target_left_hbr = evoked_dict_left[f'{CONDITION}/HbR'].get_data()
    target_left_hbt = hbt_total(target_left_hbr, target_left_hbo)
    target_left_oxy = oxy_level(target_left_hbo, target_left_hbr)
    
    rest_left_hbo = evoked_dict_left['Rest/HbO'].get_data()
    rest_left_hbr = evoked_dict_left['Rest/HbR'].get_data()
    rest_left_hbt = hbt_total(rest_left_hbr, rest_left_hbo)
    rest_left_oxy = oxy_level(rest_left_hbo, rest_left_hbr)



    def make_evoked_array(data, info):
        return mne.EvokedArray(data=data, 
                                info=info, 
                                tmin=0.0, 
                                nave=1, 
                                kind='average', 
                                baseline=(0,0),
                                verbose=None)
        
    hbt_evoked_dict_right = {
                        f'{CONDITION} hbt' : make_evoked_array(data=target_right_hbt, info=evoked_info_hbo),
                        'Rest hbt' : make_evoked_array(data=rest_right_hbt, info=evoked_info_hbo),
    }
    
    hbt_evoked_dict_left = { 'Rest hbt' : make_evoked_array(data=rest_left_hbt, info=evoked_info_hbo),
                         f'{CONDITION} hbt': make_evoked_array(data=target_left_hbt, info=evoked_info_hbo),
    }
    oxy_evoked_dict_right= {
                            f'{CONDITION} oxy' : make_evoked_array(data=target_right_oxy, info=evoked_info_hbo),
                            'Rest oxy' : make_evoked_array(data=rest_right_oxy, info=evoked_info_hbo),
    }
    oxy_evoked_dict_left = {             
                            'Rest oxy' : make_evoked_array(data=rest_left_oxy, info=evoked_info_hbo),
                            f'{CONDITION} oxy': make_evoked_array(data=target_left_oxy, info=evoked_info_hbo),
          }
    
    right_arrays_od = OrderedDict(
                    hbo=[target_right_hbo, rest_right_hbo],
                    hbr=[target_right_hbr, rest_right_hbr],
                    hbt=[target_right_hbt, rest_right_hbt],
                    oxy=[target_right_oxy, rest_right_oxy]
                    )
    right_arrays = [
                    np.stack(arrays=[right_arrays_od['hbo']]),
                    np.stack(arrays=[right_arrays_od['hbr']]),
                    np.stack(arrays=[right_arrays_od['hbt']]),
                    np.stack(arrays=[right_arrays_od['oxy']])
    ]

    for idx, item in enumerate(right_arrays):
        npy_path = op.join(DIRS_TO_SAVE_STUFF['haemo_folder_path_np'], f'{SUBJECT} {CONDITION} {list(right_arrays_od.keys())[idx]} right.npy')
        # np.save(npy_path, item)
    
    
    left_arrays_od = OrderedDict(
                    hbo=[target_left_hbo, rest_left_hbo],
                    hbr=[target_left_hbr, rest_left_hbr],
                    hbt=[target_left_hbt, rest_left_hbt],
                    oxy=[target_left_oxy, rest_left_oxy]
                    )
     
    left_arrays = [
                    np.stack(arrays=[left_arrays_od['hbo']]),
                    np.stack(arrays=[left_arrays_od['hbr']]),
                    np.stack(arrays=[left_arrays_od['hbt']]),
                    np.stack(arrays=[left_arrays_od['oxy']])
    ]

    for idx, item in enumerate(left_arrays):
        npy_path = op.join(DIRS_TO_SAVE_STUFF['haemo_folder_path_np'], f'{SUBJECT} {CONDITION} {list(left_arrays_od.keys())[idx]} left.npy')
        # np.save(npy_path, item)
        
    for condition in evoked_dict_left:
        evoked_dict_left[condition].rename_channels(lambda x: x[:-4])
    for condition in evoked_dict_right:
        evoked_dict_right[condition].rename_channels(lambda x: x[:-4])

    color_dict = dict(HbO='#AA3377', HbR='b')
    styles_dict = dict(Rest=dict(linestyle='dashed'))

    #this is made of scales unification
    y_min = min(evoked_dict_left[f'{CONDITION}/HbO'].get_data().min(),
                evoked_dict_right[f'{CONDITION}/HbO'].get_data().min(),()) * 1.5*10**6
    y_max = max(evoked_dict_left[f'{CONDITION}/HbO'].get_data().max(),
                evoked_dict_right[f'{CONDITION}/HbO'].get_data().max(),()) * 1.5*10**6
    ylim = {'hbo':[y_min, y_max],
            'hbr':[y_min, y_max]}

    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
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
    fig.clear()
    color_dict = {'Rest hbt':'r', f'{CONDITION} hbt':'r'}
    styles_dict = {'Rest hbt':dict(linestyle='dashed')}
    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
    mne.viz.plot_compare_evokeds(hbt_evoked_dict_left,
                                            combine="mean",
                                            ci=0.95,
                                            colors=color_dict,
                                            styles=styles_dict,
                                            title=f'{CONDITION} and Rest trials LEFT hemisphere HbT \nSubject {SUBJECT}',
                                            axes=axes[0],
                                            ylim=ylim,
                                            truncate_xaxis=False, 
                                            show=False
                                            ) 

    mne.viz.plot_compare_evokeds(hbt_evoked_dict_right,
                                            combine="mean",
                                            ci=0.95,
                                            colors=color_dict,
                                            styles=styles_dict,
                                            title=f'{CONDITION} and Rest trials RIGHT hemisphere HbT \nSubject {SUBJECT}',
                                            axes=axes[1],
                                            ylim=ylim,
                                            truncate_xaxis=False, 
                                            show=False 
                                            )
    fig.clear()
    color_dict = {'Rest oxy':'black', f'{CONDITION} oxy':'black'}
    styles_dict = {'Rest oxy':dict(linestyle='dashed')}
    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
    mne.viz.plot_compare_evokeds(oxy_evoked_dict_left,
                                            combine="mean",
                                            ci=0.95,
                                            colors=color_dict,
                                            styles=styles_dict,
                                            title=f'{CONDITION} and Rest trials LEFT hemisphere Oxy \nSubject {SUBJECT}',
                                            axes=axes[0],
                                            ylim=ylim,
                                            truncate_xaxis=False, 
                                            show=False
                                            ) 

    mne.viz.plot_compare_evokeds(oxy_evoked_dict_right,
                                            combine="mean",
                                            ci=0.95,
                                            colors=color_dict,
                                            styles=styles_dict,
                                            title=f'{CONDITION} and Rest trials RIGHT hemisphere Oxy \nSubject {SUBJECT}',
                                            axes=axes[1],
                                            ylim=ylim,
                                            truncate_xaxis=False, 
                                            show=False 
                                            )
    fig.clear()



    # fig.savefig(rf'{dirs_to_save_stuff["haemo_folder_path"]}\{SUBJECT} {CONDITION} haemodynamic response.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types
    # fig.clear()
    
    # topomaps_plotter('hbo', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)
    # topomaps_plotter('hbr', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)

# et = time.time()

# elapsed_time = et - start
# print('Execution time:', str(elapsed_time), 'seconds')
