"""
Written by Zain Kamal (zain.eris.kamal@rutgers.edu).
https://github.com/Humboldt-Penguin/redplanet

------------

This script allows you to remove nighttime data from the MAVEN magnetometer dataset as measured by solar zenith angle. Note that this is the second part of a series of scripts that reduces MAVEN data -- see `maven_reducer_1_altitude.py` for part 1.


This script only works with data that has been reduced by `maven_reducer_1_altitude.py`. Users can either:
    (1) Download and untar a dataset already reduced to <200 km altitude from Google Drive: https://drive.google.com/file/d/1SYZw2a6CsyDZ4kOHOxRal5067c9NO_cy/view?usp=sharing
    (2) Run `maven_reducer_1_altitude.py` themselves, although this is quite time/space intensive. See documentation in the file for more information. 


This script requires the *zipped* "MAVEN Insitu Key Parameters Data Collection" which provides solar zenith angles. Users can either:
    (1) Download from a Google Drive mirror, which is significantly faster and less prone to error: https://drive.google.com/file/d/1j5xTf1U7xnOoj1iL44q4zHbOqY0GYX-x/view?usp=sharing
    (2) Download from PDS: https://pds-ppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/maven.insitu.calibrated/data

Again, the insitu key parameters data should NOT be unzipped or else the script will not work. This is to the benefit of the user as zipping decreases folder size from ~130 GB to 11.5 GB. 


If you'd like to run this for a single .npy file, only use the code between the following lines: TODO
    start:
        `lines_to_skip = next((i for i, line in enumerate(fin_mag, start=1) if '0  0' in line), None) - 1`
            (set `fin_mag` to be the appropriate path to the data file)
    end:
        `np.save(fpath__reduced_file, dat_mag_sph)`
            (set `fpath__reduced_file` to be the appropriate path to the output file)
Note that you might have to make additional adjustments for paths and logging. These should be fairly trivial.


[Copied from `maven_reducer_1_altitude.py`:]

The final data are saved as .npy files that can be loaded with `np.load`. This returns an Nx7 np.ndarray, where N is the number of data points, and the columns are:
    0: decimal days [since 2014-10-10 00:00:00]
    1: longitude    [-180, 180]
    2: latitude     [-90, 90]
    3: elevation    [km]
    4: B_theta      [nt]
    5: B_phi        [nt]
    6: B_r          [nt]
Although .npy files can't be opened with a text editor, they are significantly smaller than a text file containing the same data (3x smaller) and can be loaded extremely quickly. If you'd like to use the data with a different language, you can first load it with Python (`np.load`) and then save it in a different format (`np.savetxt` for .txt or .csv, or `scipy.io.savemat` for matfiles). The code would look something like this, generated from ChatGPT: https://gist.github.com/Humboldt-Penguin/363f5e9bfe42ad4596f135217e8d1bee. This conversion will require Python, but if you don't want to install anything, you can use the browser-based Google Colab editor (https://colab.research.google.com/).


"""


############################################################################################################################################


from redplanet import utils

import numpy as np
import pandas as pd

import zipfile
import os
import io
from datetime import datetime, timedelta
import logging


# OPTIONAL -- make a beeping sound when done running. I think this only works on Windows.
try:
    import winsound 
    import time
except:
    pass



############################################################################################################################################
"""user inputs"""



min_sza = 110
'''
Minimum solar zenith that defines when "nighttime" begins/ends. 
'''



dirpath__mag = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\2_reduced\maven.mag.calibrated-pc-highres__filters=200km'
'''
Path to the folder of reduced data from `maven_reducer_1_altitude.py`. Users can either:
    (1) Download and untar a dataset already reduced to <200 km altitude from Google Drive: https://drive.google.com/file/d/1SYZw2a6CsyDZ4kOHOxRal5067c9NO_cy/view?usp=sharing
    (2) Run `maven_reducer_1_altitude.py` themselves, although this is quite time/space intensive. See documentation in the file for more information. 
'''



fpath__insituzip = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\1_raw\maven.insitu.calibrated.zip'
'''
Path to the *zipped* "MAVEN Insitu Key Parameters Data Collection" which provides solar zenith angles. Users can either:
    (1) Download from a Google Drive mirror, which is significantly faster and less prone to error: https://drive.google.com/file/d/1j5xTf1U7xnOoj1iL44q4zHbOqY0GYX-x/view?usp=sharing
    (2) Download from PDS: https://pds-ppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/maven.insitu.calibrated/data
'''



dirpath__reduced_parent = r'C:\Users\Eris\Documents\sync_local\00_Local\mars\data\maven\2_reduced'
'''
Path to the parent folder where the reduced data will be saved (only a single folder will be created called 'maven.mag.calibrated-pc-highres__filters=200km,sza90/').
'''




############################################################################################################################################
"""setup"""

# times
start_datetime = datetime.now()


# paths
x = os.path.basename(dirpath__mag)
max_altitude = int(x[ x.index('=')+1 : x.index('km') ])

fpath__insituzip = utils.getPath(fpath__insituzip)
dirpath__reduced_parent = utils.getPath(dirpath__reduced_parent)
dirpath__reduced = utils.getPath(dirpath__reduced_parent, f'maven.mag.calibrated-pc-highres__filters={max_altitude}km,sza{min_sza}')

os.makedirs(dirpath__reduced, exist_ok=False)


# logger
log_path = utils.getPath(dirpath__reduced, 'logs')
os.makedirs(log_path, exist_ok=True)
log_path = utils.getPath(log_path, f'log__{start_datetime.strftime("%y%m%d-%H%M")}.txt')

logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s [%(levelname)s] %(message)s",
    # format = "[%(asctime)s] %(message)s",
    format = "%(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler(log_path)  # Output to log file
    ]
)




logging.info(f'Running `maven_reducer_2_sza.py`.')
logging.info(f'\tFor more information, see https://github.com/Humboldt-Penguin/redplanet.')
logging.info('')
logging.info(f'Started running at {start_datetime.strftime("%m/%d/%Y %H:%M")}')
logging.info('')
logging.info(f'Saving logs to: \n\t{log_path}')
logging.info('')
logging.info(f'Initial altitude reduced data: \n\t{dirpath__mag}')
logging.info('')
logging.info(f'Reduced data directory: \n\t{dirpath__reduced}')
logging.info('')
logging.info('------------------------------------------------------------------------------------------')
logging.info('')



# get all paths to mag files
fpaths__mag = []
for root, dirs, fnames in os.walk(dirpath__mag):
    for fname in fnames:
        if fname.endswith('.npy'):
            fpaths__mag.append(utils.getPath(root, fname))


num_files = len(fpaths__mag)
logging.info(f'Found {num_files} files.')
logging.info('')
logging.info('')
pad_digits = len(str(num_files))



# the base of our iteration is every file in fpaths__mag, however we start by opening the zip folder since repeatedly reopening/closing is slow
with zipfile.ZipFile(fpath__insituzip, 'r') as insituzip:

    # begin processing each mag file
    num_processed = 0
    for i_fpath__mag, fpath__mag in enumerate(fpaths__mag):

        logging.info(f'Processing {i_fpath__mag:0{pad_digits}}/{num_files}...\t({os.path.basename(fpath__mag)})')

        checkpoint = datetime.now()


        year = int(fpath__mag[-14:-10])
        month = int(fpath__mag[-9:-7])
        day = int(fpath__mag[-6:-4])


        # get the corresponding insitu file
        fname__insitu = f'{year}/{month:02}/mvn_kp_insitu_{year}{month:02}{day:02}_v18_r03.tab'

        # note: sometimes it's 'v13' instead of 'v18', or some other small difference -- this shouldn't happen after 2014/10/10 (start of mag data collection), but we include this just in case
        if fname__insitu not in insituzip.namelist(): 
            phrase_match = f'{year}/{month:02}/mvn_kp_insitu_{year}{month:02}{day:02}'
            fname__insitu = [fname for fname in insituzip.namelist() if (phrase_match in fname and '.tab' in fname)]

            # if it's still not available, skip this mag file. 
            if not fname__insitu:
                logging.info(f'\t- WARNING: No insitu data available for {year}-{month:02}-{day:02}.')
                delta = datetime.now()-checkpoint
                logging.info(f'\t- This process took: {str(delta)}')
                logging.info('')
                continue
            else:
                fname__insitu = fname__insitu[0]
            


        with insituzip.open(fname__insitu) as fin_insitu:
            fin_insitu = io.TextIOWrapper(fin_insitu)

            # read the file and get start/stop indices of nighttime data
            dat_insitu = pd.read_csv(fin_insitu, comment='#', header=None, sep='\s+', usecols=(0,195-1), names=('time','sza'))

            dat_sza = dat_insitu['sza'].to_numpy()

            night_indices = []

            if (dat_sza[0] >= min_sza): # case 1: starting in nightside
                night_indices.append(0)

            for i in range(0, dat_sza.shape[0]-1):
                if (dat_sza[i] >= min_sza and dat_sza[i+1] < min_sza): # case 2: going from nightside to dayside
                    night_indices.append(i)
                elif (dat_sza[i] < min_sza and dat_sza[i+1] >= min_sza): # case 3: going from dayside to nightside
                    night_indices.append(i+1)

            if (dat_sza[-1] >= min_sza): # case 4: ending in nightside
                night_indices.append(dat_sza.shape[0]-1)

            ## note that the algorithm above sometimes includes duplicates (namely if the first sza is >=90 and the second  is <90), but this isn't really an issue for our purposes.


            # get the start/stop times (since 2014-10-10 00:00:00) of nighttime data
            dat_insitu = dat_insitu.loc[night_indices]

            night_range = dat_insitu['time'].tolist()

            for i in range(len(night_range)):
                # convert to datetime object
                night_range[i] = datetime.strptime(night_range[i], '%Y-%m-%dT%H:%M:%S')
                # convert to timedelta after data collection started on since 2014-10-10 00:00:00
                night_range[i] = night_range[i] - datetime(2014,10,10)
                # convert to decimal days
                night_range[i] = night_range[i].total_seconds() / (60 * 60 * 24)

            night_range = np.array(night_range).reshape(-1,2)



        # now that we have `night_range`, use this to filter the mag file    
        dat_mag = np.load(fpath__mag)

        night_mask = np.zeros_like(dat_mag[:,0], dtype=bool)
        for start, stop in night_range:
            night_mask = np.logical_or(night_mask, np.logical_and(dat_mag[:,0] >= start, dat_mag[:,0] <= stop))

        old_size = dat_mag.shape[0]
        dat_mag = dat_mag[night_mask]
        new_size = dat_mag.shape[0]


        # save the new mag file if anything is left
        if new_size == 0:
            logging.info(f'\t- No data left, will not save.')
        else:
            logging.info(f'\t- Percent reduction: {(old_size-new_size)/old_size*100:.5f}%')

            dirpath__reduced_file = utils.getPath(dirpath__reduced, f'{year}', f'{month:02}')
            os.makedirs(dirpath__reduced_file, exist_ok=True)
            fname__reduced_file = f'mvn_mag_{max_altitude}km,sza{min_sza}_{year}-{month:02}-{day:02}.npy'
            fpath__reduced_file = utils.getPath(dirpath__reduced_file, fname__reduced_file)
            
            np.save(fpath__reduced_file, dat_mag)

        num_processed += 1


        # logging.info(f'\t- This process took: {str(delta).split(".")[0]}')
        delta = datetime.now()-checkpoint
        logging.info(f'\t- This process took: {str(delta)}')
        logging.info('')

















logging.info('')
logging.info('')
logging.info('------------------------------------------------------------------------------------------')
logging.info('Summary (sanity check):')
logging.info(f'* {num_files} mag files to reduce.')
logging.info(f'* {num_processed} mag files saved.')

logging.info('')
if (num_files == num_processed):
    logging.info('All is well :> \t(according to num_files==num_saved)')
else:
    logging.info('Something went wrong :< \t(according to num_files==num_processed)\nThis probably means that an insitu file is not available for the corresponding mag file, which is possible. In that case, we ignore the entire mag file. Search the logs for for "WARNING: No insitu data available".')
logging.info('------------------------------------------------------------------------------------------')
logging.info('')



''' finish logging '''


end_datetime = datetime.now()
logging.info(f'Finished running at {end_datetime.strftime("%m/%d/%Y %H:%M")}')
delta = end_datetime-start_datetime
logging.info(f'(Total execution time: {str(delta).split(".")[0]})')


logging.shutdown()


# notify when done
try:
    for i in range(5):
        winsound.Beep(500, 1000)
        time.sleep(0.5)
except:
    pass