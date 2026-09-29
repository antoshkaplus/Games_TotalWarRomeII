On Windows we need to install wsl.

# `venv`
python3 -m venv .venv

To add .venv directory to PYTHONPATH:
* open `venv/bin/activate`
* append to the bottom
```
export PYTHONPATH="$VIRTUAL_ENV:$PYTHONPATH"
```

Need command alias to open related dir and activate venv at the same time:
* open ~/.bash_aliases
* add 
```
alias toromeii=cd /home/anton_logunov/Documents/Games_TotalWarRomeII/py && source ./.venv/bin/activate
```

Install dependencies from `requirements.txt`:
```
pip install -r requirements.txt
```