self note: consider modifying code such that we start with a jupyter notebook, then run:
    ```
    jupyter nbconvert notebook.ipynb --to script
    ```
to convert it to a plain python script that is then imported to docker and run.

the benefit is that i can do my development/display/presentation in jupyter (that way for anyone or myself who want to better understand the code but don't necessarily want to go through all the effort of manually reproducing, we can just peek at the notebook and learn a lot from the superior presentation, notes, and annotations!!!)
