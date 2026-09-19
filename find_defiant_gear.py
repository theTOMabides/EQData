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
    'Extravagant':80
}

accounts = {
    'trocplayer': ('Ghorkxon', 'Nissan', 'Tjarlins', 'Todbo'),
    'oguzq': ('Antoneus', 'Yedrick'),
    'osakatoome': ('Gunthur', 'Oguz', 'Ondray', 'Tarzansson'),
    'goodsmeagol': ('Djaden', 'Ultrious', 'Vondoor'),
    'myextras': ('Xygoat', 'Llogurt')
}
                    
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

def map_player_to_account(player):
    for account,players in accounts.items():
        if player in players:
            return account
    return None

def fn_to_chrsvr(filepath):
    return path.split(filepath)[1].split('-')[0].split('_')

def file_includes_personal_depot(fn):
    with open(fn, "r") as invfile:
        header = invfile.readline().strip()
        for line in invfile:
            try:
                loc, _, _, _, _ = line.strip().split('\t')
                if loc.startswith('Personal-Depot'):
                    return True
            except ValueError:
                pass
    return False

def items_of_file(fn, incl_personal = True, incl_shared_bank = False, incl_personal_depot = False):
    with open(fn,"r") as invfile:
        header = invfile.readline().strip()
        for line in invfile:
            try:
                loc, desc, _, count, _ = line.strip().split('\t')
                if desc == 'Empty':
                    include_it = False
                elif loc.startswith('SharedBank'):
                    include_it = incl_shared_bank
                elif loc.startswith('Personal-Depot'):
                    include_it = incl_personal_depot
                else:
                    include_it = incl_personal
                if include_it:
                    yield loc, desc, count
            except ValueError:
                pass

def items_of_realestate_file(fn):
    with open(fn,"r") as invfile:
        header = invfile.readline().strip()
        for line in invfile:
            try:
                _, _, desc, char, loc, _, _ = line.strip().split('\t')
                # print(desc,char,loc)
                yield loc, desc, char
            except ValueError:
                pass

def extend_inventory(inventory, filename, chrname, incl_personal = True, incl_shared_bank = False, incl_personal_depot = False):
    inventory.extend([(chrname,loc,desc,count) for loc,desc,count in items_of_file(filename, incl_personal, incl_shared_bank, incl_personal_depot)])

def extend_inventory_realestate(inventory, filename):
    inventory.extend([(chrname,loc,desc,1) for loc,desc,chrname in items_of_realestate_file(filename)])

def build_inventory(filelist):
    items = []
    most_recent_shared_bank_sources = dict([(acct,(None,None)) for acct in accounts])
    most_recent_personal_depot_sources = dict([(acct,(None,None)) for acct in accounts])
    for fn in filelist:
        chrname,_ = fn_to_chrsvr(fn)
        filetime = path.getmtime(fn)
        account = map_player_to_account(chrname)
        if account is not None:
            if most_recent_shared_bank_sources[account][0] is None or most_recent_shared_bank_sources[account][1] < filetime:
                most_recent_shared_bank_sources[account] = (fn,filetime)
            if file_includes_personal_depot(fn):
                if most_recent_personal_depot_sources[account][0] is None or most_recent_personal_depot_sources[account][1] < filetime:
                    most_recent_personal_depot_sources[account] = (fn,filetime)
        extend_inventory(items, fn, chrname)
    for acct, (fn, _) in most_recent_shared_bank_sources.items():
        if fn is not None:
            print(f"Extending inventory with most recent shared bank file for account {acct}: {fn}")
            extend_inventory(items, fn, acct, incl_personal = False, incl_shared_bank = True)
    for acct, (fn, _) in most_recent_personal_depot_sources.items():
        if fn is not None:
            print(f"Extending inventory with most recent personal depot file for account {acct}: {fn}")
            extend_inventory(items, fn, acct, incl_personal = False, incl_shared_bank = False, incl_personal_depot = True)  
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

def stray_depot_items_report(depot_items_not_in_depot):
    prev_char = None
    prev_loc_base = None
    for item in depot_items_not_in_depot:
        if item[1] != prev_char:
            print(f"\n{item[1]}'s inventory:")
            prev_char = item[1]
            prev_loc_base = None
        loc = item[2].split('-')
        loc_base = loc[0]
        if loc_base != prev_loc_base:
            print(f"  {loc_base}:")
            prev_loc_base = loc_base
        print(f"    {"-".join(loc[1:]):20} {item[0]:35} x{item[3]}")        

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

    depot_items = [desc for _,loc,desc,_ in tunare_items if loc.startswith('Personal-Depot')]
    depot_items_not_in_depot = [(desc,char,loc,count) for char,loc,desc,count in tunare_items if desc in depot_items and not loc.startswith('Personal-Depot')]
    stray_depot_items_report(depot_items_not_in_depot)

    print(f"Total items found in tunare inventories outside depot: {len(depot_items_not_in_depot)}")
    defiant_gear = [item for item in tunare_items if item[2].find('Defiant') >= 0]
    combatants_gear = [item for item in tunare_items if item[2].find("Combatant's") >= 0]
    adepts_gear = [item for item in tunare_items if item[2].find("Adept's") >= 0]

    all_gear = defiant_gear + combatants_gear + adepts_gear
    output_gear_list(all_gear, "\\\\10.19.99.2\\deepend\\EQ Data\\equiplist.txt")

    with open("\\\\10.19.99.2\\deepend\\EQ Data\\item_list.txt", "w") as f:
        item_list = []
        f.write(f"item entries from tunare characters' inventories\n")
        for item in tunare_items:
            if item[2] not in item_list:
                f.write(f"unspecified location\t{item[2]}\t0\t0\t0\n")
                item_list.append(item[2])
    