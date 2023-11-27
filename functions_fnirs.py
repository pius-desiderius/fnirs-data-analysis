import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from itertools import compress
import mne
import mne_nirs
from mne.preprocessing.nirs import optical_density, beer_lambert_law

from mne_nirs.signal_enhancement import enhance_negative_correlation, short_channel_regression

from mne.preprocessing.nirs import (optical_density,
                                    temporal_derivative_distribution_repair,
                                    scalp_coupling_index)

from mne import Epochs, events_from_annotations
from meta import *
from ROI import DROP_CHANS
from filter_params import FILTER_DICT
from file_scanning import *

def std_channels_rejector(raw_haemo, threshold):
    channel_std = np.std(raw_haemo.get_data(), axis=(1))
    threshold = threshold
    outlier_channels = list(np.where(channel_std > threshold)[0])
    
    return outlier_channels
    
def get_raw_haemo(filename):
    raw_intensity = mne.io.read_raw_nirx(filename, verbose=False)
    raw_od = optical_density(raw_intensity) #from row wavelength data

    raw_od_shorts = mne_nirs.channels.get_short_channels(raw_od)
    sci_shorts = scalp_coupling_index(raw_od_shorts)
    bad_sci_shorts = list(compress(raw_od_shorts.ch_names, sci_shorts < 0.75))
    raw_od.drop_channels(bad_sci_shorts)
    raw_od.drop_channels(DROP_CHANS) #we had a non-existent channel

    raw_od = mne_nirs.signal_enhancement.short_channel_regression(raw_od)
    raw_od = mne_nirs.channels.get_long_channels(raw_od)
    raw_od = temporal_derivative_distribution_repair(raw_od) #repairs movement artifacts

    sci = scalp_coupling_index(raw_od)
    bad_sci = list(compress(raw_od.ch_names, sci < 0.6))
    bad_sci = [i.replace('760', 'hbr') for i in bad_sci]
    bad_sci = [i.replace('850', 'hbr') for i in bad_sci]
    bad_sci_hbo = [i.replace('hbr', 'hbo') for i in bad_sci]
    bad_sci = list(set(bad_sci + bad_sci_hbo))
    
    raw_haemo = beer_lambert_law(raw_od, ppf=0.1) #from wavelength to HbO\HbR
    # channels_to_interpolate = std_channels_rejector(raw_haemo, threshold) + bad_sci
    channels_to_interpolate =  bad_sci
    raw_haemo = raw_haemo.filter(**FILTER_DICT)
    print(channels_to_interpolate, '\n', len(channels_to_interpolate))
    raw_haemo.info['bads'] = channels_to_interpolate
    raw_haemo = raw_haemo.interpolate_bads()
    raw_haemo = enhance_negative_correlation(raw_haemo)


    return raw_haemo, channels_to_interpolate

def clean_epochs(raw_haemo, events, ids, tmin, tmax, baseline, drop_epochs_flag=True):
        '''This functions takes raw_haemo recording, events and ids, 
        splits them into epochs according to events timings and ids. 
        There is and inside function epoch_rejector, which recjects top and low 10% of
        deviant epochs in each epochs' type ''' 

        epochs = mne.Epochs(
                            raw=raw_haemo,
                            events=events,
                            event_id=ids,
                            baseline=baseline,
                            tmin=tmin,
                            tmax=tmax,
                            preload=True,
                            verbose=False,
                            # picks=picks
                        )

        rest_epochs_raw = epochs['REST']
        smr_epochs_raw = epochs['SMR']

        if drop_epochs_flag:
            smr_reject_bool = epochs_rejector(smr_epochs_raw, 
                                              lower=SMR_LOWER_QUANTILE, 
                                              upper=SMR_UPPER_QUANTILE, 
                                              time_limits = (5, 13)
                                              )
            rest_reject_bool = epochs_rejector(rest_epochs_raw, 
                                               lower=REST_LOWER_QUANTILE, 
                                               upper=REST_UPPER_QUANTILE, 
                                               time_limits = (5, 13)
                                               )
            smr_epochs = smr_epochs_raw.drop(smr_reject_bool)
            rest_epochs = rest_epochs_raw.drop(rest_reject_bool)
        else:
            smr_epochs = smr_epochs_raw
            rest_epochs = rest_epochs_raw

        return smr_epochs, rest_epochs

def make_evokeds_roi(smr_epochs, rest_epochs, pick):

    smr_roi_epochs = smr_epochs.copy().pick(pick)
    rest_roi_epochs = rest_epochs.copy().pick(pick)
    
    evoked_smr = smr_roi_epochs.get_data().mean(axis=0)
    evoked_rest = rest_roi_epochs.get_data().mean(axis=0)
    
    return evoked_smr, evoked_rest

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

def hbt_total(hbo_arr, hbr_arr):
    hbt_arr = hbo_arr + hbr_arr
    return hbt_arr

def oxy_level(hbo_arr, hbr_arr):
    oxygenation = hbo_arr / hbt_total(hbo_arr, hbr_arr)
    return oxygenation

def relative_measure(arr_target, arr_rest):
    a_rest = np.median(arr_rest[:, 1:4])
    relation = (arr_target - a_rest) / a_rest * -1
    return relation