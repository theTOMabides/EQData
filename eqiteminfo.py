import re
import sys
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from pyquery import PyQuery
from re import match

headers = {
    "User-Agent": "MyCustomBrowser/1.0",
    "Accept-Language": "en-US,en;q=0.5"
}

def search_for_item(item_name):
    result = None
    item_str = item_name.replace(' ','+')
    print(f"item_str = \"{item_str}\"")
    url_string = "https://everquest.allakhazam.com/search.html?q="+item_str
    req = Request(url_string, headers=headers)
    try:
        with urlopen(req) as response:
            html = response.read().decode('utf-8')
            # print(f"Response from {url_string}:\n{html[:200]}...") # Print first 200 characters
            doc = PyQuery(html)
            items_rows = doc("#Items_t tr")
            for item in items_rows[1:]:
                href = item.find('td').find('a').attrib['href']
                found_item_id = int(href.split('=')[-1])
                found_item_name = item.text_content()
                print(f"{found_item_id}: {found_item_name}")
                if result is None or item_name == found_item_name:
                    result = found_item_id
    except HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
    except URLError as e:
        print(f"URL Error: {e.reason}")
    return result

item_flags = [
    "No Trade",
    "Temporary",
    "Lore Item",
    "Heirloom",
    "Attunable",
    "Augmentation",
    "Infusible",
    "Quest Item",
    "Prestige",
    "Cash Loot",
    "No Storage",
    "Placeable"
]

stats_list = [
    "STR",
    "STA",
    "INT",
    "WIS",
    "AGI",
    "DEX",
    "CHA"
]

primary_stats_list = [
    "AC",
    "HP",
    "Mana",
    "Endur",
    "Purity"
]

resists_list = [
    "FIRE",
    "DISEASE",
    "COLD",
    "MAGIC",
    "POISON",
    "CORRUPTION"
]

contianer_stats = [
    "Weight Red",
    "Capacity",
    "Size Capacity"
]

slots = [
	"EAR",
	"HEAD",
	"FACE",
	"NECK",
	"SHOULDERS",
	"ARMS",
	"BACK",
	"WRIST",
	"RANGE",
	"HANDS",
	"PRIMARY",
	"SECONDARY",
	"FINGER",
	"CHEST",
	"LEGS",
	"FEET",
	"WAIST",
	"CHARM",
	"POWER SOURCE",
	"AMMO"
]

def line_type(desc):
    pass

class item_info:
    def __init__(self):
        self.weight = None
        self.size = None
        self.tribute = None
        self.restrictions = None
        self.flags = []
        self.food_type = None
        self.primary_stats = {}
        self.stats = {}
        self.regens = {}
        self.resists = {}
        self.container_info = {}
        self.slots = []
        self.aug_slots = []
        self.purity = None
        self.stat_re = re.compile(
            r'([A-Z]{3,}):?\s*([+-]\d+)(?:\s*<span[^>]*>([+-]?\d+)</span>)?'
        )
        self.resists_re = re.compile(
            r'SV (FIRE|DISEASE|COLD|MAGIC|POISON|CORRUPTION):\s*([+-]\d+)'
        )
    def parse_flags(self, flag_line):
        found_one = False
        for flag in item_flags:
            if flag in flag_line:
                self.flags.append(flag)
                found_one = True
        return found_one
    def parse_augmentation_types(self, aug_line):
        if aug_line.startswith("Augmentation type: "):
            for x in aug_line[19:].split(' '):
                self.aug_slots.append(x.strip())
            return True
        return False
    def parse_slots(self, slot_line):
        if slot_line.startswith("Slot: "):
            for x in slot_line[6:].split(' '):
                self.slots.append(x.strip())
            return True
        return False
    def parse_primary_stats(self, pri_line):
        if pri_line.startswith(tuple(primary_stats_list)):
            matches = self.stat_re.findall(pri_line)
            self.primary_stats = {
                abbr: (int(value), int(mod) if mod else None)
                for abbr, value, mod in matches }
            return True
        return False
    def parse_purity(self, purity_line):
        if purity_line.startswith("Purity: "):
            self.purity = int(purity_line[8:].strip())
            return True
        return False
    def parse_resists(self, resists_line):
        matches = self.resists_re.findall(resists_line)
        if matches:
            self.resists = {
                abbr: int(value)
                for abbr, value in matches }
            return True
        return False
    def parse_classes(self, class_line):
        if class_line.startswith("Class: "):
            self.classes = class_line[7:].strip().split(' ')
            return True
        return False
    def parse_races(self, race_line):
        if race_line.startswith("Race: "):
            self.races = race_line[6:].strip().split(' ')
            return True
        return False
    def parse_all(self, line):
        parsers = [
            self.parse_flags,
            self.parse_augmentation_types,
            self.parse_slots,
            self.parse_primary_stats,
            self.parse_purity,
            self.parse_resists,
            self.parse_classes,
            self.parse_races
        ]
        for parser in parsers:
            if parser(line):
                return True
        print(f"Unparsed line: {line}")
        return False
    def to_dict(self):
        return {
            "weight": self.weight,
            "size": self.size,
            "tribute": self.tribute,
            "restrictions": self.restrictions,
            "flags": self.flags,
            "food_type": self.food_type,
            "primary_stats": self.primary_stats,
            "stats": self.stats,
            "regens": self.regens,
            "resists": self.resists,
            "container_info": self.container_info,
            "slots": self.slots,
            "aug_slots": self.aug_slots,
            "purity": self.purity
        }

def stats_from_item_page(description_td):
    info = item_info()
    for line in description_td.html().split("<br/>"):
        info.parse_all(line.strip())
    return info

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("need to specify item name\n")
        exit()
    elif len(sys.argv) > 2:
        item_arg = ' '.join(sys.argv[1:])
    else:
        item_arg = sys.argv[1]
    try:
        item_id = int(item_arg)
    except ValueError:
        item_id = search_for_item(item_arg)
    url_string = f"https://everquest.allakhazam.com/db/item.html?item={item_id}"
    req = Request(url_string, headers=headers)
    print(f"Looking for item # {item_id} with URL \"{url_string}\"")
    try:
        with urlopen(req) as response:
            html = response.read().decode('utf-8')
            # print(f"Response from {url_string}:\n{html[:200]}...") # Print first 200 characters
            doc = PyQuery(html)
            description_td = doc(f"#i{item_id} td.shotdata")
            info = stats_from_item_page(description_td)
            print(json.dumps(info.to_dict(),indent=2))
    except HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
    except URLError as e:
        print(f"URL Error: {e.reason}")
    
    # webbrowser.open_new_tab()