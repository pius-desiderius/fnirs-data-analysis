import mne
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os



def average_activity_in_epochs(epochs, limits, sfreq, averaging_mode='mean'):
    epochs_data = epochs.get_data()
    selected_data = epochs_data[:, :, limits[0]*sfreq:limits[1]*sfreq]
    if averaging_mode == 'mean':
        average_epoch = np.mean(selected_data, axis=(0, 2))
    if averaging_mode == 'median':
        average_epoch = np.median(selected_data, axis=(0, 2))

    return average_epoch

def single_topomap_plotter(data, info,
                    show_flag=False,
                    picture_title='sample title'
                    save_picture_flag=True):

    fig, ax1 = plt.subplots(1, 1)
    single_topomap = mne.viz.plot_topomap(data=data, pos=info, show=show_flag, axes=ax1)
    ax1.set_title(picture_title)
    return fig

def topomaps_plotter(haemo_picks, smr_epochs, rest_epochs, CONDITION, SUBJECT):
        times = np.arange(2, 14, 2)
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
            
def epochs_structure(epochs, SUBJECT, CONDITION):
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 6))
    epochs['Sensorimotor'].plot_image(combine='mean', vmin=-15, vmax=15,
                             ts_args=dict(ylim=dict(hbo=[-15, 15],
                                                    hbr=[-15, 15])),
                                                    axes=axes,
                                                    evoked=True, 
                                                    colorbar=True,
                                                    picks = C3_chans_of_interest_hbo,
                                                    show=False)
    fig.savefig(rf'{dirs_to_save_stuff["epochs_structure_path"]}\{SUBJECT} {CONDITION} SMR epochs.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types
    fig.clear()
    
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 6))
    epochs['Rest'].plot_image(combine='mean', vmin=-15, vmax=15,
                             ts_args=dict(ylim=dict(hbo=[-15, 15],
                                                    hbr=[-15, 15])),
                                                    axes=axes,
                                                    evoked=True, 
                                                    colorbar=True, 
                                                    picks = C3_chans_of_interest_hbo,
                                                    show=False)

    fig.savefig(rf'{dirs_to_save_stuff["epochs_structure_path"]}\{SUBJECT} {CONDITION} Rest epochs.png', bbox_inches='tight') #this is a figure for our hemodynamic curves for epochs and haemo types
    fig.clear()
