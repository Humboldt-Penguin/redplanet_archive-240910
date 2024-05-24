"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

------------
RedPlanet module `Craters.py` allows you to access coordinates, names, and diameters of Martian craters greater than 10km diameter.


###################################################################################
------------
METHODS:
------------
>>> Craters.get_database(minDiam=0, maxDiam=9999, dict=False):

Access a full/filtered database of Martian craters with diameter >=10km. 



>>> Craters.get(string):

Get all information for a crater based on its name or ID. Returns a dictionary with keys:
- 'ID'
- 'name'
- 'lat'
- 'lon'
- 'diameter_km'
- 'depth_rimfloor'
- 'num_layers'



###################################################################################
------------
REFERENCES:
------------
[These are copied from `Craters.py` docstrings -- see those for info on where/how each data is used.]

[1] Crater database:
    > Robbins, S.J., and B.M. Hynek (2012). A New Global Database of Mars Impact Craters ≥1 km: 1. Database Creation, Properties, and Parameters. Journal of Geophysical Research - Planets, 117, E05004. doi: 10.1029/2011JE003966.
    - We actually use a database uploaded to Kaggle in 2021 (https://www.kaggle.com/datasets/codebreaker619/mars-crater-study-dataset?resource=download). There is no associated citation, but it is attributed to Stuart Robbins. The database is nearly identical for craters >10km, with a few minor discrepencies and less columns (which are not used in this module anyway). We take the csv and remove all craters <10km to reduce size, then upload to Google Drive: https://drive.google.com/file/d/1s7I529s9J7E8e3iMTX1s-wXJQnw5nwlm/view?usp=sharing.



"""

from .Craters import *