conda create -y -v -n mudbot python=3.9
conda install --force-reinstall -y -q --name mudbot -c conda-forge --file requirements.txt
conda activate mudbot