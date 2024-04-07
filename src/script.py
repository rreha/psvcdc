# lets import necessary modules plz

import os
import time
import sys
import subprocess
import shutil
import openpyxl

# funcs!!1!!

def detect_type():
    global cont_id
    if os.path.isdir(input_f):
        print(">    Folder detected")
        index = input_f.find("PCS")
        if index != -1:  
            cont = input_f[index:]
            cont_id = cont.strip()
            return
            
        else:  
            print("ERROR!!! Couldn't index the input folder. Make sure that it's formatted like PCSXXXXXX.")          
            os.system("PAUSE")
            exit()
        
    if os.path.isfile(input_f):
        print(">    File detected")
        pkgjob()
        
    else:
        print("ERROR!!! Couldn't detect if input is a file or a folder. Maybe it doesn't exist? Please run the program again.")
        os.system("PAUSE")
        exit()
    
def organize_cont():
    global content
    global db_sheet
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
            #db_sheet = "DLC"
            return
    return
            
def pkgjob():
    global cont_id
    cont_id = ""
    flag = False
    if os.path.splitext(input_f)[1] == ".pkg":
        print(">    File is a .pkg")
        print(">    Running pkg2zip...\n")
        subprocess.run(["./bin/pkg2zip.exe", "-x", input_f])
        organize_cont()
        print(">    Cleaned up files")
        
        for f in os.listdir("./"):
            if flag == False and f.startswith("PC") and not f.endswith(".pkg"):
                cont_id = str(f)
                print(">    Found content ID:", cont_id)
                flag = not flag
                
    else:
        print("ERROR!!! Please make sure that the specified file is a .pkg file.")
        os.system("PAUSE")
        exit()
    return
    
def get_zRIF():
    print(">    Finding zRIF key for", cont_id, "(might take a bit)")
    if cont_id == "" or None:
        print("ERROR!!! Couldn't detect content ID. pkg2zip might not be able to extract the pkg. Try running the program again.")
        os.system("PAUSE")
        exit()
        
    db_sheet = "GAMES"
    search = cont_id
    zrif = None
    
    wb = openpyxl.load_workbook("db.xlsx")
    sheet = wb[db_sheet]
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value == search:
                next_cell = sheet.cell(row=cell.row, column=cell.column + 7)
                zrif = next_cell.value
                break
        if zrif is not None:
            break

    if zrif is not None:
        print(f'>    Found zRIF ({zrif})')
    else:
        print("ERROR!!! Couldn't find zRIF!")
        os.system("PAUSE")
        exit()
        
        
    #zrif = input(">    Enter the zRIF key for your content ({}) : ".format(cont_id))
    if os.path.exists("./DECRYPTED"):
        print(">    Found DECRYPTED folder")
    else:
        print(">    Creating DECRYPTED folder")
        os.mkdir("./DECRYPTED")
    print(">    Running psvpfsparser...\n")
    subprocess.run(["./bin/psvpfsparser/psvpfsparser.exe", "-i", "./{}".format(cont_id), "-o", "./DECRYPTED/{}".format(cont_id),"-f", "cma.henkaku.xyz", "-z", zrif])
    print("\n>    Saved decrypted content to /DECRYPTED/{}.".format(cont_id))
    return

    
# main

print("PS Vita Content DeCryptor v2.0.0a ~ https://github.com/rreha/psvcdc\n")
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
