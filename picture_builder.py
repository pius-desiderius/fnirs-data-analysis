import os.path as op
import matplotlib.pyplot as plt
from itertools import compress
import time
import logging
import mne
from mne import events_from_annotations
from collections import OrderedDict

from ROI import different_roi
from functions_fnirs import *
from meta import *
from file_scanning import *
from topomaps import topomaps_plotter

start = time.time()
logging.basicConfig(filename="log_.txt", format="%(asctime)s %(message)s", filemode="w", level=logging.INFO)

splitting_slash = '/'
fnirs_dir = r"/mnt/diskus/fNIRS data ME_MI_TS_TI_SA"
subfolders = fast_scandir(fnirs_dir)
subj_names = sorted([(i.split('\\')[-1]) for i in subfolders if len(i.split(splitting_slash)[-1])==2])
recordings_names = sorted([i for i in subfolders if len(i.split(splitting_slash)[-1])!=2])

for items in DIRS_TO_SAVE_STUFF.values():
    os.makedirs(items, exist_ok=True)

#########################################################
for filename in recordings_names:
    print (filename)
#########################################################
    CONDITION = filename.split(splitting_slash)[-1].split('_')[-1]
    SUBJECT = filename.split(splitting_slash)[-1].split('_')[0]
    
    threshold = 1.3*10**-5
    raw_haemo, channels_to_interpolate = get_raw_haemo(filename)
    
    logging.info(f'{SUBJECT} {CONDITION} interpolated channels N={len(channels_to_interpolate)}: {channels_to_interpolate}')
    
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
                            baseline=BASELINE,
                            drop_epochs_flag=False
                            )
    smr_epochs.resample(1)
    rest_epochs.resample(1)
    
    for roi in different_roi.keys():
        
        print(roi)
        
        evoked_dict_left, evoked_dict_right = make_evokeds(
                                                            smr_epochs=smr_epochs, 
                                                            rest_epochs=rest_epochs,
                                                            roi_left_hbo=different_roi[roi][0],
                                                            roi_left_hbr=different_roi[roi][1],
                                                            roi_right_hbo=different_roi[roi][2],
                                                            roi_right_hbr=different_roi[roi][3],
                                                            condition=CONDITION
                                                            )
    
        
        evoked_info_hbo_right = evoked_dict_right[f'{CONDITION}/HbO'].info
        evoked_info_hbo_left = evoked_dict_left[f'{CONDITION}/HbO'].info

        
        target_right_hbo = evoked_dict_right[f'{CONDITION}/HbO'].get_data()
        target_right_hbr = evoked_dict_right[f'{CONDITION}/HbR'].get_data()
        target_right_hbt = hbt_total(target_right_hbr, target_right_hbo)
        
        rest_right_hbo = evoked_dict_right['Rest/HbO'].get_data()
        rest_right_hbr = evoked_dict_right['Rest/HbR'].get_data()
        rest_right_hbt = hbt_total(rest_right_hbr, rest_right_hbo)
        
        target_left_hbo = evoked_dict_left[f'{CONDITION}/HbO'].get_data()
        target_left_hbr = evoked_dict_left[f'{CONDITION}/HbR'].get_data()
        target_left_hbt = hbt_total(target_left_hbr, target_left_hbo)
        
        rest_left_hbo = evoked_dict_left['Rest/HbO'].get_data()
        rest_left_hbr = evoked_dict_left['Rest/HbR'].get_data()
        rest_left_hbt = hbt_total(rest_left_hbr, rest_left_hbo)
        
        
        target_right_hbo_relation = relative_measure(target_right_hbo)
        target_right_hbr_relation = relative_measure(target_right_hbr)
        target_right_hbt_relation = relative_measure(target_right_hbt)
        target_left_hbo_relation = relative_measure(target_left_hbo)
        target_left_hbr_relation = relative_measure(target_left_hbr)
        target_left_hbt_relation = relative_measure(target_left_hbt)
        
        rest_right_hbo_relation = relative_measure(rest_right_hbo)
        rest_right_hbr_relation = relative_measure(rest_right_hbr)
        rest_right_hbt_relation = relative_measure(rest_right_hbt)
        rest_left_hbo_relation = relative_measure(rest_left_hbo)
        rest_left_hbr_relation = relative_measure(rest_left_hbr)
        rest_left_hbt_relation = relative_measure(rest_left_hbt)


        
        hbt_evoked_dict_right = {
                            f'{CONDITION} hbt' : make_evoked_array(data=target_right_hbt, info=evoked_info_hbo_right),
                            'Rest hbt' : make_evoked_array(data=rest_right_hbt, info=evoked_info_hbo_right),
        }
        
        hbt_evoked_dict_left = { 'Rest hbt' : make_evoked_array(data=rest_left_hbt, info=evoked_info_hbo_left),
                            f'{CONDITION} hbt': make_evoked_array(data=target_left_hbt, info=evoked_info_hbo_left),
        }
        
        relation_dict_right = {
                            f'{CONDITION} hbo relation' : make_evoked_array(data=target_right_hbo_relation, info=evoked_info_hbo_right),
                            f'{CONDITION} hbr relation' :make_evoked_array(data=target_right_hbr_relation, info=evoked_info_hbo_right),
                            f'{CONDITION} hbt relation' :make_evoked_array(data=target_right_hbt_relation, info=evoked_info_hbo_right),
                            'Rest hbo relation' : make_evoked_array(data=rest_right_hbo_relation, info=evoked_info_hbo_right),
                            'Rest hbr relation' : make_evoked_array(data=rest_right_hbr_relation, info=evoked_info_hbo_right),
                            'Rest hbt relation' : make_evoked_array(data=rest_right_hbt_relation, info=evoked_info_hbo_right),
                            
        }
        
        relation_dict_left = {
                            f'{CONDITION} hbo relation' : make_evoked_array(data=target_left_hbo_relation, info=evoked_info_hbo_left),
                            f'{CONDITION} hbr relation' : make_evoked_array(data=target_left_hbr_relation, info=evoked_info_hbo_left),
                            f'{CONDITION} hbt relation' : make_evoked_array(data=target_left_hbt_relation, info=evoked_info_hbo_left),
                            'Rest hbo relation' : make_evoked_array(data=rest_left_hbo_relation, info=evoked_info_hbo_left),
                            'Rest hbr relation' : make_evoked_array(data=rest_left_hbr_relation, info=evoked_info_hbo_left),
                            'Rest hbt relation' : make_evoked_array(data=rest_left_hbt_relation, info=evoked_info_hbo_left),
                            
        }
        
        right_arrays_od = OrderedDict(
                        hbo=[target_right_hbo, rest_right_hbo],
                        hbr=[target_right_hbr, rest_right_hbr],
                        hbt=[target_right_hbt, rest_right_hbt],
                        rel_hbo=[target_right_hbo_relation, 
                                 rest_right_hbo_relation
                        ],
                        rel_hbr=[target_right_hbr_relation, 
                                 rest_right_hbr_relation
                                 ],
                        rel_hbt=[target_right_hbt_relation, 
                                 rest_right_hbt_relation
                                 ])
        right_arrays = [
                        np.stack(arrays=[right_arrays_od['hbo']]),
                        np.stack(arrays=[right_arrays_od['hbr']]),
                        np.stack(arrays=[right_arrays_od['hbt']]),
                        np.stack(arrays=[right_arrays_od['rel_hbo']]),
                        np.stack(arrays=[right_arrays_od['rel_hbr']]),
                        np.stack(arrays=[right_arrays_od['rel_hbt']]),
        ]
        
        for idx, item in enumerate(right_arrays):
            npy_path = op.join(DIRS_TO_SAVE_STUFF[f'haemo_{roi}_folder_path_np'], f'{SUBJECT}_{CONDITION}_{roi}_{list(right_arrays_od.keys())[idx]}_right.npy')
            np.save(npy_path, item)
        
        
        left_arrays_od = OrderedDict(
                        hbo=[target_left_hbo, rest_left_hbo],
                        hbr=[target_left_hbr, rest_left_hbr],
                        hbt=[target_left_hbt, rest_left_hbt],
                        rel_hbo=[target_left_hbo_relation, 
                                 rest_left_hbo_relation
                                 ],
                        rel_hbr=[target_left_hbr_relation, 
                                 rest_left_hbr_relation
                                 ],
                        rel_hbt=[target_left_hbt_relation, 
                                 rest_left_hbt_relation
                                 ])
        
        left_arrays = [
                        np.stack(arrays=[left_arrays_od['hbo']]),
                        np.stack(arrays=[left_arrays_od['hbr']]),
                        np.stack(arrays=[left_arrays_od['hbt']]),
                        np.stack(arrays=[left_arrays_od['rel_hbo']]),
                        np.stack(arrays=[left_arrays_od['rel_hbr']]),
                        np.stack(arrays=[left_arrays_od['rel_hbt']]),
        ]
        

        for idx, item in enumerate(left_arrays):
            npy_path = op.join(DIRS_TO_SAVE_STUFF[f'haemo_{roi}_folder_path_np'], f'{SUBJECT}_{CONDITION}_{roi}_{list(left_arrays_od.keys())[idx]} left.npy')
            np.save(npy_path, item)
            
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
        maximal = max(np.abs(y_min), np.abs(y_max))
        ylim = {'hbo':[-1*maximal, maximal],
                'hbr':[-1*maximal, maximal]}

        fig, axes = plt.subplots(1, 2, figsize=(20, 12))
        mne.viz.plot_compare_evokeds(evoked_dict_left,
                                                combine="mean",
                                                ci=True,
                                                colors=color_dict,
                                                styles=styles_dict,
                                                title=f'{CONDITION} and Rest trials LEFT hemisphere\nSubject {SUBJECT} ROI {roi}',
                                                axes=axes[0],
                                                ylim=ylim,
                                                truncate_xaxis=False, 
                                                show=False,
                                                show_sensors=True
                                                ) 
        mne.viz.plot_compare_evokeds(evoked_dict_right,
                                                combine="mean",
                                                ci=True,
                                                colors=color_dict,
                                                styles=styles_dict,
                                                title=f'{CONDITION} and Rest trials RIGHT hemisphere\nSubject {SUBJECT} ROI {roi}',
                                                axes=axes[1],
                                                ylim=ylim,
                                                truncate_xaxis=False, 
                                                show=False,
                                                show_sensors=True 
                                                )
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"haemo_{roi}_folder_path"]}/{SUBJECT} {CONDITION} haemodynamic response.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types

        fig.clear()
        
        color_dict = {'Rest hbt':'r', f'{CONDITION} hbt':'r'}
        styles_dict = {'Rest hbt':dict(linestyle='dashed')}
        fig, axes = plt.subplots(1, 2, figsize=(20, 12))
        mne.viz.plot_compare_evokeds(hbt_evoked_dict_left,
                                                combine="mean",
                                                ci=True,
                                                colors=color_dict,
                                                styles=styles_dict,
                                                title=f'{CONDITION} and Rest trials LEFT hemisphere HbT \nSubject {SUBJECT} ROI {roi}',
                                                axes=axes[0],
                                                ylim=ylim,
                                                truncate_xaxis=False, 
                                                show=False,
                                                show_sensors=True
                                                ) 

        mne.viz.plot_compare_evokeds(hbt_evoked_dict_right,
                                                combine="mean",
                                                ci=True,
                                                colors=color_dict,
                                                styles=styles_dict,
                                                title=f'{CONDITION} and Rest trials RIGHT hemisphere HbT \nSubject {SUBJECT} ROI {roi}',
                                                axes=axes[1],
                                                ylim=ylim,
                                                truncate_xaxis=False, 
                                                show=False,
                                                show_sensors=True 
                                                )
        
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"haemo_{roi}_folder_path"]}/{SUBJECT} {CONDITION} haemodynamic response HbT.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types

        fig.clear()
        
        
        color_dict = {f'{CONDITION} hbo relation':'#AA3377', 
                      f'{CONDITION} hbr relation':'blue',  
                      f'{CONDITION} hbt relation':'black',
                      f'Rest hbo relation':'#AA3377', 
                      f'Rest hbr relation':'blue',  
                      f'Rest hbt relation':'black',
                      }
        styles_dict = {
                        f'Rest hbo relation':dict(linestyle='dashed'),
                      f'Rest hbr relation':dict(linestyle='dashed'), 
                      f'Rest hbt relation':dict(linestyle='dashed'),
                       }
        y_min = min(relation_dict_left[f'{CONDITION} hbo relation'].get_data().min(),
                    relation_dict_right[f'{CONDITION} hbo relation'].get_data().min(),
                    relation_dict_left[f'Rest hbo relation'].get_data().min(),
                    relation_dict_right[f'Rest hbo relation'].get_data().min()) 
        y_max = max(relation_dict_left[f'{CONDITION} hbo relation'].get_data().max(),
                    relation_dict_right[f'{CONDITION} hbo relation'].get_data().max(),
                    relation_dict_left[f'Rest hbo relation'].get_data().min(),
                    relation_dict_right[f'Rest hbo relation'].get_data().min(),
                    )
        maximal = max(np.abs(y_min), np.abs(y_max))
        ylim = [-1*maximal*10e5, maximal*10e5]      
        ylims = {     
                #  
                    #  f'{CONDITION} hbo relation':ylim,
                    #   f'{CONDITION} hbr relation':ylim, 
                    #   f'{CONDITION} hbt relation':ylim,
                    #   f'Rest hbo relation':ylim,
                    #   f'Rest hbr relation':ylim,
                    #   f'Rest hbt relation':ylim,
                      'hbo':ylim,
                      'hbr':ylim,

                      }
        
        print(relation_dict_left[f'{CONDITION} hbo relation'].get_data()[0])
        
        fig, axes = plt.subplots(1, 2, figsize=(20, 12))
        
        mne.viz.plot_compare_evokeds(relation_dict_left,
                                                combine="mean",
                                                ci=True,
                                                colors=color_dict,
                                                styles=styles_dict,
                                                title=f'{CONDITION} relation between task and rest LEFT in subject {SUBJECT} ROI {roi}',
                                                axes=axes[0],
                                                ylim=ylims,
                                                truncate_xaxis=False, 
                                                show=False,
                                                show_sensors=True
                                                ) 

        mne.viz.plot_compare_evokeds(relation_dict_right,
                                                combine="mean",
                                                ci=True,
                                                colors=color_dict,
                                                styles=styles_dict,
                                                title=f'{CONDITION} relation between task and rest RIGHT in subject {SUBJECT} ROI {roi}',
                                                axes=axes[1],
                                                ylim=ylims,
                                                truncate_xaxis=False, 
                                                show=False,
                                                show_sensors=True 
                                                )
        
        fig.savefig(rf'{DIRS_TO_SAVE_STUFF[f"haemo_{roi}_folder_path"]}/{SUBJECT} {CONDITION} haemodynamic response relations.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types

        fig.clear()

    
    topomaps_plotter('hbo', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)
    topomaps_plotter('hbr', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)
    topomaps_plotter('hbt', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)
    topomaps_plotter('rel', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)

# et = time.time()

# elapsed_time = et - start
# print('Execution time:', str(elapsed_time), 'seconds')
