See this page for beginner Python advice.

---

If you're trying Python out and/or only plan on using Python a few times, I highly recommend the browser-based [Google Colab](https://colab.google/) (no downloads required). The benefits are:

- It's fairly fast, 
- You don't have to worry about any download/installation/setup, and everything can be reset by refreshing the page, 
- You have access to all pip-installable Python packages (common packages like `numpy`/`matplotlib`/`scipy`/etc. are already installed so you can import them directly; others like `redplanet` can be installed by running `!pip install redplanet` in a cell -- again, nothing will be downloaded on your local computer), 
- You can access files that you or others have uploaded to Google Drive ([more info here](https://colab.research.google.com/notebooks/io.ipynb)).

&nbsp;

---

If you'd like to install Python for more in-depth work, I've described my setup/advice/reasoning below (it's copy-pasted from messages to a friend, i just wanted somewhere to store it for sharing purposes).

...

For your actual python installation, you want a way to "containerize" (aka making separated "environments") the packages you're installing. For example, I have one environment for basic data science (numpy, matpotlib, scipy), i have one for software development (build, twine, gdown, pooch), one more machine learning (pytorch, cuda). There's often overlap between environments, but the idea is that you can keep everything separate and install/uninstall packages without fear of messing up your other environments, since the specific version of a package can oftentimes make/break certain features and functionality. 

The typical options for making environments are pip+venv, conda, and poetry. 
- poetry is unnecessarily complicated, obscure, and a bit buggy. 
- pip+venv is good for basics, however conda is better because...
- conda is what 95% of data scientists use because it lets you install more advanced packages that compile non-python code, which is especially helpful for machine learning. you can also pip install inside a conda environment so you're not losing any functionality. it's not ideal for software development (look up reddit threads of people comparing pip and conda), but it's great for our purposes of convenient personal data science/exploration.

You have a few options for conda, I'll explain them from worst to best. 
- You can install the Anaconda GUI, but that's a *horrible* idea -- if anyone tells you to install anaconda, you can safely disregard 99% of their programming-related advice/opinions. It's extremely bloated, slow, and encourages bad coding practices.
- You can install the Conda command line tool, which is better since it's smaller and teaches you the command line. However conda still comes with a lot of bloat.
- You can install Miniconda, which is like the Conda CLI tool but you're starting with minimal packages and install everything on top of that. However, installing packages can take forever. So...
- The best option is to install mambaforge, which is identical to conda but it's optimized to install packages significantly faster (often times an entire order of magnitude). Link is here: https://mamba.readthedocs.io/en/latest/installation.html

Additionally, if you're on Windows, I'd HIGHLY recommend setting up WSL (Windows Subsystem for Linux): https://learn.microsoft.com/en-us/windows/wsl/install and setting up Python there. It's a way to run a full Linux terminal but fully integrated with your Windows operating system (while oftentimes running faster than Windows itself), and although it has a bit of a learning curve for command line stuff, it's way better than the Windows command line and will serve you well in the future. The biggest benefit is that if you ever mess up an installation or run the wrong command, you can completely restart the Linux environment from scratch within a minute, rather than spending hours troubleshooting a Linux environment. ChatGPT is your friend here. 

================

when it comes to using mamba, i often refer to this cheatsheet: https://docs.conda.io/projects/conda/en/latest/_downloads/843d9e0198f2a193a3484886fa28163c/conda-cheatsheet.pdf (but you just replace every `conda` with `mamba`).

there are a lot of commands, but all you really have to know is:
- `mamba env list` -- lists all your environments
- `mamba create -n [envname] [package_1] [package_2] ...` creates a new environment and installs packages in there. for example, i might do `mamba create -n mars numpy matplotlib scipy pandas gdown`
- `mamba activate [envname]` -- activates an environment so you can run code in there
- `mamba remove -n [envname] --all` -- deletes an environment and all packages in there

there are some commands for exporting your environments, but avoid those. you should get in the habit of writing environment.yaml files by hand, they look like this:
```yaml
name: mars2
channels:
  - conda-forge
dependencies:
  - numpy
  - matplotlib
  - scipy
  - gdown
  - jupyterlab
  - pandas
```

you can install an environment directly from an environment.yaml file like the one above with the command `mamba env create --file [.yaml]`. tbh i can't remember if this works with the newer mamba but it should be fine. 


================

when it comes to editing code, you should really be using jupyter notebooks if you're in data science (installation instructions after this). the idea of a notebook is basically instead of a single, long script of code, you can separate your code into individaul "cells" and run them individually while saving the variables as you go. this is useful if you want to load a big dataset in one cell, and then experiment with plotting different variables/calculating things in another cell before cementing what you actually want to do. notebooks are amazing for exploring data as you go, and then eventually cleaning up your results so you can present them later on

here's an example of a notebook i include with a package i'm publishing, it gives a demo of all the features of my package https://github.com/Humboldt-Penguin/redplanet/blob/main/docs/notebooks/demo/demo.ipynb

but they don't always have to be that formal/clean, here's one of my notebooks that i just used for scrap coding, testing things, and exploring data https://github.com/Humboldt-Penguin/redplanet/blob/main/docs/notebooks/scrap/Crust/generate_crustalthickness_data.ipynb

================

now there are a few different formats for installing notebooks. 
- your main option is installing the jupyter package through mamba (or conda/pip). then you can use jupyter notebooks in vscode directly, which is really efficient. i'd highly highly highly recommend this, i can explain how to do this since it can be a bit finnicky if you don't know what you're doing (like choosing the interpreter/kernel). the main strengths of vscode is that you get great code linting, you can use github copilot, you get great version tracking with git, and much more. 
- if you don't want to use vscode, you can install `jupyterlab` instead of just `jupyter` which is a web-based editor made for notebooks. it's not as good as vscode but it's okay, i used it for a few weeks on a machine i couldn't install vscode onto.
- if you want your notebooks to stay web-based (which is perfectly fine tbh), you can use google colab. an analogy is that google colab is to jupyter notebooks like google docs is to microsoft word. colab is pretty sick for beginners if you don't want to mess around with installing stuff on your computer, and tbh it works fine for some pretty advanced stuff