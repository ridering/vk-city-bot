import os


def fullname(name):
    return os.path.join(os.path.dirname(__file__), '..', name)
