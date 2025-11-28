import mariadb
import sys

def show_item_stats(cursor, item_db_id, curslot=None):
    cursor.execute(
        "SELECT name, restrictions, primary_stats, stats, regens, resists "
        "FROM Item WHERE id = ?",
        (item_db_id,)
    )
    row = cursor.fetchone()
    if row is None:
        print(f"Item ID {item_db_id} not found in database.")
        return
    print(f"Item Name: {row[0]}")
    if curslot is not None:
        print(f"Cursor Slot: {curslot}")
    print(f"Restrictions: {row[1]}")
    print(f"Primary Stats: {row[2]}")
    print(f"Stats: {row[3]}")
    print(f"Regens: {row[4]}")
    print(f"Resists: {row[5]}")

def lookup_item_ids(cursor, name):
    cursor.execute(
        "SELECT id, allakhazam_id FROM Item WHERE name = ?",
        (name,)
    )
    row = cursor.fetchone()
    if row is not None:
        return row[0], row[1]
    return None, None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("need to specify item to lookup\n")
        exit()
    try:
        conn = mariadb.connect(
            user="dad",
            password="xmas22",
            host="10.20.24.212",
            port=3306,
            database="everquest_data")
        cursor = conn.cursor()
        namesandslots = []
        try:
            with open(sys.argv[1], 'r') as f:
                for line in f:
                    nameslot = line.strip().split(',', 1)
                    if len(nameslot) != 2:
                        name = nameslot[0]
                        curslot = None
                    else:
                        name, curslot = nameslot
                    namesandslots.append((name, curslot))
        except FileNotFoundError:
            namesandslots.append((sys.argv[1], None))
        print(namesandslots)
        for name, curslot in namesandslots:
            id,_ = lookup_item_ids(cursor, name)
            if id is not None:
                show_item_stats(cursor, id, curslot)
            else:
                print(f"Item '{name}' not found in database.")
        cursor.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    