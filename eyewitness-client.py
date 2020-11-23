#! /usr/bin/python
# eyewitness-client: sends bookmarks to eyewitness-server upon detected changes to places.sqlite

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

# Event handler
if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

# Copy FF db (places.sqlite & places.sqlite-wal) & create path if it doesn't exist
TargetPath = Path(Backup_Folder)
TargetPath.mkdir(parents=True, exist_ok=True)
shutil.copy(Places_File, Places_File_Backup)
shutil.copy(Places_WAL, Places_WAL_Backup)
print(f'{current_date} {current_time}: eyewitness-client: found places.sqlite, database copied!')

# When changes to db detected, copy it again
def on_modified(event):
    # timestamps again so they update on event
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime("%H:%M:%S")

    # Copy FF db (places.sqlite & places.sqlite-wal) & create path if it doesn't exist
    TargetPath = Path(Backup_Folder)
    TargetPath.mkdir(parents=True, exist_ok=True)
    shutil.copy(Places_File, Places_File_Backup)
    shutil.copy(Places_WAL, Places_WAL_Backup)

    print(f'{current_date} {current_time}: eyewitness-client: changes detected, database copied!')

# Event handler condition: only if changes are detected
my_event_handler.on_modified = on_modified

# Create observer to watch FF db
go_recursively = False
my_observer = Observer()
my_observer.schedule(my_event_handler, Places_WAL)

# Start the observer
my_observer.start()
try:
    while True:
        time.sleep(1)
except:
     my_observer.stop()
my_observer.join()
