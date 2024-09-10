"""
Calculate the MD5 hash of a file from a URL, without downloading the entire file to disk.
"""

import hashlib
import requests
from tqdm import tqdm

def calculate_md5(url):
    md5_hash = hashlib.md5()
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=url.split('/')[-1])
        
        for chunk in response.iter_content(chunk_size=65_536):
            if chunk:
                md5_hash.update(chunk)
                progress_bar.update(len(chunk))
        
        progress_bar.close()
    else:
        raise Exception(f"Failed to download file: status code {response.status_code}")
    
    return md5_hash.hexdigest()



url = 'https://planetarymaps.usgs.gov/mosaic/Mars/HRSC_MOLA_Blend/Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif'
md5_hash = calculate_md5(url)
print(f"The MD5 hash of the file is: {md5_hash}")
