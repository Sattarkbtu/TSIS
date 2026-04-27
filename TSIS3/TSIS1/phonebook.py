import csv
import json
from connect import get_connection


def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return

    for row in rows:
        print("-" * 50)
        print(f"Name: {row[0]}")
        print(f"Email: {row[1]}")
        print(f"Birthday: {row[2]}")
        print(f"Group: {row[3]}")
        print(f"Phone: {row[4]}")
        print(f"Phone type: {row[5]}")


def filter_by_group():
    group = input("Enter group name: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name ILIKE %s
        ORDER BY c.name
    """, (group,))

    rows = cur.fetchall()
    print_contacts(rows)

    cur.close()
    conn.close()


def search_by_email():
    email = input("Search email: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.email ILIKE %s
        ORDER BY c.name
    """, (f"%{email}%",))

    rows = cur.fetchall()
    print_contacts(rows)

    cur.close()
    conn.close()


def sort_contacts():
    print("Sort by:")
    print("1 - name")
    print("2 - birthday")
    print("3 - date added")

    choice = input("Choose: ")

    columns = {
        "1": "c.name",
        "2": "c.birthday",
        "3": "c.date_added"
    }

    order_column = columns.get(choice, "c.name")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY {order_column}
    """)

    rows = cur.fetchall()
    print_contacts(rows)

    cur.close()
    conn.close()


def paginated_navigation():
    limit = 5
    offset = 0

    while True:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))

        rows = cur.fetchall()
        print_contacts(rows)

        cur.close()
        conn.close()

        print("\nnext / prev / quit")
        cmd = input("Command: ").lower()

        if cmd == "next":
            offset += limit
        elif cmd == "prev":
            offset = max(0, offset - limit)
        elif cmd == "quit":
            break
        else:
            print("Wrong command.")


def export_to_json():
    filename = input("JSON filename: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.name
    """)

    contacts = []

    for contact_id, name, email, birthday, group_name in cur.fetchall():
        cur.execute("""
            SELECT phone, type
            FROM phones
            WHERE contact_id = %s
        """, (contact_id,))

        phones = []

        for phone, phone_type in cur.fetchall():
            phones.append({
                "phone": phone,
                "type": phone_type
            })

        contacts.append({
            "name": name,
            "email": email,
            "birthday": str(birthday) if birthday else None,
            "group": group_name,
            "phones": phones
        })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4, ensure_ascii=False)

    print("Export completed.")

    cur.close()
    conn.close()


def import_from_json():
    filename = input("JSON filename: ")

    with open(filename, "r", encoding="utf-8") as file:
        contacts = json.load(file)

    conn = get_connection()
    cur = conn.cursor()

    for contact in contacts:
        name = contact["name"]
        group_name = contact.get("group") or "Other"

        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            action = input(f"{name} already exists. skip/overwrite: ").lower()

            if action == "skip":
                continue

            if action != "overwrite":
                print("Wrong choice. Skipped.")
                continue

            contact_id = existing[0]

            cur.execute("""
                INSERT INTO groups(name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
            """, (group_name,))

            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            group_id = cur.fetchone()[0]

            cur.execute("""
                UPDATE contacts
                SET email = %s,
                    birthday = %s,
                    group_id = %s
                WHERE id = %s
            """, (
                contact.get("email"),
                contact.get("birthday"),
                group_id,
                contact_id
            ))

            cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))

        else:
            cur.execute("""
                INSERT INTO groups(name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
            """, (group_name,))

            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            group_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                name,
                contact.get("email"),
                contact.get("birthday"),
                group_id
            ))

            contact_id = cur.fetchone()[0]

        for phone in contact.get("phones", []):
            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (
                contact_id,
                phone["phone"],
                phone["type"]
            ))

    conn.commit()
    cur.close()
    conn.close()

    print("Import completed.")


def import_from_csv():
    filename = input("CSV filename: ")

    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            name = row["name"]
            group_name = row.get("group") or "Other"

            cur.execute("""
                INSERT INTO groups(name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
            """, (group_name,))

            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            group_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO contacts(name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET
                    email = EXCLUDED.email,
                    birthday = EXCLUDED.birthday,
                    group_id = EXCLUDED.group_id
                RETURNING id
            """, (
                name,
                row.get("email"),
                row.get("birthday"),
                group_id
            ))

            contact_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (
                contact_id,
                row["phone"],
                row["phone_type"]
            ))

    conn.commit()
    cur.close()
    conn.close()

    print("CSV import completed.")


def add_phone_console():
    name = input("Contact name: ")
    phone = input("Phone: ")
    phone_type = input("Type home/work/mobile: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()

    print("Phone added.")


def move_to_group_console():
    name = input("Contact name: ")
    group = input("New group: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL move_to_group(%s, %s)", (name, group))

    conn.commit()
    cur.close()
    conn.close()

    print("Contact moved.")


def extended_search():
    query = input("Search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()

    print_contacts(rows)

    cur.close()
    conn.close()


def menu():
    while True:
        print("\n--- TSIS1 PHONEBOOK ---")
        print("1 - Filter by group")
        print("2 - Search by email")
        print("3 - Sort contacts")
        print("4 - Paginated navigation")
        print("5 - Export to JSON")
        print("6 - Import from JSON")
        print("7 - Import from CSV")
        print("8 - Add phone")
        print("9 - Move contact to group")
        print("10 - Extended search")
        print("0 - Exit")

        choice = input("Choose: ")

        if choice == "1":
            filter_by_group()
        elif choice == "2":
            search_by_email()
        elif choice == "3":
            sort_contacts()
        elif choice == "4":
            paginated_navigation()
        elif choice == "5":
            export_to_json()
        elif choice == "6":
            import_from_json()
        elif choice == "7":
            import_from_csv()
        elif choice == "8":
            add_phone_console()
        elif choice == "9":
            move_to_group_console()
        elif choice == "10":
            extended_search()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Wrong choice.")


if __name__ == "__main__":
    menu()
