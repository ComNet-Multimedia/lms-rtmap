# lms-rtmap

## What's this?
Simple script generating html map based on OpenStreetMaps with unsolved tickets shown on it.

## Usage
Just run rtmap.py with rights to read lms.ini and write lms html dir.

## Config
As it's very simple script you have just two variables to change:

|Variable|Example|Description|
|--------|-------|-----------|
|queueid_list|[1,2,3]|List of rt queues to show|
|config_file_path|/etc/lms/lms.ini|Path to lms.ini file|