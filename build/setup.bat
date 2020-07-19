echo "Current Branch : %APPVEYOR_REPO_BRANCH%"
echo "Upgrading PIP"
python -m pip install --upgrade pip
echo "Installing Python dependencies"
pip install -r requirements.txt