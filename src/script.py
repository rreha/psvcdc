# lets import necessary modules plz

import os
import time
import sys
import zipfile
import subprocess
import shutil

# funcs!!1!!

def detect_type():
    global cont_id
    if os.path.isdir(input_f):
        print(">    Folder detected")
        cont_id = input_f
        return
        
    if os.path.isfile(input_f):
        print(">    File detected")
        pkgjob()
        
    else:
        print("ERROR!!! Couldn't detect if input is a file or a folder. Maybe it doesn't exist? Please run the program again.")
        os.system("PAUSE")
        exit()

def find_zip():
    global extractedpkg
    for file in os.listdir("./"):
        if file.endswith(".zip"):
            extractedpkg = os.path.join("./", file)
            print("\n>    Found zip: ", extractedpkg)
    return
    
def extract_zip():
    with zipfile.ZipFile(extractedpkg, 'r') as zip_ref:
        zip_ref.extractall("./")
    print(">    Extracted the zip")
    os.remove(extractedpkg)
    return
    
def organize_cont():
    global content
    for folder in os.listdir("./"):
        if folder == "app":
            print(">    Detected Game (app)")
            for f in os.listdir("./app/"):
                src = os.path.join("./app", f)
                dest = os.path.join("./", f)
                shutil.move(src, dest)
            os.rmdir("./app")
            content = "Game"
            return
            
        if folder == "patch":
            print(">    Detected Game Update (patch)")
            for f in os.listdir("./patch/"):
                src = os.path.join("./patch", f)
                dest = os.path.join("./", f)
                shutil.move(src, dest)
            os.rmdir("./patch")
            content = "Update"
            return
            
        if folder == "addcont":
            print(">    Detected DLC (addcont)")
            for f in os.listdir("./addcont/"):
                src = os.path.join("./addcont", f)
                dest = os.path.join("./", f)
                shutil.move(src, dest)
            os.rmdir("./addcont")
            content = "DLC"
            return
    return
            
def pkgjob():
    global cont_id
    cont_id = ""
    if os.path.splitext(input_f)[1] == ".pkg":
        print(">    File is a .pkg")
        print(">    Running pkg2zip...\n")
        subprocess.run(["./bin/pkg2zip.exe", "-x", input_f])
        organize_cont()
        print(">    Cleaned up files")
        for f in os.listdir("./"):
            if f.startswith("PC"):
                cont_id = str(f)
                print(">    Found content ID:", cont_id)
    else:
        print("ERROR!!! Please make sure that the specified file is a .pkg file.")
        os.system("PAUSE")
        exit()
    return
    
def get_zRIF():
    if cont_id == "" or None:
        print("ERROR!!! Couldn't detect content ID. pkg2zip might not be able to extract the pkg. Try running the program again.")
        os.system("PAUSE")
        exit()
        
    zrif = input(">    Enter the zRIF key for your content ({}) : ".format(cont_id))
    if os.path.exists("./decrypted_content"):
        print(">    Found decrypted_content folder")
    else:
        print(">    Creating decrypted_content folder")
        os.mkdir("./decrypted_content")
    print(">    Running psvpfsparser...\n")
    subprocess.run(["./bin/psvpfsparser/psvpfsparser.exe", "-i", "./{}".format(cont_id), "-o", "./decrypted_content/{}".format(cont_id),"-f", "cma.henkaku.xyz", "-z", zrif])
    print("\n>    Saved decrypted content to ./decrypted_content/{}.".format(cont_id))
    return

    
# main

print("PS Vita Content DeCryptor v1.1.0a ~ https://github.com/rreha/psvcdc\n")
try:
    global input_f
    input_f = sys.argv[1] 
    print(">    Input:", input_f)
    
except IndexError:
    print("Please specify a .pkg file or folder (PS Vita)")
    os.system("PAUSE")
    exit()
 
detect_type()
get_zRIF()

print(">    Exiting...")
os.system("PAUSE")
exit()
