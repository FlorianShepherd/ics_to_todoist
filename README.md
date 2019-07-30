# ics_to_todoist
ICS to Todoist converter with a linux shell script

# INSTALLATION
1. pip install pytodoist
2. pip install icalendar
3. Enter your user credentials (mail and password) in the shell script. This is needed to connect to todoist
4. copy sh file und py file to "/usr/bin" or "/usr/local/bin"
5. Set execute rights "chmod +x /usr/bin/ics_to_todoist"

# USAGE
open ics file simply with "ics_to_todoist icsfilename" on the bash

or: copy ics_to_todoist.desktop to /usr/share/applications and set ics_to_todist as the default App for ics files

There are also command line options. For example:
./ics_to_todoist -i ics_file -p project_name -y priority
