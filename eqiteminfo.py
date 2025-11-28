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
    "Attuneable",
    "Augmentation",
    "INFUSIBLE",
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

regens_list = [
    "HP Regen",
    "Mana Regeneration"
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
        self.slots = None
        self.classes = None
        self.races = None
        self.aug_slots = []
        self.other_stats = {}
        self.unparsed_lines = []
        self.stat_mod_re = re.compile(
            r'([A-Za-z ]+):?\s*([+-]\d+)(?:\s*<span[^>]*>([+-]?\d+)</span>)?'
        )
        self.resists_re = re.compile(
            r'SV (FIRE|DISEASE|COLD|MAGIC|POISON|CORRUPTION):\s*([+-]\d+)'
        )
        self.weight_re = re.compile(
            r'WT:\s*([\d.]+)'
        )
        self.size_re = re.compile(
            r'Size:\s*(TINY|SMALL|MEDIUM|LARGE|GIANT)'
        )
        self.other_mods_re = re.compile(
            r'([A-Za-z ]+?):?\s*([+-]\d+)'
        )
        self.other_stats_re = re.compile(
            r'([A-Za-z ]+):?\s*(\d+)'
        )
        self.aug_slot_re = re.compile(
            r'Slot (\d+), (.*)'
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
            if self.slots is None:
                self.slots = []
            for x in slot_line[6:].split(' '):
                self.slots.append(x.strip())
            return True
        return False
    def parse_augmentation_slots(self, aug_slot_line):
        match = self.aug_slot_re.match(aug_slot_line)
        if match:
            slot_number = int(match.group(1))
            slot_description = match.group(2).strip()
            self.aug_slots.append((slot_number, slot_description))
            return True
        return False
    def parse_stats(self, pri_line):
        result = False
        remaining_line = pri_line
        while len(remaining_line) > 0:
            match = self.stat_mod_re.match(remaining_line)
            if not match:
                if result:
                    self.unparsed_lines.append(remaining_line)
                break
            abbr = match.group(1).strip()
            value = match.group(2)
            mod = match.group(3)
            if abbr in stats_list:
                self.stats[abbr] = (int(value), int(mod) if mod else None)
            elif abbr in regens_list:
                self.regens[abbr] = int(value)
            elif abbr in contianer_stats:
                self.container_info[abbr] = int(value)
            elif abbr in primary_stats_list:
                self.primary_stats[abbr] = (int(value), int(mod) if mod else None)
            else:
                self.other_stats[abbr.strip()] = int(value)
            remaining_line = remaining_line[match.end():].strip()
            result = True
        return result
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
    def parse_weightsize(self, ws_line):
        weight_match = self.weight_re.search(ws_line)
        size_match = self.size_re.search(ws_line)
        found_one = False
        if weight_match:
            self.weight = float(weight_match.group(1))
            found_one = True
        if size_match:
            self.size = size_match.group(1)
            found_one = True
        return found_one
    def parse_other(self, other_line):
        result = False
        matches = self.other_mods_re.findall(other_line)
        if matches:
            for abbr, value in matches:
                self.other_stats[abbr.strip()] = int(value)
            result = True
        matches = self.other_stats_re.findall(other_line)
        if matches:
            for abbr, value in matches:
                if abbr in primary_stats_list:
                    self.primary_stats[abbr.strip()] = int(value)
                elif abbr in regens_list:
                    self.regens[abbr] = int(value)
                else:
                    self.other_stats[abbr.strip()] = int(value)
            result = True
        return result
    def parse_all(self, line):
        if len(line.strip()) == 0:
            return True
        parsers = [
            self.parse_classes,
            self.parse_races,
            self.parse_augmentation_types,
            self.parse_slots,
            self.parse_augmentation_slots,
            self.parse_flags,
            self.parse_weightsize,
            self.parse_resists,
            self.parse_stats,
            self.parse_other
        ]
        for parser in parsers:
            if parser(line):
                return True
        self.unparsed_lines.append(line)
        return False
    def pack_restrictions(self):
        restrictions = {}
        if self.classes is not None:
            restrictions['Class'] = ','.join(self.classes)
        if self.races is not None:
            restrictions['Race'] = ','.join(self.races)
        if self.slots is not None:
            restrictions['Slots'] = ','.join(self.slots)
        if "Required level of" in self.other_stats:
            restrictions['Level'] = self.other_stats["Required level of"]
        self.restrictions = restrictions
    def pack_aug_slots(self):
        if len(self.aug_slots) >0 and 'aug_slots' not in self.other_stats:
            self.other_stats['aug_slots'] = []
        for aug_entry in self.aug_slots:
            self.other_stats['aug_slots'].append(aug_entry)
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
            "other_stats": self.other_stats,
            "unparsed_lines": self.unparsed_lines
        }

def stats_from_item_page(description_td):
    info = item_info()
    for line in description_td.html().split("<br/>"):
        info.parse_all(line.strip())
    info.pack_restrictions()
    info.pack_aug_slots()
    return info

def get_page_for_item(item_id):
    url_string = f"https://everquest.allakhazam.com/db/item.html?item={item_id}"
    print(f"Looking for item # {item_id} with URL \"{url_string}\"")
    req = Request(url_string, headers=headers)
    try:
        with urlopen(req) as response:
            html = response.read().decode('utf-8')
            return html
    except HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
    except URLError as e:
        print(f"URL Error: {e.reason}")
    return None

def get_item_info_from_page(html, item_id):
    doc = PyQuery(html)
    description_td = doc(f"#i{item_id} td.shotdata")
    info = stats_from_item_page(description_td)
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
    html = get_page_for_item(item_id)
    info = get_item_info_from_page(html, item_id)
    print(json.dumps(info.to_dict(),indent=2))
    
    # webbrowser.open_new_tab()