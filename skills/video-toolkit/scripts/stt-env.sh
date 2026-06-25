#!/bin/bash
# Source before running transcribe.py so faster-whisper (CTranslate2 >=4.5) finds cuDNN 9 in WSL.
# The #1 WSL gotcha: without this you get "Could not load libcudnn_ops.so.9". We point
# LD_LIBRARY_PATH at the pip-installed nvidia-*-cu12 wheels.
#   one-time install (user site):  python3 -m pip install --user faster-whisper nvidia-cublas-cu12 'nvidia-cudnn-cu12==9.*'
#   apt:                            sudo apt-get install -y tesseract-ocr
# Fallbacks if GPU/cuDNN still fails: export STT_DEVICE=cpu STT_COMPUTE=int8
#   (transcribe.py also auto-falls-back to CPU int8), or pin ctranslate2==4.4.0 for cuDNN 8.
# the nvidia-*-cu12 wheels are namespace packages (no __file__), so glob their lib dirs
# under both the user and system site-packages.
for _sp in $(python3 -c "import site,sys;print(site.getusersitepackages());print('\n'.join(site.getsitepackages()) if hasattr(site,'getsitepackages') else '')" 2>/dev/null); do
  for _d in "$_sp"/nvidia/*/lib; do
    [ -d "$_d" ] && export LD_LIBRARY_PATH="$_d:${LD_LIBRARY_PATH:-}"
  done
done
export STT_MODEL="${STT_MODEL:-small.en}"
export STT_DEVICE="${STT_DEVICE:-cuda}"
