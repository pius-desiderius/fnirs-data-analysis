from meta import *
import shutil

if __name__ == '__main__':
    for i in DIRS_TO_SAVE_STUFF.values():
        shutil.rmtree(i)
