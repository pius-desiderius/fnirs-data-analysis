import numpy as np
import matplotlib.pyplot as plt
import mne
import mne_nirs
from mne.preprocessing.nirs import optical_density, beer_lambert_law
from mne_nirs.signal_enhancement import enhance_negative_correlation

from mne.preprocessing.nirs import (optical_density,
                                    temporal_derivative_distribution_repair)

from mne import events_from_annotations
from meta import *
from ROI import different_roi
from filter_params import FILTER_DICT
from file_scanning import *

def make_evokeds_roi(smr_epochs, rest_epochs, pick):

    smr_roi_epochs = smr_epochs.copy().pick(pick)
    smr_roi_epochs_info = smr_roi_epochs.info
    rest_roi_epochs = rest_epochs.copy().pick(pick)
    
    evoked_smr = smr_roi_epochs.get_data().mean(axis=0)
    evoked_rest = rest_roi_epochs.get_data().mean(axis=0)
    
    return evoked_smr, evoked_rest, smr_roi_epochs_info

def epochs_rejector(epochs, ch_pick, criterion='median',
                    sfreq=SFREQ, 
                    time_limits = (4, 12),
                    lower=0.10, upper=0.90): 

    time_limits = (time_limits[0]*sfreq, time_limits[1]*sfreq)
    epochs.copy().pick_channels(ch_pick)
    epochs_data = epochs.get_data()[:, :, time_limits[0]:time_limits[1]]

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

def get_epochs(filename, TMIN, TMAX, BASELINE, SFREQ):

    raw_intensity = mne.io.read_raw_nirx(filename, verbose=False)
    raw_od = optical_density(raw_intensity) #from row wavelength data
    raw_od_shorts = mne_nirs.channels.get_short_channels(raw_od)
    raw_od.drop_channels(DROP_CHANS) #we had a non-existent channel

    raw_od = mne_nirs.signal_enhancement.short_channel_regression(raw_od)
    raw_od = mne_nirs.channels.get_long_channels(raw_od)
    raw_od = temporal_derivative_distribution_repair(raw_od)
    raw_od_unfiltered = raw_od.copy() #repairs movement artifacts
    raw_od = raw_od.filter(**FILTER_DICT)

    ### BAD CHANNELS ###
    channel_std = np.std(raw_od.copy().pick([i for i in raw_od.ch_names if '760' in i]).get_data(), 
                         axis=(1))
    deviant_channels_idx = np.argpartition(channel_std, -10)[-10:]
    bad_channels_hbo = [raw_od.copy().pick([i for i in raw_od.ch_names if '760' in i]).ch_names[i]
                   for i in deviant_channels_idx]
    bad_channels_hbr = [i.replace('760', '850') for i in bad_channels_hbo]
    bad_channels = bad_channels_hbo + bad_channels_hbr

    raw_od.info['bads'] = bad_channels
    raw_od.interpolate_bads(method={'fnirs':'nearest'})
    raw_od.apply_function(rolling_mean_filter, picks=raw_od.ch_names)


    raw_haemo = beer_lambert_law(raw_od, ppf=0.1) #from wavelength to HbO\HbR
    raw_haemo = enhance_negative_correlation(raw_haemo)
    ######################################
    ids_target= 'SMR'
    ids_rest = 'REST'

    events, ids = events_from_annotations(raw_haemo)
    ids[ids_target] = 1
    ids[ids_rest] = 2

    IDS_TO_POP = ["2.0", "33.0", "1.0", "2", "1", "33"]
    ids_to_pop = IDS_TO_POP
    for i in ids_to_pop:
        popper(ids, i)

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

    rest_epochs = epochs['REST']
    smr_epochs = epochs['SMR']

    info_hbo_total = rest_epochs.copy().pick_types(fnirs='hbo').info
    info_hbr_total = rest_epochs.copy().pick_types(fnirs='hbr').info

    
    return epochs, smr_epochs, rest_epochs, info_hbo_total, info_hbr_total, info_left_smz, info_right_smz, bad_channels


def relative_measure(arr_target, arr_rest, SFREQ):
    a_rest = np.median(arr_rest[1*SFREQ:4*SFREQ])
    relation = (arr_target - a_rest) / np.abs(a_rest) * 100
    return relation    
    

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

    ax.set_title(title, fontsize=title_size)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.axvline(x=0, color='black', linestyle='--', linewidth=linewidth)
    ax.axhline(y=0, color='black', linewidth=linewidth)
    
    if legend_flag:
        ax.legend(loc='lower center')
        
        
def filler_between(ax, ylims):

    return ax.fill_between( [0, 4], 
                                ylims[0]/3, 
                                ylims[1]/3, 
                                color='#576767', 
                                alpha=0.15, 
                                label='Task duration')
    
def get_top_channels_mask(arr, info, top_n=10):
    top_idx = np.argpartition(arr, 
                                    -1*top_n)[-1*top_n:]
    mask = np.zeros(arr.shape[0], dtype=bool)
    mask[top_idx] = True
    top_values = arr[top_idx]
    names_dict = {info['ch_names'][int(top_idx[idx])]:top_values[idx] for idx in range(len(top_idx))}
    return mask, names_dict

def relative_measure_topo(arr_target, arr_rest, SFREQ):
    a_rest = np.median(arr_rest[:, 1*SFREQ:4*SFREQ], axis=1)
    relation = (arr_target - a_rest[:, None]) / np.abs(a_rest[:, None]) * 100
    return relation

    
    
    
    
