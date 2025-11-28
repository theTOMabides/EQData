import mariadb
import sys

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
        cursor.execute(
            "SELECT id, allakhazam_id FROM Item WHERE name = ?",
            (sys.argv[1],)
        )
        row = cursor.fetchone()
        if row is None:
            print(f"Item not found in DB: {sys.argv[1]}")
        else:
            print(f"Item found in DB: {row[0]}: {row[1]}")
        cursor.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    