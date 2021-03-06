from django.conf import settings
import os

def files_lookup_from_ls(fsspec_ls_output):
    lookup = {}
    for x in fsspec_ls_output:
        if x['type'] == 'directory':
            continue
        shortname = os.path.basename(x['name'])
        if shortname[0] == '.' or shortname in settings.REGISTRAR_IGNORED_FILES:
            continue
        lookup[shortname] = x
    return lookup

def sorted_filenames(fsspec_ls_output):
    return list(sorted(files_lookup_from_ls(fsspec_ls_output).keys()))
