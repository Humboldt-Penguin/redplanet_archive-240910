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

Get GRS-derived concentration/sigma of an element at a desired coordinate. Options are: ['al','ca','cl','fe','h2o','k','si','s','th'].



>>> GRS.visualize(
            element_name: str, 
            normalize=False, 
            quantity='concentration', 
            lon_bounds: tuple = (-180,180), 
            lat_bounds: tuple = (-60,60), 
            grid_spacing: float = 5,
            colormap='viridis',
            overlay=False,
            transparency_data=0.6,
            transparency_mola=0.9,
            figsize=(10,7)
        ):

Create a map of concentration/sigma for some element. Options are: ['al','ca','cl','fe','h2o','k','si','s','th'].

    

###################################################################################
------------
REFERENCES:
------------
[These are copied from `GRS.py` docstrings -- see those for info on where/how each data is used.]

2022_Mars_Odyssey_GRS_Element_Concentration_Maps:
    > Rani, A., Basu Sarbadhikari, A., Hood, D. R., Gasnault, O., Nambiar, S., & Karunatillake, S. (2022). 2001 Mars Odyssey Gamma Ray Spectrometer Element Concentration Maps. https://doi.org/https://doi.org/10.1029/2022GL099235
    - Data downloaded from https://digitalcommons.lsu.edu/geo_psl/1/
    - Data reuploaded to https://drive.google.com/file/d/1Z5Esv-Y4JAQvC84U-VataKJHIJ9OA4_8/view?usp=sharing for significantly increased downloading speeds

    
'Mars_HRSC_MOLA_BlendShade_Global_200mp_v2_resized-7.tif'
    > Fergason, R.L, Hare, T.M., & Laura, J. (2017). HRSC and MOLA Blended Digital Elevation Model at 200m. Astrogeology PDS Annex, U.S. Geological Survey.
    - Original download link: https://astrogeology.usgs.gov/search/map/Mars/Topography/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendShade_Global_200mp_v2
    - The original file is 5 GB which is unnecessarily high resolution. We downsample the file by reducing the width/height by a factor of 7. Maps with other reduction factors as well as the code to do so can be found here: https://drive.google.com/drive/u/0/folders/1SuURWNQEX3xpawN6a-LEWIduoNjSVqAF.

         
"""

from .GRS import *