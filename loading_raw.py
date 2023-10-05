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

def get_raw_haemo(filename):
    raw_intensity = mne.io.read_raw_nirx(
        filename,
        verbose=True
    )
    raw_od = mne.preprocessing.nirs.optical_density(raw_intensity) #from row wavelength data
    
    try:
        raw_od_shorts = mne_nirs.channels.get_short_channels(raw_od)
        sci_shorts = scalp_coupling_index( 
                                    raw_od_shorts, 
                                    )
        bad_sci_shorts = list(compress(raw_od_shorts.ch_names, sci_shorts < 0.75))
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
    raw_od.resample(sfreq)
    raw_od = temporal_derivative_distribution_repair(raw_od) #repairs movement artifacts
    
    low_f_border, high_f_border = 0.05, 0.1
    # low_f_border, high_f_border = 0.05, 0.1
    # h_trans_bandwidth, l_trans_bandwidth = 0.2, 0.015
    
    raw_od = raw_od.filter(low_f_border, high_f_border,
                                 method='fir',
                                 fir_design='firwin2',
                                # h_trans_bandwidth=h_trans_bandwidth,
                                # l_trans_bandwidth=l_trans_bandwidth, 
                                n_jobs=-1)
    
    raw_haemo = mne.preprocessing.nirs.beer_lambert_law(raw_od, ppf=0.1) #from wavelength to HbO\HbR
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
    raw_haemo = raw_haemo.interpolate_bads()

    
    return raw_haemo