# game_protoype_work
Aim is to create a python based game as a lame fast attemp to create something


pyenv: https://github.com/pyenv-win/pyenv-win
install with: 
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

Set the version of py env
pyenv local 3.11.8
pyenv global 3.11.8



Poetry:
poetry lock
del poetry lock
poetry env use 3.11
poetry init # This initialises package dependancy
poetry add <package_name> # Add the dependancy to your project
poetry install
poetry show


Steps:
1. Implement Database and structure for NOSQL
2. Create crawler class following builder pattern
