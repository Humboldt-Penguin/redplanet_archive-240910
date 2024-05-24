# ——————————————————————————————— how to: install ———————————————————————————— #

WARNING: NEVER DIRECTLY INSTALL THIS ENVIRONMENT -- INSTEAD, UPDATE THE `pyproject.toml` AND INSTALL LOCALLY AGAIN!

    mamba create -n dev2 python<3.12 pip
    mamba activate dev2
    pip install -e ".[dev]"



# ——————————————————————————————— how to: export ————————————————————————————— #

commands:

    mamba list > YYMMDD-V_ENVNAME_env.txt
    mamba list --explicit > YYMMDD-V_ENVNAME_env-explicit.txt

* former gives versions of ALL packages, latter will only show explicitly installed versions (which doesn't include stuff gotten from pyproject.toml)





# —————————————————————————————— changelog: (?) —————————————————————————————— #

