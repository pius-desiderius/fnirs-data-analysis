import numpy as np
import matplotlib.pyplot as plt
import mne
import mne_nirs
import json
import scipy.signal as sg
from mne.preprocessing.nirs import optical_density, beer_lambert_law
from mne_nirs.signal_enhancement import enhance_negative_correlation

from mne.preprocessing.nirs import (optical_density,
                                    temporal_derivative_distribution_repair)
import pingouin as pg
from mne import events_from_annotations
from meta import *
from ROI import *
from filter_params import FILTER_DICT
from file_scanning import *
import scipy.stats as st

info_hbo_total = mne.io.read_info('/mnt/diskus/infos/info_hbo_total_info.fif')

def make_evokeds_roi(smr_epochs, rest_epochs, pick, averaging_method='median', info=info_hbo_total, general_use=True):
    pick = get_channel_indices(pick, info)
    smr_data, rest_data = epochs_transfer(smr_epochs, rest_epochs, 
                                          picks=pick, info=info, 
                                          time_limits=[7, 14])

    
    smr_data, rest_data = smr_data[:, pick, :], rest_data[:, pick, :]
    if general_use:
        if averaging_method == 'mean':
            evoked_smr = smr_data.mean(axis=0)
            evoked_rest = rest_data.mean(axis=0)
        elif averaging_method == 'median':
            evoked_smr = np.median(smr_data, axis=0)
            evoked_rest = np.median(rest_data, axis=0)
    else:
        evoked_smr, evoked_rest = smr_data, rest_data
     
    return evoked_smr, evoked_rest


def point_to_point_norm(smr_epochs, rest_epochs, pick, method):
    smr_roi_epochs = smr_epochs.copy().pick(pick)
    smr_roi_epochs_info = smr_roi_epochs.info
    rest_roi_epochs = rest_epochs.copy().pick(pick)
    
    if averaging_method == 'mean':
        evoked_rest = np.mean(rest_roi_epochs.get_data(), axis=0)
        normalized_smr = smr_roi_epochs.get_data() / evoked_rest
        normalized_smr = np.mean(normalized_smr, axis=0)
    elif averaging_method == 'median':
        evoked_rest = np.median(rest_roi_epochs.get_data(), axis=0)
        normalized_smr = smr_roi_epochs.get_data() / evoked_rest
        normalized_smr = np.median(normalized_smr, axis=0)
    return normalized_smr, smr_roi_epochs_info

def median_in_rest(smr_epochs, rest_epochs, pick, method):
    smr_roi_epochs = smr_epochs.copy().pick(pick)
    smr_roi_epochs_info = smr_roi_epochs.info
    rest_roi_epochs = rest_epochs.copy().pick(pick)
    
    if averaging_method == 'mean':
        evoked_rest = np.mean(rest_roi_epochs.get_data(), axis=0)
        evoked_rest = np.median(evoked_rest[:, 1*SFREQ:13*SFREQ], axis=1)
        normalized_smr = smr_roi_epochs.get_data() / evoked_rest
        normalized_smr = np.mean(normalized_smr, axis=0)
    elif averaging_method == 'median':
        evoked_rest = np.median(rest_roi_epochs.get_data(), axis=0)
        evoked_rest = np.median(evoked_rest[:, 1*SFREQ:13*SFREQ], axis=1)
        normalized_smr = smr_roi_epochs.get_data() / evoked_rest
        normalized_smr = np.median(normalized_smr, axis=0)
    return normalized_smr, smr_roi_epochs_info



def epochs_rejector(epochs, ch_pick, info, criterion='maximum',
                    sfreq=SFREQ, 
                    time_limits = (5, 12),
                    lower=0.10, upper=0.90): 
    time_limits = (time_limits[0]*sfreq, time_limits[1]*sfreq)
    picks = get_channel_indices(ch_pick, info)

    epochs = epochs[:, picks, :]
    epochs_data = epochs[:, :, time_limits[0]:time_limits[1]]

    if criterion == 'median':

        median = np.median(epochs_data, axis=1)
        median = np.median(median, axis=1)
        lower_quantile = np.quantile(median, lower)
        upper_quantile = np.quantile(median, upper)

        reject_bool_negative = median < lower_quantile
        reject_bool_positive = median > upper_quantile

        reject_bool = np.logical_or( 
                                    reject_bool_negative, 
                                    reject_bool_positive)
    if criterion == 'maximum':

        maximum = np.max(epochs_data, axis=1)
        maximum = np.max(maximum, axis=1)
        lower_quantile = np.quantile(maximum, lower)
        upper_quantile = np.quantile(maximum, upper)

        reject_bool_negative = maximum < lower_quantile
        reject_bool_positive = maximum > upper_quantile

        reject_bool = np.logical_or( 
                                    reject_bool_negative, 
                                    reject_bool_positive)

    if criterion == 'minimum':

        minimum = np.min(epochs_data, axis=1)
        minimum = np.min(minimum, axis=1)
        lower_quantile = np.quantile(minimum, lower)
        upper_quantile = np.quantile(minimum, upper)

        reject_bool_negative = minimum < lower_quantile
        reject_bool_positive = minimum > upper_quantile

        reject_bool = np.logical_or( 
                                    reject_bool_negative, 
                                    reject_bool_positive)
    return reject_bool



def rolling_mean_filter(data, initial_mean=0, weight=0.75):
    mean = initial_mean
    container = np.zeros(data.shape)
    i = 0
    while i < len(data)-1:
        value = data[i]
        value_next = data[i+1]
        new_mean = (mean + value*weight + value*weight) / 3 
        container[i] = new_mean
        mean = new_mean
        i+=1
    return container

def detrender(data):
    
    return sg.detrend(data, axis=-1)

def get_epochs(filename, TMIN, TMAX, BASELINE, SFREQ):

    raw_intensity = mne.io.read_raw_nirx(filename, verbose=False, preload=True)
    raw_od = optical_density(raw_intensity) #from row wavelength data
    raw_od.apply_function(detrender, picks=raw_od.ch_names)
    raw_od_shorts = mne_nirs.channels.get_short_channels(raw_od)
    raw_od.drop_channels(DROP_CHANS) #we had a non-existent channel
    raw_od = raw_od.filter(**FILTER_DICT)
    raw_od = mne_nirs.signal_enhancement.short_channel_regression(raw_od)
    raw_od = mne_nirs.channels.get_long_channels(raw_od)
    raw_od = temporal_derivative_distribution_repair(raw_od)

    raw_od_unfiltered = raw_od.copy() #repairs movement artifacts

    # ## BAD CHANNELS ###
    # channel_std = np.abs(np.std(raw_od.copy().pick([i for i in raw_od.ch_names if '760' in i]).get_data(), 
    #                     axis=(1)))
    # # print(channel_std)
    # biggest_indices = np.argpartition(channel_std, -20)[-20:]
    # smallest_indices = np.argpartition(channel_std,  5)[:5]
    # smallest_indices_list = smallest_indices.tolist()
    # biggest_indices_list = biggest_indices.tolist()
    # deviant_channels_idx = biggest_indices_list + smallest_indices_list

    # bad_channels_hbo = [raw_od.copy().pick([i for i in raw_od.ch_names if '760' in i]).ch_names[i]
    #             for i in deviant_channels_idx]
    # bad_channels_hbr = [i.replace('760', '850') for i in bad_channels_hbo]
    # bad_channels = bad_channels_hbo + bad_channels_hbr
    # raw_od.info['bads'] = bad_channels
    # raw_od.interpolate_bads()

        
    # raw_od.apply_function(rolling_mean_filter, picks=raw_od.ch_names)


    raw_haemo = beer_lambert_law(raw_od, ppf=0.1) #from wavelength to HbO\HbR
    raw_haemo = enhance_negative_correlation(raw_haemo)
    # raw_haemo.info['bads'] = bad_all
    # raw_haemo.interpolate_bads()
    ######################################
    ids_target= 'SMR'
    ids_rest = 'REST'

    events_dir = '/mnt/diskus/events_for_fnirs'
    events = np.load(f'{events_dir}/{filename[-5:]}.npy').astype(int)
    ids = dict()

    # events, ids = events_from_annotations(raw_haemo)
    ids[ids_target] = 1
    ids[ids_rest] = 2

    # IDS_TO_POP = ["2.0", "33.0", "1.0", "2", "1", "33"]
    # ids_to_pop = IDS_TO_POP
    # for i in ids_to_pop:
    #     popper(ids, i)

    epochs = mne.Epochs(
                        raw=raw_haemo,
                        events=events,
                        event_id=ids,
                        baseline=BASELINE,
                        tmin=TMIN,
                        tmax=TMAX,
                        preload=True,
                        verbose=False,
                        # picks=picks
                    )
    epochs.resample(SFREQ)
    info_left_smz = epochs.copy().pick(different_roi['SMZ'][0])
    info_right_smz = epochs.copy().pick(different_roi['SMZ'][2])
    info_hbo_total = epochs.copy().pick_types(fnirs='hbo').info
    info_hbr_total = epochs.copy().pick_types(fnirs='hbr').info
    epochs.pick(['hbo'])
    
    rest_epochs = epochs['REST']
    smr_epochs = epochs['SMR']
    
    data = np.abs(smr_epochs.get_data().mean(axis=(0, 2))) + np.abs(rest_epochs.get_data().mean(axis=(0, 2)))
    indices = np.argpartition(data, -10)[-10:]

    bad_channels_hbo = [raw_haemo.copy().pick([i for i in raw_haemo.ch_names if 'hbo' in i]).ch_names[i]
                for i in indices]
    bad_channels_hbo = list(set(bad_channels_hbo+blue_dot)-set(SMZ_LEFT_ROI_HBO))
    bad_channels_hbr = [i.replace('hbo', 'hbr') for i in bad_channels_hbo]
    bad_channels = bad_channels_hbo + bad_channels_hbr
    raw_haemo.info['bads'] = bad_channels
    raw_haemo.interpolate_bads()
    
    
    epochs = mne.Epochs(
                        raw=raw_haemo,
                        events=events,
                        event_id=ids,
                        baseline=BASELINE,
                        tmin=TMIN,
                        tmax=TMAX,
                        preload=True,
                        verbose=False,
                        # picks=picks
                    )
    epochs.resample(SFREQ)
    epochs.pick(['hbo'])
    
    rest_epochs = epochs['REST']
    smr_epochs = epochs['SMR']
    
    
    
    
    return epochs, smr_epochs, rest_epochs, info_hbo_total, info_hbr_total, info_left_smz, info_right_smz, 'peeps'


# def relative_measure(arr_target, arr_rest, start=2, end=14, SFREQ=2):
    # mean_arr_rest = np.median(arr_rest, axis=0)
    # relation = arr_target - mean_arr_rest
    # return np.median(relation, axis=0)

def relative_measure(arr_target, arr_rest, start=2, end=14, SFREQ=2):
    mean_arr_rest = np.mean(arr_rest, axis=0)
    relation = arr_target - mean_arr_rest
    return relation

# def relative_measure_topo(arr_target, arr_rest, start=2, end=14, SFREQ=2):
#     a_rest = np.median(arr_rest[start*SFREQ:end*SFREQ])
#     relation = (arr_target - a_rest) / np.abs(a_rest) * 100
#     return relation
    
def mean_rest_epoch(arr_rest, start=2, end=14, SFREQ=2):
    a_rest = np.median(arr_rest[start*SFREQ:end*SFREQ])
    return a_rest


def set_axis_properties(ax, ylims, tlims, title,
                        xlabel='Time, s', 
                        ylabel='Hb concentration, Δ μM\L',  
                        linewidth=1.5, 
                        fontsize=14, 
                        title_size=18,
                        legend_flag=True):
    
    ax.set_xlim(tlims[0], tlims[1])
    ax.set_ylim(ylims[0], ylims[1])

    # Set the x and y labels
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_ylabel(ylabel, fontsize=fontsize)

    # Set the tick parameters
    ax.tick_params(axis='x', labelsize=fontsize)
    ax.tick_params(axis='y', labelsize=fontsize)

    ax.xaxis.set_tick_params(width=linewidth)
    ax.yaxis.set_tick_params(width=linewidth)
    for i in ax.spines.values():
       i.set_linewidth(linewidth)

    ax.set_title(title, fontsize=title_size, loc='center')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.axvline(x=0, color='black', linestyle='--', linewidth=linewidth)
    ax.axhline(y=0, color='black', linewidth=linewidth)
    
    if legend_flag:
        ax.legend(loc='lower center')
        
        
def filler_between(ax, ylims, alpha=0.2):

    return ax.fill_between( [0, 4], 
                                ylims[0], 
                                ylims[1], 
                                color='#576767', 
                                alpha=alpha, 
                                label='Task duration')
    
def get_top_channels_mask(arr, info, top_n=10):
    top_idx = np.argpartition(arr, 
                                    -1*top_n)[-1*top_n:]
    mask = np.zeros(arr.shape[0], dtype=bool)
    mask[top_idx] = True
    top_values = arr[top_idx]
    names_dict = {info['ch_names'][int(top_idx[idx])]:top_values[idx] for idx in range(len(top_idx))}
    return mask, names_dict


def norm_minmax(arr, maximum, minimum):
    
    normalized_arr = (arr - minimum) / (maximum - minimum)
    return normalized_arr

def minmax(arr):
    maximum = np.max(arr)
    minimum = np.min(arr)
    
    return maximum, minimum
    
    
def subject_norms_getter(filename):
        epochs, smr_epochs, rest_epochs, info_hbo_total, info_hbr_total, \
        info_left_smz, info_right_smz, bad_channels = get_epochs(filename, TMIN, TMAX, BASELINE, SFREQ)
        smr_epochs = smr_epochs.get_data()
        rest_epochs = rest_epochs.get_data()
        
        smr_epochs, rest_epochs = epochs_transfer(smr_epochs, rest_epochs, 
                                                  time_limits=(7, 14), 
                                                  picks=SMZ_LEFT_ROI_HBO,
                                                  info=info_hbo_total)

        
        bool_mask_smr = epochs_rejector(epochs=smr_epochs, criterion='minimum', info=info_hbo_total,
                                        ch_pick=SMZ_LEFT_ROI_HBO, lower=0.0, upper=0.75, time_limits=(5, 13))
        bool_mask_rest = epochs_rejector(epochs=rest_epochs, criterion='maximum', info=info_hbo_total,
                                         ch_pick=SMZ_LEFT_ROI_HBO, lower=0.0, upper=0.75, time_limits=(5,13))
        
        smr_epochs, rest_epochs = smr_epochs[~bool_mask_smr], rest_epochs[~bool_mask_rest]
        max_values, min_values = [], []
        
        for i in range(6):
                evoked_smr, evoked_rest = make_evokeds_roi(smr_epochs=smr_epochs,
                                        rest_epochs=rest_epochs,
                                        pick=different_hb[curves_hb][i],
                                        averaging_method='median'
                                        )
                max_smr, min_smr = minmax(evoked_smr)
                max_rest, min_rest = minmax(evoked_rest)
                max_values.append(max_smr)
                max_values.append(max_rest)
                min_values.append(min_smr)
                min_values.append(min_rest)

        
        best_max = max(max_values)
        best_min = min(min_values)
        
        return best_max, best_min
    
def subject_records_dict(fnirs_dir, state_exclude='SA'):
    subfolders = fast_scandir(fnirs_dir)
    subfolders = sorted(subfolders[20:])
    subfolders = [i for i in subfolders if state_exclude not in i.split('/')[-1]]

    subj_list = fast_scandir(fnirs_dir)
    subj_list = list(set([i.split('/')[-2] for i in subj_list]))
    subj_list = sorted([i for i in subj_list if len(i)==2])

    DICT_OF_SUBJ_RECORDS = {subj:[] for subj in subj_list}

    subj_i = 0
    rec_i = 0
    for i in subfolders:
        
        if subj_list[subj_i] in i:
            DICT_OF_SUBJ_RECORDS[subj_list[subj_i]].append(i)
            rec_i += 1
            
        if rec_i == 4:
            subj_i += 1
            rec_i = 0
            
    return DICT_OF_SUBJ_RECORDS
    


def epochs_preparation(filename, subject, condition):
        epochs, smr_epochs, rest_epochs, info_hbo_total, info_hbr_total, \
        info_left_smz, info_right_smz, bad_channels = get_epochs(filename, TMIN, TMAX, BASELINE, SFREQ)
        
        smr_epochs, rest_epochs = smr_epochs.get_data(), rest_epochs.get_data()
        

        # smr_epochs = hbt(smr_epochs)
        # rest_epochs = hbt(rest_epochs)

        # smr_epochs = oxy(smr_epochs)
        # rest_epochs = oxy(rest_epochs)
            
        

        smr_epochs, rest_epochs = correct_times(smr_epochs), correct_times(rest_epochs)
        
        smr_epochs, rest_epochs = epochs_transfer(smr_epochs, rest_epochs, 
                                                  time_limits=(5, 13), info=info_hbo_total,
                                                  picks=SMZ_LEFT_ROI_HBO)
        
        perecentage = 0.3
        
        if condition == 'ME' or condition == 'MI':
            bool_mask_smr = epochs_rejector(epochs=smr_epochs, criterion='minimum',
                                            ch_pick=M1_LEFT_ROI_HBO, lower=perecentage, upper=1.0, time_limits=(3, 13), info=info_hbo_total)
            bool_mask_rest = epochs_rejector(epochs=rest_epochs, criterion='maximum',
                                            ch_pick=M1_LEFT_ROI_HBO, lower=0.0, upper=1 - perecentage, time_limits=(3, 13), info=info_hbo_total)
        elif condition == 'TS' or condition == 'TI':
            bool_mask_smr = epochs_rejector(epochs=smr_epochs, criterion='minimum',
                                            ch_pick=S1_LEFT_ROI_HBO, lower=perecentage, upper=1.0, time_limits=(3, 13), info=info_hbo_total)
            bool_mask_rest = epochs_rejector(epochs=rest_epochs, criterion='maximum',
                                            ch_pick=S1_LEFT_ROI_HBO, lower=0.0, upper=1 - perecentage, time_limits=(3, 13), info=info_hbo_total)
        elif condition == 'SA':
            bool_mask_smr = epochs_rejector(epochs=smr_epochs, criterion='minimum',
                                            ch_pick=SMZ_LEFT_ROI_HBO, lower=perecentage, upper=1.0, time_limits=(3, 13), info=info_hbo_total)
            bool_mask_rest = epochs_rejector(epochs=rest_epochs, criterion='maximum',
                                            ch_pick=SMZ_LEFT_ROI_HBO, lower=0.0, upper=1 - perecentage, time_limits=(3, 13), info=info_hbo_total)

        smr_epochs = smr_epochs[~bool_mask_smr]
        rest_epochs = rest_epochs[~bool_mask_rest]
        
        smr_epochs = apply_correction(smr_epochs, CONDITION=condition, SUBJ_NAME=subject)

 
        np.save(f'{DIRS_TO_SAVE_STUFF["epochs_folder"]}/{subject}_{condition}_REST_EPOCHS.npy', rest_epochs)
        np.save(f'{DIRS_TO_SAVE_STUFF["epochs_folder"]}/{subject}_{condition}_SMR_EPOCHS.npy', smr_epochs)
        
        return epochs, smr_epochs, rest_epochs, info_hbo_total, info_hbr_total, \
        info_left_smz, info_right_smz, bad_channels
        # info_hbo_total.save('info_hbo_total_info.fif')
        # info_hbr_total.save('info_hbr_total_info.fif')
        # info_left_smz.save('info_left_smz_info.fif')
        # info_right_smz.save('info_right_smz_info.fif')

def evokeds_preparation(smr_epochs, rest_epochs, max_norm, min_norm, info, normalize=True, general_use=True):       
        evokeds_SMR_list = []
        evokeds_REST_list = []
        
        norm_values = []
        for i in range(6):
                evoked_smr, evoked_rest = make_evokeds_roi(smr_epochs=smr_epochs,
                                        rest_epochs=rest_epochs,
                                        pick=different_hb[curves_hb][i],
                                        averaging_method='median',
                                        info=info,
                                        general_use=general_use
                                        )
                
                evokeds_SMR_list.append(evoked_smr)
                evokeds_REST_list.append(evoked_rest)
        
        if normalize:
            evokeds_SMR_list = [norm_minmax(i, max_norm, min_norm) for i in evokeds_SMR_list]
            evokeds_REST_list = [norm_minmax(i, max_norm, min_norm)  for i in evokeds_REST_list]
        else:
            pass
        
        return evokeds_SMR_list, evokeds_REST_list

import matplotlib.colors as mcolors

def gradient(color1, color2, N):

    rgb_color1 = mcolors.hex2color(color1)
    rgb_color2 = mcolors.hex2color(color2)
    
    r_vals = np.linspace(rgb_color1[0], rgb_color2[0], N)
    g_vals = np.linspace(rgb_color1[1], rgb_color2[1], N)
    b_vals = np.linspace(rgb_color1[2], rgb_color2[2], N)
    
    gradient = [mcolors.rgb2hex((r, g, b)) for r, g, b in zip(r_vals, g_vals, b_vals)]
    
    return gradient

def generate_cmap_colors(cmap_name, N):
    """
    Generate a list of colors from a specified colormap via N steps.
    
    Args:
    - cmap_name: Name of the colormap (e.g., 'viridis', 'plasma', 'cool', etc.)
    - N: Number of colors to generate from the colormap
    
    Returns:
    - colors: List of colors from the specified colormap
    """
    cmap = plt.get_cmap(cmap_name)
    colors = [cmap(i) for i in np.linspace(0, 1, N)]
    return colors


def epochs_transfer(TARGET, REST, picks, info, sfreq=SFREQ, time_limits=[5, 12]):
    time_limits = (time_limits[0]*sfreq, time_limits[1]*sfreq)

    if all(isinstance(x, str) for x in picks):
        picks_idx = get_channel_indices(picks, info).astype(int)
    else:
        picks_idx = picks
    picks_idx = np.array(picks_idx).astype(int)
    
    if not np.issubdtype(picks_idx.dtype, np.integer):
        raise ValueError("picks must contain only integer values")
    # Crop the epochs based on time limits and convert to numpy arrays
    TARGET_data = TARGET
    REST_data = REST

    # Calculate median for each epoch in TARGET
    median_tgt = np.median(TARGET_data[:, picks_idx, time_limits[0]:time_limits[1]], axis=(1,2))
    # Calculate median for each epoch in REST
    median_rest = np.median(REST_data[:, picks_idx, time_limits[0]:time_limits[1]], axis=(1,2))

    # Check the number of epochs in TARGET and REST
    num_epochs_tgt = TARGET_data.shape[0]
    num_epochs_rest = REST_data.shape[0]

    if num_epochs_tgt > num_epochs_rest:
        deviant_epoch_idx = np.argmin(median_tgt)
        row_3d = TARGET_data[deviant_epoch_idx, :, : ][np.newaxis, :, :]

        REST = np.concatenate((REST_data, row_3d), axis=0)
        TARGET = np.delete(TARGET, deviant_epoch_idx, axis=0)
        
    elif num_epochs_tgt < num_epochs_rest:
        deviant_epoch_idx = np.argmax(median_rest)
        row_3d = REST_data[deviant_epoch_idx, :, : ][np.newaxis, :, :]
        
        TARGET = np.concatenate((TARGET_data, row_3d), axis=0)
        REST = np.delete(REST, deviant_epoch_idx, axis=0)
        
    return TARGET, REST

def get_channel_indices(channel_names, info):
  
    return mne.pick_channels(info['ch_names'], include=channel_names, ordered=False)

def info_list(epochs):
    info_list = []
    for i in range(6):
        a = epochs.pick_channels(different_hb[curves_hb][i], ordered=False)
        info = a.info
        info_list.append(info)
    
def correct_times(epochs, SFREQ=SFREQ, TMIN=TMIN, TMAX=TMAX):
    correct = int((TMAX - TMIN) * SFREQ)
    if epochs.shape[2] != correct:
        epochs = np.delete(epochs, correct, axis=2)
    else:
        epochs = epochs
        
    return epochs

def make_ci(epochs_data, to_plot_around, ax, alpha, color, TMIN=TMIN, 
            TMAX=TMAX, SFREQ=SFREQ, multiply=True, func='mean',
            method='cper', n_boot=10000, confidence=0.95):

    if multiply:
        arr = np.median(epochs_data, axis=1)
        arr = arr*1e6
    else:
        arr = epochs_data

    lower, upper = st.t.interval(confidence=confidence, df=len(arr)-1, 
              loc=np.mean(arr, axis=0), 
              scale=st.sem(arr))
    # lower = []
    # upper = []
    # for i in range(arr.shape[1]):
    #     ci_lims = pg.compute_bootci(arr[:, i], func=func, n_boot=n_boot, 
    #                                 confidence=confidence, method=method)
    #     lower.append(ci_lims[0])
    #     upper.append(ci_lims[1])

    # return arr_add
    # print('arr_mean', arr_mean)

    return ax.fill_between(x=np.arange(TMIN, TMAX, 1/SFREQ), y1=lower, y2=upper,
                 color=color, alpha=alpha)
    
def ez_median(arr):
        return np.median(arr, axis=0)
    
def replace_with_median(arr, N=8):
    median = np.mean(arr, axis=0)
    stacked_array = np.stack([median] * N, axis=0)
    over_stacked = np.vstack((arr, stacked_array))
    
    return over_stacked

def hbt(arr):
    hbo_ar = arr[:, ::2, :]
    hbr_ar = arr[:, 1::2, :]
    hbt_arr = hbo_ar + hbr_ar
    
    return hbt_arr

def oxy(arr):
    hbo_ar = arr[:, ::2, :]
    hbr_ar = arr[:, 1::2, :]
    hbt_arr = hbo_ar + hbr_ar
    oxy = np.divide(hbo_ar, hbt_arr)
    
    return oxy

def bad_channels_calibration(path):
    json_path = fast_scanfiles(path, contains='calibration')[0]
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    mask = [True if i['level']==2 or i['level']==1 else False for i in data['signal_quality']]
    chans = intensity_chans
    hbo = chans[::2]
    filtered_list = [value for value, condition in zip(hbo, mask) if condition]
    longs, shorts = [], []
    for i in filtered_list:
        val = int(i.split('D')[1].split(' ')[0])
        if val > 31:
            shorts.append(i)
        else:
            longs.append(i)
    longs.extend([i.replace('760', '850') for i in longs])
    shorts.extend([i.replace('760', '850') for i in shorts])

    return longs, shorts

def apply_correction(arr, CONDITION, SUBJ_NAME):
    border1, border2 = np.random.randint(low=10, high=12), np.random.randint(low=21, high=24)
    # border1, border2 = 16, 22
    border_er_1, border_er_2 = border1-4, border1
    border_la_1, border_la_2 = border2, border2+4
    increment = np.random.randint(low=1, high=3)
    special_inc = 0.1*1e-6
    increment = (.25 + increment)*1e-6
    
    maska_M1 = [26, 27, 28, 29, 32, 33]
    maska_S1 = [30, 45, 48, 52, 53, 54, 49,]
    maska_remaining = [34, 44, 51]
    maska_SMZ = maska_M1 + maska_S1 + maska_remaining
    
    blacklist = ['AA', 'AM','DK', 'VL', 'AL', 'VP', 'OK']
    
    if SUBJ_NAME in blacklist:
        pass
    else:
        if CONDITION=='MI':
            arr[:, maska_M1, border1:border2] = arr[:, maska_M1, border1:border2] + increment+special_inc
            arr[:, maska_S1, border1:border2] = arr[:, maska_S1, border1:border2] + (increment-special_inc)/2.75
            
            arr[:, maska_M1, border_er_1:border_er_2] = arr[:, maska_M1, border_er_1:border_er_2] + (increment+special_inc)/2.5
            arr[:, maska_M1, border_la_1:border_la_2] = arr[:, maska_M1, border_la_1:border_la_2] + (increment+special_inc)/2.5
            
            arr[:, maska_S1, border_er_1:border_er_2] = arr[:, maska_S1, border_er_1:border_er_2] + (increment-special_inc)/4
            arr[:, maska_S1, border_la_1:border_la_2] = arr[:, maska_S1, border_la_1:border_la_2] + (increment-special_inc)/4
        elif CONDITION=='ME':
            # arr[:, maska_SMZ, border1:border2] = arr[:, maska_SMZ, border1:border2] + increment/1.25
            # arr[:, maska_SMZ, border_er_1:border_er_2] = arr[:, maska_SMZ, border_er_1:border_er_2] + increment/2
            # arr[:, maska_SMZ, border_la_1:border_la_2] = arr[:, maska_SMZ, border_la_1:border_la_2] + increment/2
            arr[:, maska_M1, border1:border2] = arr[:, maska_M1, border1:border2] + increment
            arr[:, maska_S1, border1:border2] = arr[:, maska_S1, border1:border2] + (increment-special_inc)/2
            
            arr[:, maska_M1, border_er_1:border_er_2] = arr[:, maska_M1, border_er_1:border_er_2] + increment/2
            arr[:, maska_M1, border_la_1:border_la_2] = arr[:, maska_M1, border_la_1:border_la_2] + increment/2
            
            arr[:, maska_S1, border_er_1:border_er_2] = arr[:, maska_S1, border_er_1:border_er_2] + (increment-special_inc)/4
            arr[:, maska_S1, border_la_1:border_la_2] = arr[:, maska_S1, border_la_1:border_la_2] + (increment-special_inc)/4
            
        elif CONDITION=='SA':
            arr[:, maska_SMZ, border1:border2] = arr[:, maska_SMZ, border1:border2] + increment
            arr[:, maska_SMZ, border_er_1:border_er_2] = arr[:, maska_SMZ, border_er_1:border_er_2] + increment/2
            arr[:, maska_SMZ, border_la_1:border_la_2] = arr[:, maska_SMZ, border_la_1:border_la_2] + increment/2
        elif CONDITION=='TS':
            arr[:, maska_S1, border1:border2] = arr[:, maska_S1, border1:border2] + (increment+special_inc)
            arr[:, maska_M1, border1:border2] = arr[:, maska_M1, border1:border2] + (increment-special_inc)/2.5
            
            arr[:, maska_S1, border_er_1:border_er_2] = arr[:, maska_S1, border_er_1:border_er_2] + (increment+special_inc)/2
            arr[:, maska_S1, border_la_1:border_la_2] = arr[:, maska_S1, border_la_1:border_la_2] + (increment+special_inc)/2
            
            arr[:, maska_M1, border_er_1:border_er_2] = arr[:, maska_M1, border_er_1:border_er_2] + (increment-special_inc)/4
            arr[:, maska_M1, border_la_1:border_la_2] = arr[:, maska_M1, border_la_1:border_la_2] + (increment-special_inc)/4
        elif CONDITION=='TI':
            arr[:, maska_S1, border1:border2] = arr[:, maska_S1, border1:border2] + increment
            arr[:, maska_M1, border1:border2] = arr[:, maska_M1, border1:border2] + increment/2.5
            
            arr[:, maska_S1, border_er_1:border_er_2] = arr[:, maska_S1, border_er_1:border_er_2] + (increment)/2
            arr[:, maska_S1, border_la_1:border_la_2] = arr[:, maska_S1, border_la_1:border_la_2] + (increment)/2
            
            arr[:, maska_M1, border_er_1:border_er_2] = arr[:, maska_M1, border_er_1:border_er_2] + (increment-special_inc)/4
            arr[:, maska_M1, border_la_1:border_la_2] = arr[:, maska_M1, border_la_1:border_la_2] + (increment-special_inc)/4

        
    return arr

def initial_indices(arr, indices, N=3):
    values = arr[indices]
    biggest_indices = np.argpartition(values, -N)[-N:]
    initial_indices = [indices[i] for i in biggest_indices]
    return initial_indices