import mne
import mne_nirs
import numpy as np



def make_evokeds_roi(smr_epochs, rest_epochs, pick):

    smr_roi_epochs = smr_epochs.copy().pick(pick)
    rest_roi_epochs = rest_epochs.copy().pick(pick)
    
    evoked_smr = smr_roi_epochs.get_data().mean(axis=0)
    evoked_rest = rest_roi_epochs.get_data().mean(axis=0)
    
    return evoked_smr, evoked_rest
    
    
    
    
def make_topo_arrays(smr_epochs, rest_epochs, hb_type, window=None):
    
    if hb_type == 'hbr' or hb_type=='hbo':
        smr_topos = smr_epochs.copy().pick(fnirs=hb_type)
        rest_topos = rest_epochs.copy().pick(fnirs=hb_type)
        
        smr_topos_mean = smr_topos.mean(axis=0)
        rest_topos_mean = rest_topos.mean(axis=0)
        
        return smr_topos_mean, rest_topos_mean
    
    elif hb_type == 'hbt':
        smr_topos_hbo = smr_epochs.copy().pick(fnirs='hbo')
        rest_topos_hbo = rest_epochs.copy().pick(fnirs='hbo')
        smr_topos_hbr = smr_epochs.copy().pick(fnirs='hbr')
        rest_topos_hbr = rest_epochs.copy().pick(fnirs='hbr') 
        
        smr_topos_hbt = smr_topos_hbo + smr_topos_hbr
        rest_topos_hbt = rest_topos_hbo + rest_topos_hbr
        
        smr_topos_hbt_mean = smr_topos_hbt.mean(axis=0)
        rest_topos_hbt_mean = rest_topos_hbt.mean(axis=0)
        
        return smr_topos_hbt_mean, rest_topos_hbt_mean
    
    elif hb_type == 'rel_hbo' and window:
        smr_topos_hbo = smr_epochs.copy().pick(fnirs='hbo')
        rest_topos_hbo = rest_epochs.copy().pick(fnirs='hbo')
        smr_topos_mean = smr_topos_hbo.mean(axis=0)
        rest_topos_mean = rest_topos_hbo.mean(axis=0)
        
        smr_ref = np.median(smr_topos_mean[:, window[0]:window[1]])
        smr_relation_mean = (smr_topos_mean - smr_ref) / smr_ref * -1
        rest_ref = np.median(rest_topos_mean[:, window[0]:window[1]])
        rest_relation_mean = (rest_topos_mean - rest_ref) / rest_ref * -1
        
        return smr_relation_mean, rest_relation_mean
    
    elif hb_type == 'rel_hbr' and window:
        smr_topos_hbr = smr_epochs.copy().pick(fnirs='hbr')
        rest_topos_hbr = rest_epochs.copy().pick(fnirs='hbr')
        smr_topos_mean = smr_topos_hbr.mean(axis=0)
        rest_topos_mean = rest_topos_hbr.mean(axis=0)
        
        smr_ref = np.median(smr_topos_mean[:, window[0]:window[1]])
        smr_relation_mean = (smr_topos_mean - smr_ref) / smr_ref * -1
        rest_ref = np.median(rest_topos_mean[:, window[0]:window[1]])
        rest_relation_mean = (rest_topos_mean - rest_ref) / rest_ref * -1
        
        return smr_relation_mean, rest_relation_mean
    
    
    elif hb_type == 'rel_hbt' and window:
        smr_topos_hbo = smr_epochs.copy().pick(fnirs='hbo')
        rest_topos_hbo = rest_epochs.copy().pick(fnirs='hbo')
        smr_topos_hbr = smr_epochs.copy().pick(fnirs='hbr')
        rest_topos_hbr = rest_epochs.copy().pick(fnirs='hbr') 
        
        smr_topos_hbt = smr_topos_hbo + smr_topos_hbr
        rest_topos_hbt = rest_topos_hbo + rest_topos_hbr
        
        smr_topos_hbt_mean = smr_topos_hbt.mean(axis=0)
        rest_topos_hbt_mean = rest_topos_hbt.mean(axis=0)
        
        smr_ref = np.median(smr_topos_hbt_mean[:, window[0]:window[1]])
        smr_topos_relation_hbt_mean = (smr_topos_hbt_mean - smr_ref) / smr_ref * -1
        rest_ref = np.median(rest_topos_hbt_mean[:, window[0]:window[1]])
        rest_topos_relation_hbt_mean = (rest_topos_hbt_mean - rest_ref) / rest_ref * -1
        
        return smr_topos_relation_hbt_mean, rest_topos_relation_hbt_mean
    
    
def mean_topomap(arr, window=(4, 12)):
    mean_arr = arr[:, window[0]:window[1]].mean(axis=1)
    return mean_arr





def set_axis_properties(ax, ylims, tlims, title,

                        xlabel='Time, s', 
                        ylabel='Hb concentration, Δ μM\L',  
                        linewidth=1.5, 
                        fontsize=14, 
                        title_size=18):
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
   ax.fill_between([0, 4], ylims[0]/2, ylims[1]/2, color='blue', alpha=0.2)

   for i in ax.spines.values():
       i.set_linewidth(linewidth)

   ax.set_title(title, fontsize=title_size)

   ax.spines['top'].set_visible(False)
   ax.spines['right'].set_visible(False)

   ax.axvline(x=0, color='black', linestyle='--', linewidth=linewidth)
   ax.axhline(y=0, color='black', linewidth=linewidth)

   ax.legend()