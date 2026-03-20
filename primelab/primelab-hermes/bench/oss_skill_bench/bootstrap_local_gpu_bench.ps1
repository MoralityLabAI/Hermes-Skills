param(
    [string]$PythonExe = "C:\Python311\python.exe",
    [string]$VenvPath = ".venv-gpu"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $VenvPath)) {
    & $PythonExe -m venv $VenvPath --system-site-packages
}

$venvPython = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Missing venv interpreter at $venvPython"
}

& $venvPython -m pip install -e .
& $venvPython -m pip uninstall -y torch | Out-Null
& $venvPython -m pip install --upgrade --force-reinstall --no-deps transformers==4.57.3
& $venvPython -m pip install --upgrade --force-reinstall --no-deps huggingface-hub==0.36.0
& $venvPython -m pip install --upgrade --force-reinstall --no-deps "numpy<2"

Write-Host "BOOTSTRAP_OK"
& $venvPython -c "import torch, transformers, trl, peft, accelerate, bitsandbytes, datasets, huggingface_hub, numpy; print({'torch': torch.__version__, 'cuda': torch.cuda.is_available(), 'cuda_version': torch.version.cuda, 'transformers': transformers.__version__, 'trl': trl.__version__, 'peft': peft.__version__, 'accelerate': accelerate.__version__, 'bnb': bitsandbytes.__version__, 'datasets': datasets.__version__, 'hub': huggingface_hub.__version__, 'numpy': numpy.__version__})"
