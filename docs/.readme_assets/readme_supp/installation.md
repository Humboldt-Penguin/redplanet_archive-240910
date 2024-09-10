# TODO: instructions for how to install various ways

# TODO: either link to this file or move all this info directly into the Makefile — in the main README, say that instructions for installing/modifying/etc are in the Makefile.

(use this as reference: https://github.com/MarkWieczorek/ctplanet/blob/master/docs/installation.rst)

---

If you want to modify the source code (for example, change plot titles or add new features):

1. Make a new python environment (virtualenv, conda/mamba env, etc).
    - e.g: `mamba create -n [env_name] python<3.12 pip`.
        - TODO: does python 3.12 work now (specifically pyshtools)? and if not, explain more in depth and in more places that you NEED an older version (python 3.11.9).
2. Clone the repository.
    - e.g.: `git clone https://github.com/Humboldt-Penguin/redplanet.git` (or download zip from github web page).
3. Install locally:
    - e.g.: `make install-dev` (shorthand for `pip install -e ".[dev]"`, see [`Makefile`](/Makefile) for more info).

Now you can make changes to the source code and they will be reflected immediately in your Python environment. If you're using Jupyter, you'll have to restart your kernel first.