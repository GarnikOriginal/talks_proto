#!/usr/bin/env bash
if [ -d "env" ]; then
  rm -r env
fi
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install opencv-python-headless
pip install PyQt5
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
pip install asyncqt
pip install tqdm
pip install scipy
pip install matplotlib
pip install PyYAML
pip install av
cd "modules/TDDFA_V2"
chmod 777 "build.sh"
./modules/TDDFA_V2/build.sh
cd ../..