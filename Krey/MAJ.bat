@echo off
chcp 65001
echo.
pushd %~dp0

net session >nul 2>&1
if NOT %errorLevel% == 0 (
    echo Ce script doit etre lance avec les privileges administrateur.
    echo Clique droit > Executer en tant qu'Administrateur.
    echo.
    PAUSE
    GOTO end  
)

::Recherche de Git et MAJ
git.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO gitmessage
echo Mise a jour du Bot en cours [...]
git stash
git pull

echo.
echo Mise � jour des dependances [...]
::Essaye de mettre a jour sans PATH
%SYSTEMROOT%\py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO attempt
%SYSTEMROOT%\py.exe -3.5 -m pip install --upgrade -r dependances.txt
PAUSE
GOTO end

::Avec PATH si �a ne fonctionne pas.
:attempt
py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO lastattempt
py.exe -3.5 -m pip install --upgrade -r dependances.txt
PAUSE
GOTO end

::En cas que �a fonctionne toujours pas...
:lastattempt
python.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO pythonmessage
python.exe -m pip install --upgrade -r dependances.txt
PAUSE
GOTO end

:pythonmessage
echo Aucune installation valide de Python trouv�e. Assurez-vous d'avoir Python 3.5 ou sup�rieur.
PAUSE
GOTO end

:gitmessage
echo Git n'a pas �t� install� ou est install� de fa�on incorrect. Avez-vous coch� "PATH" lors de son installation ?
PAUSE

:end