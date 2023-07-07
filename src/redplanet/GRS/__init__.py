"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

------------
RedPlanet module `GRS.py` allows you to get and plot surface element concentrations derived from the 2001 Mar Odyssey Gamma Ray Spectrometer. The original data is defined in 5 degree bins, but this module allows you to calculate values at exact coordinates by linearly interpolating between the four nearest points. Both exact concentration and volatile-free (normalized to an H20/Cl/Si free basis) are available.

NOTE: The first time you import this module, it will take ~7 seconds to download data. It's only 1 MB, but we're downloading from the original source which is a bit slow. All subsequent loads will be much faster due to caching. 


###################################################################################
------------
METHODS:
------------
>>> GRS.get(
            element_name: str, 
            lon: float, 
            lat: float, 
            normalize=False, 
            quantity='concentration'
        ) -> float:

Get GRS-derived concentration/sigma of an element at a desired coordinate.



>>> GRS.visualize(
            element_name: str, 
            normalize=False, 
            quantity='concentration', 
            lon_bounds: tuple = (-180,180), 
            lat_bounds: tuple = (-75,75), 
            grid_spacing: float = 5,
            colormap='jet'
        ):

Create a map of concentration/sigma for some element.



###################################################################################
------------
USAGE:
------------
    >>> from redplanet import GRS
    >>> help(GRS.visualize)
    >>> GRS.visualize('th')
    >>> GRS.visualize('th', quantity='sigma')
    >>> GRS.visualize('th', normalize=True)
    >>> GRS.visualize('th', normalize=True, lon_bounds=(-10,10), lat_bounds=(-10,10), grid_spacing=1)
    >>> help(GRS.get)

    

###################################################################################
------------
REFERENCES:
------------
[These are copied from `GRS.py` docstrings -- see those for info on where/how each data is used.]

2022_Mars_Odyssey_GRS_Element_Concentration_Maps:
    > Rani, A., Basu Sarbadhikari, A., Hood, D. R., Gasnault, O., Nambiar, S., & Karunatillake, S. (2022). 2001 Mars Odyssey Gamma Ray Spectrometer Element Concentration Maps. https://doi.org/https://doi.org/10.1029/2022GL099235
    - Data downloaded from https://digitalcommons.lsu.edu/geo_psl/1/
    - Data reuploaded to https://drive.google.com/file/d/1Z5Esv-Y4JAQvC84U-VataKJHIJ9OA4_8/view?usp=sharing for significantly increased downloading speeds

        
"""

from .GRS import *