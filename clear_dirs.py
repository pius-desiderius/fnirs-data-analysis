from meta import *
import shutil

if __name__ == '__main__':
    for i in dirs_to_save_stuff.values():
        shutil.rmtree(i)
