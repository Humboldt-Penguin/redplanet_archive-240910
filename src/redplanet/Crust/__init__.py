"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

------------
RedPlanet module `Crust.py` allows you to access and plot high-resolution data for topography, moho, crustal thickness, and crustal density. The original data is defined in 0.1 degree bins (can be increased up to 0.0346, but this is not recommended), and we let you calculate values at exact coordinates by liniearly interpolating between the four nearest points.

NOTE: The first time you import this module, it can take a few seconds to download data (~70 MB). All subsequent loads will be much faster due to caching. 



###################################################################################
------------
METHODS:
------------
>>> Crust.get(
            quantity: str, 
            lon: float, 
            lat: float
        ) -> float:

Get topography ('topo'), moho elevation ('moho'), crustal thickness ('thick'), or crustal density ('rho'/'density') at a specific coordinate. Units are km and kg/m^3.



>>> Crust.visualize(
            quantity: str, 
            lon_bounds: tuple = (-180,180), 
            lat_bounds: tuple = (-90,90),  
            grid_spacing: float = 1,
            colormap='',
            overlay=False,
            transparency_data=0.6,
            transparency_mola=0.9,
            figsize=(10,7)
        ):

Create a map of topography ('topo'), moho elevation ('moho'), crustal thickness ('thick'), or crustal density ('rho'/'density'). Model name is formatted f'{Reference_Interior_Model}-{insight_thickness}-{rho_south}-{rho_north}'.



>>> Crust.get_current_model(include_data=False) -> dict:

Get the current model parameters. Default is Khan2022-39-2900-2900 and grid spacing 0.1 degrees.



>>> Crust.load_model(
            RIM, 
            insight_thickness, 
            rho_north, 
            rho_south, 
            grid_spacing = -1, 
            suppress_model_error = False,
            suppress_grid_error = False,
        ) -> bool:

Load a moho and crustal thickness dataset based on the provided parameters. The data itself comes from a file of spherical harmonic coefficients which are downloaded/cached from a massive Google Drive folder.
        
A summary of all available models can be found here: https://docs.google.com/spreadsheets/d/1ZDILcSPdbXAFp60VfyC4xTZzdnAVhx_U/edit?usp=sharing&ouid=107564547097010500390&rtpof=true&sd=true, or by calling `Crust.peek_models()`. 



>>> Crust.load_topo(grid_spacing=0.1):

Loads a basic topography model. This is called automatically upon import, but can be called again if the user wants to change the grid spacing (not recommended). 

        

>>> Crust.get_model_name() -> str:

Get the name of the current model formatted '{Reference_Interior_Model}-{insight_thickness}-{rho_south}-{rho_north}'.



>>> Crust.peek_models():

Print a summary of all available models.



###################################################################################
------------
REFERENCES:
------------
[These are copied from `Crust.py` docstrings -- see those for info on where/how each data is used.]


Dichotomy coordinates:
    > Andrews-Hanna, J., Zuber, M. & Banerdt, W. The Borealis basin and the origin of the martian crustal dichotomy. Nature 453, 1212–1215 (2008). https://doi.org/10.1038/nature07011
    - The file itself ('dichotomy_coordinates-JAH-0-360.txt') is downloaded from 
        > Wieczorek, Mark A. (2022). InSight Crustal Thickness Archive [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6477509
        

"MarsTopo2600 is a 2600 degree and order spherical harmonic model of the shape of the planet Mars." - pyshtools documentation        
    > Wieczorek, Mark A. (2015). Spherical harmonic model of the shape of Mars: MarsTopo2600 [Data set]. Zenodo. https://doi.org/10.5281/zenodo.3870922
    The actual file, 'MarsTopo2600.shape.gz', is reuploaded to Google Drive for significantly increased downloading speeds (~10 seconds as opposed to 3 minutes).
    - Textbook:
        > Wieczorek, M.A. (2015). Gravity and Topography of the Terrestrial Planets, Treatise on Geophysics, 2nd edition, Oxford, 153-193, doi:10.1016/B978-0-444-53802-4.00169-X.
    

Raw data (spherical harmonic coefficients for the crust-mantle interface, i.e. Moho, with various parameters) as well as spreadsheet summarizing available models:
    > Wieczorek, Mark A. (2022). InSight Crustal Thickness Archive [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6477509
    - The process of converting this data into the pre-computed registry we use is explained here: https://gist.github.com/Humboldt-Penguin/6f3f6e7e375f68c1368d094b8fdb70f0
    - Original paper: 
        > Wieczorek, M. A., Broquet, A., McLennan, S. M., Rivoldini, A., Golombek, M., Antonangeli, D., et al. (2022). InSight constraints on the global character of the Martian crust. Journal of Geophysical Research: Planets, 127, e2022JE007298. https://doi.org/10.1029/2022JE007298

        
'Mars_HRSC_MOLA_BlendShade_Global_200mp_v2_resized-7.tif'
    > Fergason, R.L, Hare, T.M., & Laura, J. (2017). HRSC and MOLA Blended Digital Elevation Model at 200m. Astrogeology PDS Annex, U.S. Geological Survey.
    - Original download link: https://astrogeology.usgs.gov/search/map/Mars/Topography/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendShade_Global_200mp_v2
    - The original file is 5 GB which is unnecessarily high resolution. We downsample the file by reducing the width/height by a factor of 7. Maps with other reduction factors as well as the code to do so can be found here: https://drive.google.com/drive/u/0/folders/1SuURWNQEX3xpawN6a-LEWIduoNjSVqAF.



"""

from .Crust import *