import sqlite3
import json
from models import Entry, Mood, Tag

def get_all_entries():
    # Open a connection to the database
    with sqlite3.connect("./dailyjournal.db") as conn:

        # Just use these. It's a Black Box.
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT 
            a.id,
            a.concept,
            a.entry,
            a.date,
            a.moodId,
            b.id moodCode,
            b.label,
            c.entry_id,
            c.tag_id,
            d.Id tagId,
            d.name tagName
        FROM Entries a
        LEFT JOIN MOODS b
        ON a.moodId == moodCode
        LEFT JOIN entry_tag c
        ON a.id == c.entry_id
        LEFT JOIN Tags d
        ON c.tag_id == d.id
        """)

        # Initialize an empty list to hold all animal representations
        entries = {}

        # Convert rows of data into a Python list
        dataset = db_cursor.fetchall()

        # Iterate list of data returned from database
        for row in dataset:
            if row['id'] in entries:
                tag = Tag(row['tagId'], row['tagName'])
                entries[row['id']].tags.append(tag.__dict__)
                
            else: 
                entry = Entry(row['id'], row['concept'], row['entry'],
                                row['date'], row['moodId'])
                entries[row['id']] = entry

                tag = Tag(row['tagId'], row['tagName'])
                entries[row['id']].tags = []
                entries[row['id']].tags.append(tag.__dict__)

                mood = Mood(row['moodCode'], row['label'])
                entries[row['id']].mood = mood.__dict__

                """
                {
                    1: {
                        "id": 1,
                        "concept": "vjefivofe",
                        "date"; : "vitnvio",
                        tags: [
                            "tired"
                        ],
                        "moodId": 4
                    },
                    3: [Object Entry]
                }
                """
                    
#Figure out how to only get relevant tags onto the object and only make one object

    # Use `json` package to properly serialize list as JSON
    dict_entries = []
    for entry in entries.values():
        dict_entries.append(entry.__dict__)

    return json.dumps(dict_entries)


def get_single_entry(id):
    with sqlite3.connect("./dailyjournal.db") as conn:

        # Just use these. It's a Black Box.
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT
            a.id,
            a.concept,
            a.entry,
            a.date,
            a.moodId,
            b.id moodCode,
            b.label
        FROM Entries a
        JOIN MOODS b
        ON a.moodId == moodCode
        WHERE a.id = ?
        """, ( id, ))

        data = db_cursor.fetchone()

        entry = Entry(data['id'], data['concept'], data['entry'], data['date'], data['moodId'])
        mood = Mood (data['moodCode'], data['label'])

        entry.mood = mood.__dict__

        return json.dumps(entry.__dict__)

def delete_entry(id):
    with sqlite3.connect("./dailyjournal.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        DELETE FROM Entries
        WHERE id = ?
        """, (id, ))

def search_entry(word):
    with sqlite3.connect("./dailyjournal.db") as conn:

        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
        SELECT
            a.id,
            a.concept,
            a.entry,
            a.date,
            a.moodId
        FROM Entries a
        WHERE a.entry LIKE ?
        """, ("%"+ word + "%", ))

        entries = []

        dataset = db_cursor.fetchall()

        for row in dataset:

            entry = Entry(row['id'], row['concept'], row['entry'],
                            row['date'], row['moodId'])
            entries.append(entry.__dict__)

    return json.dumps(entries)

def create_entry(new_entry):
    with sqlite3.connect("./dailyjournal.db") as conn:
        db_cursor = conn.cursor()
        conn.row_factory = sqlite3.Row


        db_cursor.execute("""
        INSERT INTO Entries
            ( concept, entry, date, moodId )
        VALUES
            ( ?, ?, ?, ?);
        """, (new_entry['concept'], new_entry['entry'],
              new_entry['date'], new_entry['moodId'], ))

        # The `lastrowid` property on the cursor will return
        # the primary key of the last thing that got added to
        # the database.
        id = db_cursor.lastrowid

        # Add the `id` property to the animal dictionary that
        # was sent by the client so that the client sees the
        # primary key in the response.
        new_entry['id'] = id

        tag_ids = new_entry["tag_ids"]

        for tag in tag_ids:

            db_cursor.execute("""
            INSERT INTO entry_tag
                ( entry_id, tag_id )
            VALUES
                ( ?, ? );        
            """, ( id, tag, ))


    return json.dumps(new_entry)

def update_entry(id, new_entry):
    with sqlite3.connect("./dailyjournal.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        UPDATE Entries
            SET
                concept = ?,
                entry = ?,
                date = ?,
                moodId = ?
                WHERE id = ?
        """, (new_entry['concept'], new_entry['entry'],
              new_entry['date'], new_entry['moodId'], id, ))

        # Were any rows affected?
        # Did the client send an `id` that exists?
        rows_affected = db_cursor.rowcount

    if rows_affected == 0:
        # Forces 404 response by main module
        return False
    else:
        # Forces 204 response by main module
        return True