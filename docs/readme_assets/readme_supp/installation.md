TODO: instructions for how to install various ways 

(use this as reference: https://github.com/MarkWieczorek/ctplanet/blob/master/docs/installation.rst)

---

If you want to include Jupyter or JupyterLab, use `pip install "redplanet[jupyter]"` or `pip install "redplanet[jupyterlab]"`, respectively. 

---

If you want to modify the source code (for example, change plot titles or add new features), you can make a new environment, clone the repository, and install the package in editable mode:

```bash
git clone https://github.com/Humboldt-Penguin/redplanet.git
cd redplanet
pip install -e .
```

Now you can make changes to the source code and they will be reflected immediately in your Python environment. If you're using Jupyter, you'll have to restart your kernel first.