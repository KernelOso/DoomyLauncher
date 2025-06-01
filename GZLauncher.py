import platform
import subprocess
import sys
import json
import os
from dataclasses import dataclass
from typing import List

GZDOOM_BIN = 'D:\\Games\\0_Emulators\\GZDoom\\gzdoom.exe'
SAVEDIR_WIN_LINK = 'win_saves'
SAVEDIR_LNX_LINK = 'lnx_saves'

@dataclass
class FILE:
    dir: str
    file: str

@dataclass
class DOOM:
    iwad: FILE
    mods: List[FILE]
    config: str
    saveDir: str

def loadJson(file: str) -> DOOM:
    print(f"File to read : {file}.json")
    
    with open(file , 'r' , encoding='utf-8') as openedFile:
        data = json.load(openedFile)
        
    # construir el objeto
    iwad = FILE(**data["iwad"])
    mods = [FILE(**mod) for mod in data["mods"]]
    config = data["config"]
    saveDir = data["saveDir"]
    
    return DOOM(iwad=iwad , mods=mods , config=config , saveDir=saveDir)
    

def main() :
    #salir si no se ejeucta con argumento
    if len(sys.argv) < 2:
        print("no arg detected")
        sys.exit(1)
    
    # obtener el argumento
    arg = sys.argv[1]
    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path , f"{arg}.json")
    
    #Salir si no existe el archivo
    if not os.path.isfile(file):
        print("file doesn't exist!")
        sys.exit(2)
    
    
    # cargar configuracion
    doom = loadJson(file=file)
    
    # construir comando
    iwad = f'"{os.path.join(path , doom.iwad.dir , doom.iwad.file)}"'
    modsList = [ f'"{os.path.join(path, mod.dir, mod.file)}"' for mod in doom.mods ]
    mods = " ".join(modsList)
    saveHpv: str
    gzBin: str
    if platform.system() == "Windows":
        print("Windows")
        saveHpv = SAVEDIR_WIN_LINK
        gzBin = GZDOOM_BIN
    elif platform.system() == "Linux":
        print("Linux")
        saveHpv = SAVEDIR_LNX_LINK
        gzBin = "gzdoom"
    else:
        print("System not detected")
        saveHpv = ""
        gzBin = ""
    config = f'"{os.path.join(path , saveHpv , doom.config)}"'
    saveDir = f'"{os.path.join(path , saveHpv , doom.saveDir)}"'
    
    print("")
    print(f"IWAD : {iwad}")
    print(f"MODS : {mods}")
    print(f"CONFIG FILE : {config}")
    print(f"SAVE DIR : {saveDir}")
    print("")
    
    cmd = f'{gzBin} -iwad {iwad} -file {mods} -config {config} -savedir {saveDir}'
    print(cmd)
    subprocess.run(cmd , shell=True)

if __name__ == "__main__":
    main()
