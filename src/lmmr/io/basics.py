# SPDX-License-Identifier: MIT
# Copyright (c) 2021 ETH Zurich, Luc Grosheintz-Laval

import json
import os
import pickle
import itertools
import csv
import hashlib

import lmmr


def random_hash(length=5):
    import numpy as np

    hash = hashlib.sha256(f"{np.random.randint(2**32-1)}".encode()).hexdigest()
    return hash[:length]


def symlink(src, dst, overwrite=False):
    if overwrite and os.path.islink(dst):
        os.unlink(dst)

    os.symlink(src, dst)


def first_non_existant(pattern):
    """Returns the first path which does not exist.

    Input:
        pattern: This is a format string containing one (integer) field.
    """
    dir_gen = (pattern.format(k) for k in itertools.count())
    return next(d for d in dir_gen if not os.path.exists(d))


def ensure_directory_exists(filename):
    dirname = os.path.dirname(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)


def read_array(filename, key, slices=None):
    import numpy as np
    import h5py

    with h5py.File(filename, "r") as h5:
        if slices is None:
            return np.array(h5[key])

        else:
            return np.array(h5[key][slices])


def read_something(filename, command, mode="r", **kwargs):
    with open(filename, mode, **kwargs) as f:
        return command(f)


def write_something(filename, command, mode="w", **kwargs):
    ensure_directory_exists(filename)
    with open(filename, mode=mode, **kwargs) as f:
        command(f)


def read_txt(filename):
    return read_something(filename, lambda f: f.read())


def write_txt(filename, string):
    write_something(filename, lambda f: f.write(string))


def read_json(filename):
    return read_something(filename, lambda f: json.load(f))


class NumpyEncoder(json.JSONEncoder):
    # credit: https://stackoverflow.com/a/47626762

    def default(self, obj):
        import numpy as np

        transforms = [
            (np.ndarray, lambda obj: obj.tolist()),
            (np.float16, lambda obj: float(obj)),
            (np.float32, lambda obj: float(obj)),
            (np.float64, lambda obj: float(obj)),
            (np.float128, lambda obj: float(obj)),
            (np.int16, lambda obj: int(obj)),
            (np.int32, lambda obj: int(obj)),
            (np.int64, lambda obj: int(obj)),
        ]

        for T, f in transforms:
            if isinstance(obj, T):
                return f(obj)

        return json.JSONEncoder.default(self, obj)


def write_json(filename, obj):
    write_something(filename, lambda f: json.dump(obj, f, indent=4, cls=NumpyEncoder))


def read_pickle(filename):
    return read_something(filename, lambda f: pickle.load(f), mode="rb")


def write_pickle(filename, obj):
    write_something(filename, lambda f: pickle.dump(obj, f), mode="wb")


def read_csv(filename, delimiter=","):
    def parse(f):
        reader = csv.DictReader(f, delimiter=delimiter)
        return [row for row in reader]

    return read_something(filename, parse, newline="", encoding="utf-8")


def savefig(filename, dpi=300, bbox_inches="tight", **kwargs):
    import matplotlib.pyplot as plt

    lmmr.io.ensure_directory_exists(filename)
    plt.savefig(filename, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
