"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu). Last updated 06/28/2023.
https://github.com/Humboldt-Penguin/redplanet

...

RedPlanet module `GRS.py` allows you to get surface element concentrations derived from the 2001 Mar Odyssey Gamma Ray Spectrometer. The original data is defined in 5 degree bins, but this module allows you to calculate values at exact coordinates by linearly interpolating between the four nearest points. Both exact concentration and volatile-free (normalized to an H20/Cl/Si free basis) are available.

NOTE: The first time you import this module, it will take ~7 seconds to download data. It's only 1 MB, but we're downloading from the original source which is a bit slow. All subsequent loads will be much faster due to caching. 

...
USAGE:

    >>> from redplanet import GRS
    >>> help(GRS.visualize)
    >>> GRS.visualize('th')
    >>> help(GRS.getConcentration)

...

RESOURCES:
    - Source of raw data:
        - Paper: https://doi.org/10.1029/2022GL099235
        - Dataset: https://digitalcommons.lsu.edu/geo_psl/1/    

"""

from .GRS import *