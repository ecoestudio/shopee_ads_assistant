@echo off

:: check git exists
IF NOT EXIST PortableGit (
  echo PortableGit folder does not exist.
  echo Running PortableGit-2.40.0-64-bit.7z.exe with force option.
  start "" "PortableGit-2.40.0-64-bit.7z.exe" force
) ELSE (
  echo PortableGit folder exists.
)
IF NOT EXIST .git (
  PortableGit\bin\git.exe init
  PortableGit\bin\git.exe add .
  PortableGit\bin\git.exe remote add origin https://github.com/ecoestudio/shopee_ads_assistant.git
  PortableGit\bin\git.exe remote update
  PortableGit\bin\git.exe checkout master
)
PortableGit\bin\git.exe reset --hard HEAD
PortableGit\bin\git.exe pull https://github.com/ecoestudio/shopee_ads_assistant.git --force

if not defined PYTHON (set PYTHON=python)
if not defined VENV_DIR (set "VENV_DIR=%~dp0%venv")


set ERROR_REPORTING=FALSE

mkdir tmp 2>NUL

%PYTHON% -c "" >tmp/stdout.txt 2>tmp/stderr.txt
if %ERRORLEVEL% == 0 goto :check_pip
echo Couldn't launch python
goto :show_stdout_stderr

:check_pip
%PYTHON% -mpip --help >tmp/stdout.txt 2>tmp/stderr.txt
if %ERRORLEVEL% == 0 goto :start_venv
if "%PIP_INSTALLER_LOCATION%" == "" goto :show_stdout_stderr
%PYTHON% "%PIP_INSTALLER_LOCATION%" >tmp/stdout.txt 2>tmp/stderr.txt
if %ERRORLEVEL% == 0 goto :start_venv
echo Couldn't install pip
goto :show_stdout_stderr

:start_venv
dir "%VENV_DIR%\Scripts\Python.exe" >tmp/stdout.txt 2>tmp/stderr.txt
if %ERRORLEVEL% == 0 goto :activate_venv

for /f "delims=" %%i in ('CALL %PYTHON% -c "import sys; print(sys.executable)"') do set PYTHON_FULLNAME="%%i"
echo Creating venv in directory %VENV_DIR% using python %PYTHON_FULLNAME%
%PYTHON_FULLNAME% -m venv "%VENV_DIR%" >tmp/stdout.txt 2>tmp/stderr.txt
if %ERRORLEVEL% == 0 goto :activate_venv
echo Unable to create venv in directory "%VENV_DIR%"
goto :show_stdout_stderr

:activate_venv
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
echo venv %PYTHON%
goto :check_packages

:check_packages
venv\Scripts\pip3.exe install -r requirements.txt

:skip_venv
goto :launch


:launch
%PYTHON% -m streamlit run main.py
pause
exit /b

:show_stdout_stderr
echo.
echo exit code: %errorlevel%

for /f %%i in ("tmp\stdout.txt") do set size=%%~zi
if %size% equ 0 goto :show_stderr
echo.
echo stdout:
type tmp\stdout.txt

:show_stderr
for /f %%i in ("tmp\stderr.txt") do set size=%%~zi
if %size% equ 0 goto :show_stderr
echo.
echo stderr:
type tmp\stderr.txt

:endofscript
echo.
echo Launch unsuccessful. Exiting.
pause