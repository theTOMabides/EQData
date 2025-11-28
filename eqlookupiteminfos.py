import mariadb
import sys
import json
from eqiteminfo import search_for_item, get_page_for_item, get_item_info_from_page

def update_item_info_in_db(cursor, item_id, item_info):
    cursor.execute(
        "UPDATE Item SET weight = ?, size = ?, flags = ? WHERE allakhazam_id = ?",
        (
            item_info['weight'],
            item_info['size'],
            json.dumps(item_info['flags']),
            item_id
        )
    )
    if item_info['tribute'] is not None:
        cursor.execute(
            "UPDATE Item SET tribute = ? WHERE allakhazam_id = ?",
            (
                item_info['tribute'],
                item_id
            )
        )
    if item_info['restrictions'] is not None:
        cursor.execute(
            "UPDATE Item SET restrictions = ? WHERE allakhazam_id = ?",
            (
                json.dumps(item_info['restrictions']),
                item_id
            )
        )
    if len(item_info['primary_stats']) > 0:
        cursor.execute(
            "UPDATE Item SET primary_stats = ? WHERE allakhazam_id = ?",
            (
                json.dumps(item_info['primary_stats']),
                item_id
            )        
        )
    if len(item_info['stats']) > 0:
        cursor.execute(
            "UPDATE Item SET stats = ? WHERE allakhazam_id = ?",
            (
                json.dumps(item_info['stats']),
                item_id
            )        
        )
    if len(item_info['regens']) > 0:
        cursor.execute(
            "UPDATE Item SET regens = ? WHERE allakhazam_id = ?",
            (
                json.dumps(item_info['regens']),
                item_id
            )        
        )
    if len(item_info['resists']) > 0:
        cursor.execute(
            "UPDATE Item SET resists = ? WHERE allakhazam_id = ?",
            (
                json.dumps(item_info['resists']),
                item_id
            )        
        )
    if len(item_info['container_info']) > 0:
        cursor.execute(
            "UPDATE Item SET container_info = ? WHERE allakhazam_id = ?",
            (
                json.dumps(item_info['container_info']),
                item_id
            )        
        )
    if item_info['food_type'] is not None:
        cursor.execute(
            "UPDATE Item SET food_type = ? WHERE allakhazam_id = ?",
            (
                item_info['food_type'],
                item_id
            )        
        )
    if len(item_info['other_stats']) > 0:
        cursor.execute(
            "UPDATE Item SET other_stats = ? WHERE allakhazam_id = ?",
            (
                json.dumps(item_info['other_stats']),
                item_id
            )        
        )   
    if len(item_info['unparsed_lines']) > 0:
        cursor.execute(
            "UPDATE Item SET unparsed_lines = ? WHERE allakhazam_id = ?",
            (
                json.dumps(item_info['unparsed_lines']),
                item_id
            )        
        )

def lookup_item_infos(cursor, count):
    cursor.execute(
        "SELECT allakhazam_id, name FROM Item WHERE allakhazam_id IS NOT NULL AND weight IS NULL LIMIT ?",
        (count,)
    )
    rows = cursor.fetchall()
    for row in rows:
        print(f"Looking up item: {row[1]}: id={row[0]}")
        html = get_page_for_item(row[0])
        if html is not None:
            item_info = get_item_info_from_page(html, row[0])
            update_item_info_in_db(cursor, row[0], item_info.to_dict())
        #    cursor.execute(
        #        "UPDATE Item SET allakhazam_id = ? WHERE id = ?",
        #        (item_id, row[0])
        #    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("need to specify number of items to look up\n")
        exit()
    try:
        count = int(sys.argv[1])
    except ValueError:
        print("Invalid number specified")
        exit()
    try:
        conn = mariadb.connect(
            user="dad",
            password="xmas22",
            host="10.20.24.212",
            port=3306,
            database="everquest_data")
        cursor = conn.cursor()
        lookup_item_infos(cursor, int(sys.argv[1]))
        conn.commit()
        cursor.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    except:
        conn.commit()
        cursor.close()
        conn.close()
        raise
    