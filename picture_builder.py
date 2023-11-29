import os.path as op
import matplotlib.pyplot as plt
import logging
import mne
from mne import events_from_annotations

from ROI import different_hb, different_roi
from functions_fnirs import *
from meta import *
from file_scanning import *
from topomaps import topomaps_plotter

logging.basicConfig(filename="log_.txt", format="%(asctime)s %(message)s", filemode="w", level=logging.INFO)

splitting_slash = '/'
fnirs_dir = r"/mnt/diskus/fNIRS data ME_MI_TS_TI_SA"
subfolders = fast_scandir(fnirs_dir)


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
    smr_epochs.resample(SFREQ)
    rest_epochs.resample(SFREQ)
        
        
    curves_hb = 'hbo'
    
    ###EVOKEDS LEFT##    
    M1_evoked_SMR_left, M1_evoked_REST_left = make_evokeds_roi(
                                                        smr_epochs=smr_epochs, 
                                                        rest_epochs=rest_epochs,
                                                        pick=different_hb[curves_hb][0])
    S1_evoked_SMR_left, S1_evoked_REST_left = make_evokeds_roi(
                                                        smr_epochs=smr_epochs, 
                                                        rest_epochs=rest_epochs,
                                                        pick=different_hb[curves_hb][1])
    SMZ_evoked_SMR_left, SMZ_evoked_REST_left = make_evokeds_roi(
                                                        smr_epochs=smr_epochs, 
                                                        rest_epochs=rest_epochs,
                                                        pick=different_hb[curves_hb][2]
                                                        )
    ###EVOKEDS RIGHT###
    M1_evoked_SMR_right, M1_evoked_REST_right = make_evokeds_roi(
                                                        smr_epochs=smr_epochs, 
                                                        rest_epochs=rest_epochs,
                                                        pick=different_hb[curves_hb][3]
                                                        ) 
    S1_evoked_SMR_right, S1_evoked_REST_right = make_evokeds_roi(
                                                        smr_epochs=smr_epochs, 
                                                        rest_epochs=rest_epochs,
                                                        pick=different_hb[curves_hb][4]
                                                        )
    SMZ_evoked_SMR_right, SMZ_evoked_REST_right = make_evokeds_roi(
                                                        smr_epochs=smr_epochs, 
                                                        rest_epochs=rest_epochs,
                                                        pick=different_hb[curves_hb][5]
                                                        )
    
    M1_right_relation = relative_measure()
    S1_right_relation = relative_measure()
    SMZ_right_relation = relative_measure()
    M1_left_relation = relative_measure()
    S1_left_relation = relative_measure()
    SMZ_left_relation = relative_measure()
    


    for idx, item in enumerate(right_arrays):
        npy_path = op.join(DIRS_TO_SAVE_STUFF[f'haemo_{roi}_folder_path_np'], f'{SUBJECT}_{CONDITION}_{roi}_{list(right_arrays_od.keys())[idx]}_right.npy')
        np.save(npy_path, item)
    

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
    
    topomaps_plotter('hbo', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)
    topomaps_plotter('hbr', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)
    topomaps_plotter('hbt', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)
    topomaps_plotter('rel', smr_epochs=smr_epochs, rest_epochs=rest_epochs, SUBJECT=SUBJECT, CONDITION=CONDITION)

# et = time.time()

# elapsed_time = et - start
# print('Execution time:', str(elapsed_time), 'seconds')
