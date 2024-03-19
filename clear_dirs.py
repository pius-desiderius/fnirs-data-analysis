from meta import *
import shutil
import os

if __name__ == '__main__':
    for i in DIRS_TO_SAVE_STUFF.values():
        shutil.rmtree(i)
    os.remove('../fnirs_infos/log_runtime.txt')