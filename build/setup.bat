echo "Current Branch : %APPVEYOR_REPO_BRANCH%"
echo "Upgrading PIP"
python -m pip install --upgrade pip
echo "Installing Python dependencies"
pip install -r requirements.txt
pip install build\dependencies\pyWinhook-1.6.2-cp36-cp36m-win_amd64.whl