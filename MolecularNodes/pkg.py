import subprocess
import sys
import os
import site
from importlib.metadata import version
import bpy
import re
import requests
import platform
import pathlib

ADDON_DIR = pathlib.Path(__file__).resolve().parent
print(ADDON_DIR)

PYPI_MIRROR = {
    # the original.
    'Default':'', 
    # two mirrors in China Mainland to help those poor victims under GFW.
    'BFSU (Beijing)':'https://mirrors.bfsu.edu.cn/pypi/web/simple',
    'TUNA (Beijing)':'https://pypi.tuna.tsinghua.edu.cn/simple',
    # append more if necessary.

}

def get_pypi_mirror_alias(self, context, edit_text):
    return PYPI_MIRROR.keys()
    

def verify_user_sitepackages(package_location):
    if os.path.exists(package_location) and package_location not in sys.path:
        sys.path.append(package_location)


def verify(): 
    verify_user_sitepackages(site.getusersitepackages())


def run_pip(cmd, mirror='', timeout=600):
    # path to python.exe
    python_exe = os.path.realpath(sys.executable)
    if type(cmd)==list:
        cmd_list=[python_exe, "-m"] + cmd
    elif type(cmd)==str:
        cmd_list=[python_exe, "-m"] + cmd.split(" ")
    else:
        raise TypeError(f"Invalid type of input cmd.")
    if mirror and mirror.startswith('https'):
        cmd_list+=['-i', mirror]
    try:
        print("Running pip:")
        print(cmd_list)
        pip_result = subprocess.run(cmd_list, timeout=timeout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode()
        if ("fatal error: 'Python.h' file not found" in error_message) and (platform.system()== "Darwin") and ('arm' in platform.machine()):
            return("ERROR: Could not find the 'Python.h' header file in version of Python bundled with Blender.\n" \
                    "This is a problem with the Apple Silicon versions of Blender.\n" \
                    "Please follow the link to the MolecularNodes GitHub page to solve it manually: \n" \
                    "https://github.com/BradyAJohnston/MolecularNodes/issues/108#issuecomment-1429384983 ")
        else:
            return("Full error message:\n" + error_message)

def install(pypi_mirror=''):
    # Get PIP upgraded
    run_pip('ensurepip')
    run_pip('pip install --upgrade pip', mirror=PYPI_MIRROR[pypi_mirror])

    #install required packages
    try:
        stderr=run_pip(cmd=['pip', 'install', '-r', f'{ADDON_DIR}/requirements.txt'], mirror=PYPI_MIRROR[pypi_mirror])
        return stderr
    except:
        return("Error installing dependencies")

        

def available():
    verify()
    all_packages_available = True
    for module in ['biotite', 'MDAnalysis']:
        try:
            version(module)
        except Exception as e:
            all_packages_available = False
    return all_packages_available
