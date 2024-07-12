# Create Python .venv

```bash
python3.11 -m venv .venv
```

```bash
source .venv/bin/activate

# install requirements
pip install -r requirements.txt
```


# TODO:
- Split packages: https://packaging.python.org/en/latest/guides/packaging-namespace-packages/#legacy-namespace-packages


aidmepy



# Log format

## Easy to read and use with vscode:
```python
from loguru import logger as log

log.remove()
log.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
```

## More compact

without time stamp:
```python
from loguru import logger as log

log.remove()
log.add(sys.stdout, format="<level>{level: <8}</level> | "
    "<cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
```

# Mkdocs 

## Install
```bash
pip install mkdocs-material
```

## Run
```bash
mkdocs serve
```
