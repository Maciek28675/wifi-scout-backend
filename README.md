# How to run
## Create and activate virtual environment
``` powershell
Powershell:

python -m venv .venv
.venv/Scripts/activate
```
## Install dependencies
```Powershell
pip install -r requirements.txt
```

## Run local server
```Powershell
cd src/
uvicorn main:app --host 0.0.0.0 --port 8000
```