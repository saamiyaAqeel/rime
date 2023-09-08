import os


def ensuredir(pathname):
    """
    Ensure that the directory component of `pathname` exists.
    """

    dirname = os.path.dirname(pathname)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
