#DEFINE SAMPLING RATE
SFREQ = 1

#DEFINE EPOCHS LIMITS
TMIN = float(-1)
TMAX = float(15.0)

#DEFINE EPOCHS LABELS
EPOCHS_LABEL_REST = 'REST'
EPOCHS_LABEL_SMR = 'SMR'

#DEFINE IDS TO POP
IDS_TO_POP = ["2.0", "33.0", "1.0", "2", "1", "33"]

#DEFINE BASELINE
BASELINE = (-1, 0)

#DEFINE EPOCHS DROPPING PARAMETERS
SMR_LOWER_QUANTILE, SMR_UPPER_QUANTILE = 0.05, 0.95
REST_LOWER_QUANTILE, REST_UPPER_QUANTILE = 0.05, 0.95

#DEFINE FAULTY CHANNELS TO DROP 
CHANNELS_TO_DROP = []
SPECIAL_CHANNELS_TO_DROP = []


#DEFINE PATHNAMES FOR DIRECTORIES
DIRS_TO_SAVE_STUFF = dict(
                            haemo_M1_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_M1",
                            haemo_M1_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_M1_np",
                            # haemo_M1_hbt_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_M1_hbt",
                            # haemo_M1_hbt_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_M1_hbt_np",
                            # haemo_M1_rel_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_M1_rel",
                            # haemo_M1_rel_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_M1_rel_np",
                            
                            haemo_S1_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_S1",
                            haemo_S1_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_S1_np",
                            # haemo_S1_hbt_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_S1_hbt",
                            # haemo_S1_hbt_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_S1_hbt_np",
                            # haemo_S1_rel_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_S1_rel",
                            # haemo_S1_rel_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_S1_rel_np",
                                                       
                            haemo_SMZ_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_SMZ",
                            haemo_SMZ_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_SMZ_np",
                            # haemo_SMZ_hbt_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_SMZ_hbt",
                            # haemo_SMZ_hbt_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_SMZ_hbt_np",
                            # haemo_SMZ_rel_folder_path = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_SMZ_rel",
                            # haemo_SMZ_rel_folder_path_np = r"/mnt/diskus/pictures and arrays fNIRS/haemodynamics_SMZ_rel_np",
                            
                            topo_hbo_path = r"/mnt/diskus/pictures and arrays fNIRS/topomaps_hbo",
                            topo_hbo_path_np = r"/mnt/diskus/pictures and arrays fNIRS/topomaps_hbo_np",
                            topo_hbr_path = r"/mnt/diskus/pictures and arrays fNIRS/topomaps_hbr",
                            topo_hbr_path_np = r"/mnt/diskus/pictures and arrays fNIRS/topomaps_hbr_np",
                            topo_hbt_path = r"/mnt/diskus/pictures and arrays fNIRS/topomaps_hbt",
                            topo_hbt_path_np = r"/mnt/diskus/pictures and arrays fNIRS/topomaps_hbt_np",
                            topo_rel_path = r"/mnt/diskus/pictures and arrays fNIRS/topomaps_rel",
                            topo_rel_path_np = r"/mnt/diskus/pictures and arrays fNIRS/topomaps_rel_np",
                            epochs_structure_path = r"./epochs_structure",
                            
                            
)


