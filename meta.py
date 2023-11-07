#DEFINE SAMPLING RATE
SFREQ = 1

#DEFINE EPOCHS LIMITS
TMIN = float(0.0)
TMAX = float(14.0)

#DEFINE EPOCHS LABELS
EPOCHS_LABEL_REST = 'REST'
EPOCHS_LABEL_SMR = 'SMR'

#DEFINE IDS TO POP
IDS_TO_POP = ["2.0", "33.0", "1.0", "2", "1", "33"]

#DEFINE BASELINE
BASELINE = (0, 0)

#DEFINE EPOCHS DROPPING PARAMETERS
SMR_LOWER_QUANTILE, SMR_UPPER_QUANTILE = 0.05, 0.95
REST_LOWER_QUANTILE, REST_UPPER_QUANTILE = 0.05, 0.95

#DEFINE FAULTY CHANNELS TO DROP 
CHANNELS_TO_DROP = []
SPECIAL_CHANNELS_TO_DROP = []

#DEFINE ROI FOR LEFT HEMISPHERE
RIGHT_ROI_CHANNELS = ['S9_D18 760',
  'S9_D18 850',
  'S13_D18 760',
  'S13_D18 850',
  'S15_D18 760',
  'S15_D18 850',
  'S16_D13 760',
  'S16_D13 850',
  'S16_D16 760',
  'S16_D16 850',
  'S16_D18 760',
  'S16_D18 850',
  'S16_D19 760',
  'S16_D19 850',
  'S16_D23 760',
  'S16_D23 850',
  'S19_D18 760',
  'S19_D18 850',
  'S20_D18 760',
  'S20_D18 850',
  'S20_D36 760',
  'S20_D36 850',
  'S23_D18 760',
  'S23_D18 850',
  'S24_D19 760',
  'S24_D19 850']

#DEFINE ROI FOR RIGHT HEMISPHERE
LEFT_ROI_CHANNELS = []


#DEFINE PATHNAMES FOR DIRECTORIES
DIRS_TO_SAVE_STUFF = dict(
                            haemo_folder_path = r"./haemodynamics",
                            haemo_folder_path_np = r"./haemodynamics_np",
                            topo_hbo_path = r"./topomaps_hbo",
                            topo_hbo_path_np = r"./topomaps_hbo_np",
                            topo_hbr_path = r"./topomaps_hbr",
                            topo_hbr_path_np = r"./topomaps_hbr_np",
                            epochs_structure_path = r"./epochs_structure",
)


C3 = ['C5', 'C1', 'CCP5h', 'CCP3h']
C4 = ['C2', 'C6', 'CCP4h', 'CCP6h']

optodes_to_channels = {
                'FC3':'D10',
                'FC4':'D11',
                'FTT7h':'D12',
                'FCC5h':'S9',
                'FCC3h':'D13',
                'FCC1h':'S10',
                'FCC2h':'S11',
                'FCC4h':'D14',
                'FCC6h':'S12',
                'FTT8h':'D15',
                'C5':'S13',
                'C1':'D16',
                'C2':'D17',
                'C6':'S14',
                'TTP7h':'S15',
                'CCP5h':'D18',
                'CCP3h':'S16',
                'CCP1h':'D19',
                'CCP2h':'D20',
                'CCP4h':'S17',
                'CCP6h':'D21',
                'TTP8h':'S18'
                }


C3_channels = [optodes_to_channels[i] for i in C3]
C4_channels = [optodes_to_channels[i] for i in C4]

# def chans_of_interest(optodes_of_interest):
#     chans_hbo = [x for x in chnames if any(y in x for y in optodes_of_interest) if 'hbo' in x]
#     chans_hbr = [x for x in chnames if any(y in x for y in optodes_of_interest) if 'hbr' in x]
#     return chans_hbo, chans_hbr

# C3_chans_of_interest_hbo, C3_chans_of_interest_hbr = chans_of_interest(C3_channels)
# C4_chans_of_interest_hbo, C4_chans_of_interest_hbr = chans_of_interest(C4_channels)


C3_chans_of_interest_hbo =  ['S9_D13 hbo',
'S9_D18 hbo',
'S10_D13 hbo',
'S10_D16 hbo',
'S10_D19 hbo',
'S13_D18 hbo',
'S16_D13 hbo',
'S16_D16 hbo',
'S16_D18 hbo',
'S16_D19 hbo',
'S16_D23 hbo',
'S24_D19 hbo']
C3_chans_of_interest_hbr = [i.replace('hbo', 'hbr') for i in C3_chans_of_interest_hbo]

C4_chans_of_interest_hbo =  ['S11_D14 hbo',
'S11_D17 hbo',
'S11_D20 hbo',
'S12_D14 hbo',
'S12_D21 hbo',
'S17_D14 hbo',
'S17_D17 hbo',
'S17_D20 hbo',
'S17_D21 hbo',
'S17_D24 hbo',
'S18_D15 hbo',
'S25_D20 hbo']
C4_chans_of_interest_hbr = [i.replace('hbo', 'hbr') for i in C4_chans_of_interest_hbo]

DROP_CHANS = [
 'S2_D4 760',
 'S2_D4 850',

 'S2_D1 760',
 'S2_D3 760',
 'S3_D1 760',
 'S3_D4 760',
 'S31_D27 760',
 'S31_D30 760',
 'S28_D27 760',
 'S29_D28 760',
 'S32_D28 760',
 'S32_D31 760',
 'S2_D1 850',
 'S2_D3 850',
 'S3_D1 850',
 'S3_D4 850',
 'S31_D27 850',
 'S31_D30 850',
 'S28_D27 850',
 'S29_D28 850',
 'S32_D28 850',
 'S32_D31 850'
 ]

SPECIAL_DROP_CHANS = ['S31_D32 760',
                      'S32_D32 760',
                      'S31_D32 850',
                      'S32_D32 850',
                      ]
