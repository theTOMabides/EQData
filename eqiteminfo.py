import sys
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

def stats_from_item_page(description_td):
    item_info = {}
    for line in description_td.html().split("<br/>"):
        print(line)

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
            stats_from_item_page(description_td)
    except HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
    except URLError as e:
        print(f"URL Error: {e.reason}")
    
    # webbrowser.open_new_tab()