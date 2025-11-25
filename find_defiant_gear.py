from os import path
from glob import glob
from shutil import copy2 as copyfile
from datetime import datetime

eqdir = "\\\\10.19.99.2\\deepend\\EQ Data"
invglob = "*_<servername>-Inventory.txt"
guildbankglob = '*_<servername>-GuildBank.txt'
realestateglob = '*_<servername>-RealEstate.txt'
localpath = "c:\\Users\\Public\\Daybreak Games\\Installed Games\\Everquest"

gear_levels = {
    'Crude':0,
    'Simple':5,
    'Rough':15,
    'Ornate':26,
    'Flawed':37,
    'Intricate':48,
    'Elaborate':59,
    'Elegant':70,
    'Extravagant':80 }
                    
def map_to_level(desc):
    words = desc.split(' ')
    try:
        lvl = gear_levels[words[0]]
        result = ' '.join([f"{lvl:03}",]+words[1:])
    except KeyError:
        result = desc
    return result
    
def map_type_to_number(desc):
    pass

def fn_to_chrsvr(filepath):
    return path.split(filepath)[1].split('-')[0].split('_')

def items_of_file(fn):
    with open(fn,"r") as invfile:
        header = invfile.readline().strip()
        for line in invfile:
            try:
                loc, desc, _, _, _ = line.strip().split('\t')
                if desc != 'Empty':
                    yield loc, desc
            except ValueError:
                pass

def items_of_realestate_file(fn):
    with open(fn,"r") as invfile:
        header = invfile.readline().strip()
        for line in invfile:
            try:
                _, _, desc, char, loc, _, _ = line.strip().split('\t')
                print(desc,char,loc)
                yield loc, desc, char
            except ValueError:
                pass

def extend_inventory(inventory, filename, chrname):
    inventory.extend([(chrname,loc,desc) for loc,desc in items_of_file(filename)])

def extend_inventory_realestate(inventory, filename):
    inventory.extend([(chrname,loc,desc) for loc,desc,chrname in items_of_realestate_file(filename)])

def build_inventory(filelist):
    items = []
    for fn in filelist:
        chrname,_ = fn_to_chrsvr(fn)
        extend_inventory(items, fn, chrname)
    return items

def output_gear_list(gearlist,outfilepath):
    gearlist.sort(key=lambda x: map_to_level(x[2]))
    with open(outfilepath,"w") as outfile:
        for item in gearlist:
            outfile.write(f"{item[2]:35}{item[0]:15}{item[1]}\n")

def get_yes_no(prompt,default):
    result = None
    while result == None:
        response = input(prompt)
        if response == "":
            result = default
        elif response.upper() in ["Y","YES"]:
            result = True
        elif response.upper() in ["N","NO"]:
            result = False
        else:
            print("Invalid response. Enter Y/Yes or N/No (case insensitive)\n")
    return result
    
def check_for_updated_files(localpath,remotepath,pattern):
    filetimestr = lambda x: datetime.fromtimestamp(x).strftime("%Y-%m-%d %I:%M %p")
    local_filelist = glob(path.join(localpath,pattern))
    for localfile in local_filelist:
        localfilename = path.split(localfile)[1]
        remotefile = path.join(remotepath,localfilename)
        localfiletime = path.getmtime(localfile)
        try:
            remotefiletime = path.getmtime(remotefile)
        except FileNotFoundError:
            remotefiletime = None
        if remotefiletime is None:
            copy_file = get_yes_no(f"File: \"{localfilename}\" {filetimestr(localfiletime)} is not on the server, copy it? (Y/n): ",True)
        else:
            print(f"File: \"{localfilename:25}\" local: {filetimestr(localfiletime)} remote: {filetimestr(remotefiletime)}")
            if remotefiletime < localfiletime:
                copy_file = get_yes_no(f"File: \"{localfilename}\" is newer than the file on the server, copy it? (Y/n): ",True)
            else:
                copy_file = False
        if copy_file:
            copyfile(localfile,remotepath)
    
def glob_files_of_server(apath,aglob,server):
    return glob(path.join(apath,aglob.replace('<servername>',server)))

if __name__ == "__main__":
    check_for_updated_files(localpath,eqdir,invglob.replace('<servername>','tunare'))
    check_for_updated_files(localpath,eqdir,guildbankglob.replace('<servername>','tunare'))
    check_for_updated_files(localpath,eqdir,realestateglob.replace('<servername>','tunare'))
    
    inv_file_list = glob_files_of_server(eqdir,invglob,'tunare')
    tunare_items = build_inventory(inv_file_list)

    guildbank_file_list = glob(path.join(eqdir,guildbankglob.replace('<servername>','tunare')))
    guildbank_file_list = glob_files_of_server(eqdir,guildbankglob,'tunare')
    guildbank_file_list.sort(key=lambda x:path.getmtime(x))
    extend_inventory(tunare_items, guildbank_file_list[-1], 'GuildBank')

    real_estate_filename = path.join(eqdir,"Nissan_tunare-RealEstate.txt")
    extend_inventory_realestate(tunare_items, real_estate_filename)

    defiant_gear = [item for item in tunare_items if item[2].find('Defiant') >= 0]
    combatants_gear = [item for item in tunare_items if item[2].find("Combatant's") >= 0]
    adepts_gear = [item for item in tunare_items if item[2].find("Adept's") >= 0]

    all_gear = defiant_gear + combatants_gear + adepts_gear
    output_gear_list(all_gear, "\\\\10.19.99.2\\deepend\\EQ Data\\equiplist.txt")
    