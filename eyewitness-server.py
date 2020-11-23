#! /usr/bin/python
# eyewitness-server: a bookmark webapp with automatic archival & backup

import os, time, sqlite3, shutil, toml, json
from sqlite3 import Error
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from datetime import datetime

# Clear the screen for a clean start
os.system('clear')

# Set timestamps
current_date = datetime.now().strftime('%Y-%m-%d')
current_time = datetime.now().strftime("%H:%M:%S")

# Set paths
Path_Config = toml.load('config.toml')
Places_File = Path_Config['Places_File']
Places_WAL = Path_Config['Places_WAL']
Backup_Folder = Path_Config['Backup_Folder'] + f"eyewitness-{current_date}/"
Places_File_Backup = Backup_Folder + "places.sqlite"
Places_WAL_Backup = Backup_Folder + "places.sqlite-wal"
eyewitnessdb = 'eyewitness.db'

# first run
def create_db(db_file):
    conn = None
    try:
        # create eyewitness-server db if one doesn't exist yet
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Bookmarks
                      (id INTEGER PRIMARY KEY, url TEXT, title TEXT,
                       archive1 TEXT, archive2 TEXT, tags TEXT, dateAdded datetime)''')
        conn.commit()
        cursor.close()
        time.sleep(1)
        print(f'{current_date} {current_time}: eyewitness-server: warp field initialized!')

        # Connect to the copied FF db & extract list of bookmarks
        conn = sqlite3.connect(Places_File_Backup)
        cursor = conn.cursor()
        cursor.execute('''SELECT moz_places.id, moz_places.url, moz_bookmarks.title AS title
            FROM moz_places INNER JOIN moz_bookmarks ON moz_bookmarks.fk = moz_places.id''')
        list_of_bookmarks = cursor.fetchall()
        cursor.close()
        conn.close()

        # Connect to eyewitness-server db & insert list of bookmarks
        conn = sqlite3.connect(eyewitnessdb)
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO Bookmarks (id, url, title) VALUES (?,?,?)", list_of_bookmarks)
        conn.commit()
        cursor.close()
        print(f'{current_date} {current_time}: eyewitness-server: warp field initialized!')

    except Error as e:
        print(f'{current_date} {current_time}: eyewitness-server: something went wrong starting up!')
        print(e)
    finally:
        if conn:
            conn.close()

# Create db & event handler
if __name__ == '__main__':
    create_db(r'eyewitness.db')
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

# Operations to perform upon detected changes to file
def on_modified(event):
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime("%H:%M:%S")
    try:
        # reconnect to Firefox db, extract list of bookmarks
        # wait a second first to avoid conflicts reading the db
        time.sleep(1)
        conn = sqlite3.connect(Places_File_Backup)
        cursor = conn.cursor()
        cursor.execute('''SELECT moz_places.id, moz_places.url, moz_bookmarks.title AS title
                        FROM moz_places INNER JOIN moz_bookmarks ON moz_bookmarks.fk = moz_places.id''')
        list_of_bookmarks = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        # reconnect to eyewitness-server db, insert list of bookmarks (skip duplicates)
        conn = sqlite3.connect(eyewitnessdb)
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO Bookmarks (id, url, title) VALUES (?,?,?)", list_of_bookmarks)
        conn.commit()
        cursor.close()
        conn.close()
        print(f'{current_date} {current_time}: eyewitness-server: transport complete!')
    except Error as e:
        print(e)
        print(f'{current_date} {current_time}: eyewitness-server: subspace anomaly detected!')

# # Event handler condition: if changes to file happens
# my_event_handler.on_created = on_created
my_event_handler.on_modified = on_modified
# my_event_handler.on_deleted = on_deleted
# my_event_handler.on_moved = on_moved

# Create observer to watch for file changes
go_recursively = False
my_observer = Observer()
my_observer.schedule(my_event_handler, Places_File_Backup)

# Start the observer
my_observer.start()
try:
    while True:
        time.sleep(1)
except:
     my_observer.stop()
my_observer.join()
