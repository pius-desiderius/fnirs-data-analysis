import numpy as numpy

def convert_epochs(path_eeg, path_fnirs):
    '''Даешь путь к ЭЭГ в формате .vhdr и путь к папке с записью фНИРС.
    на выходе получаешь скорректированный под sampling rate фНИРСа массив 
    ивентами, а также название фнирсовой записи (типа 'AM_ME', 'LJ_TS')
    '''
    name = path_fnirs[-5:]
    raw_eeg = mne.io.read_raw_brainvision(path_eeg, verbose=False)
    sfreq_eeg = raw_eeg.info['sfreq']
    raw_haemo = mne.io.read_raw_nirx(path_fnirs, verbose=False)
    sfreq_haemo = raw_haemo.info['sfreq']
    
    try:
        events_eeg, ids_eeg = mne.events_from_annotations(raw_eeg)
        events_haemo, ids_haemo = mne.events_from_annotations(raw_haemo)
        events_eeg = events_eeg[(events_eeg[:, 2] == 10001) | (events_eeg[:, 2] == 10002)]
        events_eeg = np.vstack((events_eeg[:, 0]/sfreq_eeg, events_eeg[:, 1], events_eeg[:, 2])).T
        events_haemo = np.vstack((events_haemo[:, 0]/sfreq_haemo, events_haemo[:, 1], events_haemo[:, 2])).T

        events_eeg = events_eeg[(events_eeg[:, 2] == 10001) | (events_eeg[:, 2] == 10002)]
        events_haemo = events_haemo[(events_haemo[:, 2] == 2) | (events_haemo[:, 2] == 1)]

        first_eeg_timestamp = events_eeg[0, 0]
        first_haemo_timestamp = events_haemo[0, 0]
        time_diff = first_haemo_timestamp - first_eeg_timestamp

        new_fnirs_events = events_eeg[:, :]
        new_fnirs_events[:, 0] += time_diff
        new_fnirs_events[:, 0] *= sfreq_haemo

        new_fnirs_events[:, 2] = np.where(new_fnirs_events[:, 2] == 10001, 1, new_fnirs_events[:, 2])
        new_fnirs_events[:, 2] = np.where(new_fnirs_events[:, 2] == 10002, 2, new_fnirs_events[:, 2])
        new_fnirs_events = np.round(new_fnirs_events, decimals=0).astype(int)

        return new_fnirs_events, name
    except IndexError:
        events_haemo, ids_haemo = mne.events_from_annotations(raw_haemo)
        events_haemo = np.vstack((events_haemo[:, 0]/sfreq_haemo, events_haemo[:, 1], events_haemo[:, 2])).T
        events_haemo = events_haemo[(events_haemo[:, 2] == 2) | (events_haemo[:, 2] == 1)]
        events_haemo[:, 0] *= sfreq_haemo
        events_haemo = events_haemo.astype(int)

        
        return events_haemo, name