#DEFINE SAMPLING RATE
SFREQ = 3

#DEFINE EPOCHS LIMITS
TMIN = float(-2.0)
TMAX = float(14.0)

#DEFINE EPOCHS LABELS
EPOCHS_LABEL_REST = 'REST'
EPOCHS_LABEL_SMR = 'SMR'

#DEFINE IDS TO POP
IDS_TO_POP = ["2.0", "33.0", "1.0", "2", "1", "33"]

#DEFINE BASELINE
BASELINE = (-1, 0.5)

curves_hb = 'hbo'

# #DEFINE EPOCHS DROPPING PARAMETERS
# SMR_LOWER_QUANTILE, SMR_UPPER_QUANTILE = 0.05, 0.95
# REST_LOWER_QUANTILE, REST_UPPER_QUANTILE = 0.05, 0.95


# #DEFINE PATHNAMES FOR DIRECTORIES
# DIRS_TO_SAVE_STUFF = dict(
#                             haemo_folder_path = r"./haemodynamics",
#                             haemo_folder_path_np = r"./haemodynamics_np",
#                             topo_hbo_path = r"./topomaps_hbo",
#                             topo_hbo_path_np = r"./topomaps_hbo_np",
#                             topo_hbr_path = r"./topomaps_hbr",
#                             topo_hbr_path_np = r"./topomaps_hbr_np",
#                             epochs_structure_path = r"./epochs_structure",
# )

#DEFINE PATHNAMES FOR DIRECTORIES
DIRS_TO_SAVE_STUFF = dict( 
                          epochs_folder = r"./epochs",
                          
                            haemo_folder_path = r"./haemodynamics",
                            haemo_folder_path_np = r"./haemodynamics_np",
                            
                            relation_path = r"./relation",
                            relation_path_np = r"./relation_np",
                            
                            topo_path = r"./topomaps",
                            topo_path_np = r"./topomaps_np",
                            
                            evokeds_ = r'./evokeds_np',
                            evokeds_rel = r'./evokeds_rel_np',
                            
                            topo_rel_path = r"./topomaps_rel",
                            topo_rel_path_np = r"./topomaps_rel_np",
                            
                            all_epochs = r'./all_epochs'
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

