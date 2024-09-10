TODO: explain the purpose/meaning/use of `redplanet/docs/datasets/`. 

Explanation of files (sample):
    - Consider a sample dataset `planet.dat`.
        - `planet.dat/` is a directory containing files to recreate the dataset.
        - `planet.dat/README.md` is a text file giving background information.
        - `planet.dat/Dockerfile` is a Dockerfile to build a container with the dataset.
    (note every data file has a README in this repo, but we sometimes omit Dockerfiles if the raw data is not altered, and we sometimes omit the data file itself if it's too large to store in the repo in which case a cloud mirror is provided.)