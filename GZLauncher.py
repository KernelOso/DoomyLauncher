
# A basic multiplatform gzdoom launcher
#
# Copyright (C) 2025 - github.com/KernelOso
#
# This project is licensed under the MIT License.
# See the LICENSE file for details.

import json
import platform
import os
import sys
import re
import configparser
import subprocess
from dataclasses import dataclass
from typing import List

# error codes :
# 1 : no preset arg
# 2 : file doesn't exist
# 3 : more than one dynamic var on preset file


@dataclass
class CONFIG:
    scriptPath: str = ""
    
    presets_local_dir: str = "presets"

# gloabl config var
config:CONFIG = CONFIG()

configReader = configparser.ConfigParser()


def loadConfig():
    global config
    
    # get the Script Path
    config.scriptPath = os.path.dirname(os.path.abspath(__file__))
    
    configReader.read(os.path.join(config.scriptPath ,'config.cfg'))
    
    presets_local_dir = configReader.get('settings' , 'presets_local_dir' , fallback='')
    if presets_local_dir.strip():
        config.presets_local_dir = presets_local_dir

@dataclass
class PRESET:
    iwad: str
    mods: List[str]
    config: str
    saveDir: str
    
def verifyFile(file : str) -> str :
    if os.path.exists(file):
        return file
    else:
        print(f"ERROR : file doesn't exist : {file}")
        sys.exit(2)
    
def getPresetFile(arg: str) -> str:
    
    if "/" in arg or "\\" in arg:
        # absolute path arg mode   
        
        return verifyFile(arg)
     
    else:
        # local preset file mode
        
        # add ".json" at the end if arg doesn't have it
        if not arg.lower().endswith("json"):
            arg = arg + ".json"
            
        file = os.path.join(config.scriptPath , config.presets_local_dir , arg)
        
        return verifyFile(file)
     
def getVariablesPath(value: str) -> str:
    
    file = value
    
    if re.search(r"\{\{.*?\}\}", file):
        # the value has dynamic variable
        
        if len(re.findall(r"\{\{(.*?)\}\}", file)) > 1:
            print(f'ERROR : more than one dynamic var in : {file}')
            sys.exit(3)
    
        # get dynamic var name
        dynamicVar = re.search(r"\{\{(.*?)\}\}", file).group(1)
        
        # delete dynamic var
        file = re.sub(r"\{\{.*?\}\}", "", file)
        
        # build path
        if dynamicVar == "shareware":
            file = os.path.join( config.scriptPath , "shareware" , file )
        else:
            file = os.path.join(configReader.get(platform.system() , dynamicVar) , file)
        
        
        
        
    verifyFile(file)
    
    return file
     
def loadPreset(presetFilePath: str) -> PRESET:
    print(f"readding the file : {presetFilePath}")
    print("")
    
    with open(presetFilePath , 'r' , encoding='utf-8' )as openedFile:
        data = json.load(openedFile)
    
    # read each var
    iwad = getVariablesPath(data["iwad"])
    print(f"IWAD : {iwad}")
    
    mods = [getVariablesPath(mod) for mod in data["mods"]]
    print(f"MODS : {mods}")
    
    config = getVariablesPath(data["config"])
    print(f"CONFIG : {config}")
    
    saveDir = getVariablesPath(data["saveDir"])
    print(f"SAVE DIR : {saveDir}")
    
    print("")
    
    return PRESET(iwad=iwad , mods=mods , config=config , saveDir=saveDir)  
    
def main( ):
    print("starting")
    # exit when no arg passed
    if len(sys.argv) < 2:
        print("ERROR : no arg detected")
        sys.exit(1)
        
    # verify config
    loadConfig()
        
    # Get the arg
    arg = sys.argv[1]
    presetfile = getPresetFile(arg=arg)
    
    # get preset objetct 
    preset = loadPreset(presetFilePath=presetfile)
    
    gzdoomBin = f"{configReader.get(platform.system() , "gzDoomBin")}"
    iwad = f"\"{preset.iwad}\""
    mods = " ".join(f'"{mod}"' for mod in preset.mods)
    config = f"\"{preset.config}\""
    saveDir = f"\"{preset.saveDir}\""
    
    if not gzdoomBin == "":
        cmd = f"{gzdoomBin} -iwad {iwad} -file {mods} -config {config} -savedir {saveDir}"
        print(f"Command : {cmd}")
        subprocess.run(cmd , shell=True)
    else :
        os.startfile(iwad)
    
if __name__ == "__main__":
    main()