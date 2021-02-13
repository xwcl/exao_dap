from django.conf import settings
import os

def sorted_filenames(fsspec_ls_output):
    files_only = (os.path.basename(x['name']) 
        for x in fsspec_ls_output 
        if x['type'] != 'directory')
    return list(sorted(filter(lambda x: x not in settings.REGISTRAR_IGNORED_FILES, files_only)))

