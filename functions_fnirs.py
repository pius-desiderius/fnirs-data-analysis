import os.path as op
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from itertools import compress
from scipy import stats as st
import time

import mne
import mne_nirs
from mne.preprocessing.nirs import optical_density, beer_lambert_law

from mne.preprocessing.nirs import (optical_density,
                                    temporal_derivative_distribution_repair,
                                    scalp_coupling_index)
from mne import Epochs, events_from_annotations
from meta import *


def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

def fast_scanfiles(dirname, contains=None):
    subfiles = [f.path for f in os.scandir(dirname) if f.is_file()]
    if contains != None:
        subfiles = [i for i in subfiles if contains in i ]
    return subfiles

def fast_scanfiles_subjfiles(dirname, contains=None):
    subfolders = fast_scandir(dirname)
    subfiles = []
    subfiles.extend(fast_scanfiles(dirname, contains=contains))
    for dirs in subfolders:
        subfiles.extend(fast_scanfiles(dirs, contains=contains))
    return subfiles

def clean_epochs(raw_haemo, events, ids, tmin=-0.2, tmax=14, baseline=(-0.2, 0.0)):
        '''This functions takes raw_haemo recording, events and ids, 
        splits them into epochs according to events timings and ids. 
        There is and inside function epoch_rejector, which recjects top and low 10% of
        deviant epochs in each epochs' type ''' 

        tmin, tmax = tmin, tmax
        epochs = mne.Epochs(
                            raw_haemo,
                            events,
                            event_id=ids,
                            baseline=baseline,
                            tmin=tmin,
                            tmax=tmax,
                            preload=True,
                            verbose=False,
                            # picks=picks
                        )

        rest_epochs_raw = epochs["Rest"]
        smr_epochs_raw = epochs["Sensorimotor"]

        info = smr_epochs_raw.info
        chans = mne.io.pick.channel_indices_by_type(info)
        info_hbo = mne.pick_info(info,chans['hbo'])
        info_hbr = mne.pick_info(info,chans['hbr'])
        hbo_chnames = info_hbo.ch_names
        hbr_chanames = info_hbr.ch_names

        smr_reject_bool = epochs_rejector(smr_epochs_raw, lower=0.2, upper=1.0, time_limits = (5, 13))
        rest_reject_bool = epochs_rejector(rest_epochs_raw, lower=0.0, upper=0.80, time_limits = (4, 12))

        smr_epochs = smr_epochs_raw.drop(smr_reject_bool)
        rest_epochs = rest_epochs_raw.drop(rest_reject_bool)

        evoked_smr = smr_epochs.average()
        evoked_rest = rest_epochs.average()

        return smr_epochs, rest_epochs, evoked_smr, evoked_rest



def epochs_rejector(epochs, criterion='median',
                    sfreq=5, 
                    time_limits = (4, 12),
                    lower=0.10, upper=0.90):
    time_limits = (time_limits[0]*sfreq, time_limits[1]*sfreq)
    epochs.copy().pick_channels(C3_chans_of_interest_hbo)
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



def topomaps_plotter(haemo_picks, smr_epochs, rest_epochs, CONDITION, SUBJECT):
        times = np.arange(2*sfreq, 14*sfreq, 2*sfreq)
        haemo_picks = haemo_picks

        if haemo_picks=='hbo':
            topo_haemo = 'HbO'
        else:
            topo_haemo = 'HbR'

        topomap_args = dict(extrapolate='local')
        smr_evoked = smr_epochs.average(picks=haemo_picks)
        rest_evoked = rest_epochs.average(picks=haemo_picks)
        vmin = min(smr_evoked.data.min(), rest_evoked.data.min())*10**6
        vmax = max(smr_evoked.data.max(), rest_evoked.data.max())*10**6
        vlim = (vmin, vmax)
        sm = plt.cm.ScalarMappable(cmap='RdBu_r', norm=matplotlib.colors.Normalize(vmin=vmin, vmax=vmax))

        # create a figure to contain both topomap plots
        fig, axes = plt.subplots(2, len(times), figsize=(14, 7))

        # loop through times and plot the topomaps for smr epochs and rest epochs
        smr_fig = smr_evoked.plot_topomap(times, axes=axes[0, :],
                                colorbar=False,
                                show=False,
                                **topomap_args)
        rest_fig = rest_evoked.plot_topomap(times, axes=axes[1, :],
                                show=False,
                                colorbar=False,
                                **topomap_args)

        cbaxes = fig.add_axes([0.095, 0.25, 0.02, 0.5]) # setup colorbar axes. 

        cbar = plt.colorbar(mappable=sm, cax=cbaxes, pad=0.15, orientation='vertical')
        cbar.set_label(f'{topo_haemo} concentration, Δ μM\L', loc='center', size=12)

        fig.subplots_adjust( 
                            top=0.910, 
                            bottom=0.06,
                            left=0.150, 
                            right=0.950, 
                            hspace=0.195, 
                            wspace=0.0 
                        )

        x_top, y_top = 0.55, 0.95
        x_bottom, y_bottom = 0.55, 0.5

        fig.text(
                x=x_top, y=y_top, 
                s=f'{CONDITION} {topo_haemo} changes timeline', 
                fontsize='x-large', 
                horizontalalignment='center', 
                verticalalignment='center' 
                )
        fig.text( 
                x=x_bottom, y=y_bottom, 
                s=f'Rest {topo_haemo} changes timeline', 
                fontsize='x-large', 
                horizontalalignment='center', 
                verticalalignment='center'
                )#we set a timeline for each epoch
        if haemo_picks == 'hbo':
            topo_smr_np = np.save(rf'{dirs_to_save_stuff["topo_hbo_path_np"]}\{SUBJECT} {CONDITION}_smr {haemo_picks} np topo.npy', smr_evoked.get_data())
            topo_rest_np = np.save(rf'{dirs_to_save_stuff["topo_hbo_path_np"]}\{SUBJECT} {CONDITION}_rest {haemo_picks} np topo.npy', rest_evoked.get_data())
            fig.savefig(rf'{dirs_to_save_stuff["topo_hbo_path"]}\{SUBJECT} {CONDITION} timeline.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types
            fig.clear()
        elif haemo_picks == 'hbr':
            topo_smr_np = np.save(rf'{dirs_to_save_stuff["topo_hbr_path_np"]}\{SUBJECT} {CONDITION}_smr {haemo_picks} np topo.npy', smr_evoked.get_data())
            topo_rest_np = np.save(rf'{dirs_to_save_stuff["topo_hbr_path_np"]}\{SUBJECT} {CONDITION}_rest {haemo_picks} np topo.npy', rest_evoked.get_data())
            fig.savefig(rf'{dirs_to_save_stuff["topo_hbr_path"]}\{SUBJECT} {CONDITION} timeline.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types
            fig.clear()