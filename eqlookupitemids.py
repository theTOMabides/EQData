import mariadb
import sys
from eqiteminfo import search_for_item

def lookup_item_ids(cursor, count):
    cursor.execute(
        "SELECT id, name FROM Item WHERE allakhazam_id IS NULL LIMIT ?",
        (count,)
    )
    rows = cursor.fetchall()
    for row in rows:
        print(f"Looking up item: {row[0]}: {row[1]}")
        item_id = search_for_item(row[1])
        if item_id is not None:
            print(f"Found Allakhazam ID {item_id} for item {row[1]}")
            cursor.execute(
                "UPDATE Item SET allakhazam_id = ? WHERE id = ?",
                (item_id, row[0])
            )

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
        lookup_item_ids(cursor, int(sys.argv[1]))
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
        
    