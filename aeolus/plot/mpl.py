"""Matplotlib-related utilities."""
import matplotlib.colors as mcolors
import numpy as np


class MidpointNormalize(mcolors.Normalize):
    """Normalise data around a midpoint."""

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        mcolors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # Ignoring masked values and all kinds of edge cases
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))
