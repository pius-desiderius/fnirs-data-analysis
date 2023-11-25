from collections import OrderedDict


M1_LEFT_ROI_HBO = [
  'S9_D6 hbo',
  'S9_D12 hbo',
  'S9_D13 hbo',
  'S9_D10 hbo',
  'S10_D13 hbo',
  'S6_D13 hbo',
]
M1_LEFT_ROI_HBR = [i.replace('hbo', 'hbr') for i in M1_LEFT_ROI_HBO]
M1_LEFT_ROI = M1_LEFT_ROI_HBO + M1_LEFT_ROI_HBR

S1_LEFT_ROI_HBO = [
  'S15_D18 hbo',
  'S16_D18 hbo',
  'S16_D19 hbo',
  'S16_D23 hbo',
  'S20_D18 hbo',
  'S19_D18 hbo',
  'S23_D18 hbo',
]
S1_LEFT_ROI_HBR = [i.replace('hbo', 'hbr') for i in S1_LEFT_ROI_HBO]
S1_LEFT_ROI = S1_LEFT_ROI_HBO + S1_LEFT_ROI_HBR

REMAINING_LEFT_ROI_HBO = [
  'S13_D12 hbo',
  'S13_D18 hbo',
  'S9_D18 hbo',
  'S16_D16 hbo',
  'S16_D13 hbo',
  'S10_D16 hbo',
]
REMAINING_LEFT_ROI_HBR = [i.replace('hbo', 'hbr') for i in REMAINING_LEFT_ROI_HBO]
REMAINING_LEFT_ROI = REMAINING_LEFT_ROI_HBR + REMAINING_LEFT_ROI_HBO


SMZ_LEFT_ROI_HBO = S1_LEFT_ROI_HBO + M1_LEFT_ROI_HBO + REMAINING_LEFT_ROI_HBO
SMZ_LEFT_ROI_HBR = S1_LEFT_ROI_HBR + M1_LEFT_ROI_HBR + REMAINING_LEFT_ROI_HBR
SMZ_LEFT_ROI = S1_LEFT_ROI + M1_LEFT_ROI + REMAINING_LEFT_ROI

######################

M1_RIGHT_ROI_HBO = [
  'S12_D9 hbo',
  'S12_D15 hbo',
  'S12_D11 hbo',
  'S11_D14 hbo',
  'S12_D14 hbo',
  'S7_D14 hbo',
]
M1_RIGHT_ROI_HBR = [i.replace('hbo', 'hbr') for i in M1_RIGHT_ROI_HBO]
M1_RIGHT_ROI = M1_RIGHT_ROI_HBO + M1_RIGHT_ROI_HBR

S1_RIGHT_ROI_HBO = [
  'S18_D21 hbo',
  'S17_D21 hbo',
  'S17_D20 hbo',
  'S17_D24 hbo',
  'S21_D21 hbo',
  'S26_D21 hbo',
  'S22_D21 hbo',
]
S1_RIGHT_ROI_HBR = [i.replace('hbo', 'hbr') for i in S1_RIGHT_ROI_HBO]
S1_RIGHT_ROI = S1_RIGHT_ROI_HBO + S1_RIGHT_ROI_HBR

REMAINING_RIGHT_ROI_HBO = [
  'S14_D15 hbo',
  'S14_D21 hbo',
  'S12_D21 hbo',
  'S17_D14 hbo',
  'S17_D17 hbo',
  'S11_D17 hbo',
]
REMAINING_RIGHT_ROI_HBR = [i.replace('hbo', 'hbr') for i in REMAINING_RIGHT_ROI_HBO]
REMAINING_RIGHT_ROI = REMAINING_RIGHT_ROI_HBR + REMAINING_RIGHT_ROI_HBO

SMZ_RIGHT_ROI_HBO = S1_RIGHT_ROI_HBO + M1_RIGHT_ROI_HBO + REMAINING_RIGHT_ROI_HBO
SMZ_RIGHT_ROI_HBR = S1_RIGHT_ROI_HBR + M1_RIGHT_ROI_HBR + REMAINING_RIGHT_ROI_HBR
SMZ_RIGHT_ROI = S1_RIGHT_ROI + M1_RIGHT_ROI + REMAINING_RIGHT_ROI

different_roi = OrderedDict(
    M1=[
            M1_LEFT_ROI_HBO, 
            M1_LEFT_ROI_HBR,
            M1_RIGHT_ROI_HBO,
            M1_RIGHT_ROI_HBR,
            M1_LEFT_ROI,
            M1_RIGHT_ROI
            ],
    S1=[
            S1_LEFT_ROI_HBO, 
            S1_LEFT_ROI_HBR,
            S1_RIGHT_ROI_HBO,
            S1_RIGHT_ROI_HBR,
            S1_LEFT_ROI, 
            S1_RIGHT_ROI
            ],
    SMZ=[
            SMZ_LEFT_ROI_HBO, 
            SMZ_LEFT_ROI_HBR,
            SMZ_RIGHT_ROI_HBO,
            SMZ_RIGHT_ROI_HBR,            
            SMZ_LEFT_ROI, 
            SMZ_RIGHT_ROI]
)


DROP_CHANS = [
 'S2_D4 760',
 'S2_D4 850',
#  'S2_D1 760',
#  'S2_D3 760',
#  'S3_D1 760',
#  'S3_D4 760',
#  'S31_D27 760',
#  'S31_D30 760',
#  'S28_D27 760',
#  'S29_D28 760',
#  'S32_D28 760',
#  'S32_D31 760',
#  'S2_D1 850',
#  'S2_D3 850',
#  'S3_D1 850',
#  'S3_D4 850',
#  'S31_D27 850',
#  'S31_D30 850',
#  'S28_D27 850',
#  'S29_D28 850',
#  'S32_D28 850',
#  'S32_D31 850'
 ]

##################################

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



