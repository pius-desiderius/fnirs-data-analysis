import os

def fast_scandir(dirname):
    subfolders= [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders

def fast_scanfiles(dirname, contains=None):
    subfiles = [f.path for f in os.scandir(dirname) if f.is_file()]
    if contains != None:
        subfiles = [i for i in subfiles if contains in i ]
    return subfiles

def fast_scanfiles_subjfiles(dirname, contains=None):
    subfolders = fast_scandir(dirname)
    subfiles = []
    subfiles.extend(fast_scanfiles(dirname, contains=contains))
    for dirs in subfolders:
        subfiles.extend(fast_scanfiles(dirs, contains=contains))
    return subfiles

def popper(ids, ids_key):
    try:
        ids.pop(ids_key)
    except:
        pass