from collections import OrderedDict


M1_LEFT_ROI_HBO = [
  'S9_D6 hbo',
  'S9_D12 hbo',
  'S9_D13 hbo',
  'S9_D10 hbo',
  'S10_D13 hbo',
  'S6_D13 hbo',
  'S10_D16 hbo'
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
  'S15_D12 hbo',
  'S10_D19 hbo'
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
  'S11_D17 hbo'
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
  'S11_D20 hbo',
  'S18_D15 hbo'
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
    REMAINING=[
            REMAINING_LEFT_ROI_HBO, 
            REMAINING_LEFT_ROI_HBR,
            REMAINING_RIGHT_ROI_HBO,
            REMAINING_RIGHT_ROI_HBR,
            REMAINING_LEFT_ROI_HBO + REMAINING_LEFT_ROI_HBR,
            REMAINING_RIGHT_ROI_HBO + REMAINING_RIGHT_ROI_HBR],
    
    SMZ=[
            SMZ_LEFT_ROI_HBO, 
            SMZ_LEFT_ROI_HBR,
            SMZ_RIGHT_ROI_HBO,
            SMZ_RIGHT_ROI_HBR,            
            SMZ_LEFT_ROI, 
            SMZ_RIGHT_ROI]
)

different_hb = OrderedDict(
    hbo=[
            M1_LEFT_ROI_HBO, 
            S1_LEFT_ROI_HBO,
            SMZ_LEFT_ROI_HBO,  
    
            M1_RIGHT_ROI_HBO,
            S1_RIGHT_ROI_HBO,
            SMZ_RIGHT_ROI_HBO,
            
            REMAINING_LEFT_ROI_HBO, 
            REMAINING_RIGHT_ROI_HBO,
            ],
    hbr=[
            M1_LEFT_ROI_HBR, 
            S1_LEFT_ROI_HBR,
            SMZ_LEFT_ROI_HBR,
              
            
            M1_RIGHT_ROI_HBR,
            S1_RIGHT_ROI_HBR,
            SMZ_RIGHT_ROI_HBR,
            
            REMAINING_LEFT_ROI_HBR,
            REMAINING_RIGHT_ROI_HBR
            ])


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

porsche_colors = {
    'Black': '#0D0D0D',
    'White': '#F7F7F7',
    'Guards Red': '#C91111',
    'Carmine Red': '#960018',
    'Papaya': '#FFC173',
    'Racing Yellow': '#FFB400',
    'Speed Yellow': '#FFB400',
    'Signal Yellow': '#F5AB35',
    'Viper Green': '#2A7D4D',
    'Irish Green': '#00574C',
    'Gulf Blue': '#0087B8',
    'Miami Blue': '#22A0D4',
    'Sapphire Blue': '#004E7C',
    'Night Blue': '#0F3B5C',
    'Mexico Blue': '#00A1D6',
    'Riveria Blue': '#005D7E',
    'GT Silver Metallic': '#A0A0A0',
    'Agate Grey Metallic': '#828282',
    'Chalk': '#E8E8E8',
    'Crayon': '#A2A2A2',
    'Dolomite Silver Metallic': '#7A7A7A',
    'Jet Black Metallic': '#1D1D1D',
    'Mahogany Metallic': '#672023',
    'Moonlight Blue Metallic': '#202A44',
    'Night Blue Metallic': '#0F3B5C',
    'Quartzite Grey Metallic': '#717171',
    'Rhodium Silver Metallic': '#A0A0A0',
    'Sapphire Blue Metallic': '#004E7C',
    'Vulcano Grey Metallic': '#7E7E7E',
    'Crayon Metallic': '#A2A2A2',
    'Python Green': '#007C59',
    'Lava Orange': '#FF4E09',
    'Lizard Green': '#5D8B35',
    'Mamba Green': '#0C6E3D',
    'Mint Green': '#78A086',
    'Riviera Blue': '#005D7E'
}
