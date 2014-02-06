import staging.settings as staging_settings
import os

import os.path


def staging_breadcrumbs(path, base=staging_settings.STAGING_IMPORT_DIR):
    """Returns the intermediate paths above this one as elements of a tuple."""
    crumbs = [("", "Root")]
    if path:
        dirs = path.split("/")
        recurse_path = ""
        for d in dirs:
            recurse_path = os.path.join(recurse_path, d)
            system_path = os.path.join(base, recurse_path)
            if os.path.exists(system_path) and os.path.isdir(system_path):
                crumbs.append((recurse_path, d))
            else:
                raise Exception("Directory not valid.")
    return crumbs


def staging_browse(path, base=staging_settings.STAGING_IMPORT_DIR):
    """Return all the subdirectories and files in path.

    The entries are returned as two lists of paths relative
    to base and filename in 2-tuples.
    """
    names = os.listdir(system_path)
    directories = []
    files = []

    for local_name in names:
        system_name = os.path.join(base, path, local_name)
        staging_name = os.path.join(path, local_name)

        if os.path.isdir(system_name):
            directories.append((staging_name, local_name))
        elif os.path.isfile(system_name):
            files.append((staging_name, local_name))
        else:
            # file is of unknown type
            pass

    return directories, files
