import mne
import mne_nirs
import numpy as np
    
    
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



