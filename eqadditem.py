import mariadb
import sys

def items_of_file(fn):
    with open(fn,"r") as invfile:
        _ = invfile.readline()
        for line in invfile:
            try:
                loc, desc, _, _, _ = line.strip().split('\t')
                if desc != 'Empty':
                    yield loc, desc
            except ValueError:
                pass

def add_items_to_db(cursor, inventory):
    for _, desc in inventory:
        cursor.execute(
            "SELECT id, name FROM  Item WHERE name IS ?",
            (desc,)
        )
        row = cursor.fetchone()
        if row is None:
            print(f"Inserting item: {desc}")
            cursor.execute(
                "INSERT INTO Item (name) VALUES (?)",
                (desc,)
            )
        else:
            print(f"Item already in DB: {row[0]}: {row[1]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("need to specify inventory file\n")
        exit()
    try:
        conn = mariadb.connect(
            user="dad",
            password="xmas22",
            host="10.20.24.212",
            port=3306,
            database="everquest_data")
        cursor = conn.cursor()
        add_items_to_db(cursor, items_of_file(sys.argv[1]))
        conn.commit()
        cursor.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    