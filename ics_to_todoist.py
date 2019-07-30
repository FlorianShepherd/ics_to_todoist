import getopt
import sys

from icalendar import Calendar
from pytodoist import todoist

todoist_mail_adress = "you@mail.com"
todoist_password = 'secret_p@ssw0rd'


def _get_minutes(component):
    dtend = component.get("dtend").dt
    dtstart = component.get("dtstart").dt
    fmt = '%Y-%m-%d %H:%M:%S'
    # this can be done more efficient i guess. But I don't care
    seconds = (dtend.strptime(dtend.strftime(fmt), fmt) - dtstart.strptime(dtstart.strftime(fmt), fmt)).seconds
    minutes = int(seconds / 60)
    return minutes

def _get_days(component):
    dtend = component.get("dtend").dt
    dtstart = component.get("dtstart").dt
    days = (dtend - dtstart).days
    return days

def _get_date_str_from_component(component, value):
    value_date = component.get(value).dt
    if not hasattr(value_date, 'time'):
        # only date without time
        utc_date = value_date.strftime("%a %d %b %Y")
        is_date = True
    else:
        # with time
        utc_date = value_date.astimezone().strftime("%a %d %b %Y %H:%M:%S %z")
        is_date = False
    return utc_date, is_date


def ics_to_dict(ics_file):
    g = open(ics_file, 'rb')
    gcal = Calendar.from_ical(g.read())
    ics_dict = dict()
    for component in gcal.walk():
        # print(component.name)
        if component.name == "VEVENT":
            # Start date
            ics_dict["dtstart"], is_date = _get_date_str_from_component(component, 'dtstart')
            # end date
            ics_dict["end"], _ = _get_date_str_from_component(component, 'dtend')
            # when it arrived
            ics_dict["received"], _ = _get_date_str_from_component(component, 'dtstamp')
            # attendee
            ics_dict["attendee"] = component.get("ATTENDEE")
            # description
            ics_dict["description"] = component.get("DESCRIPTION")
            # location
            ics_dict["location"] = component.get("LOCATION")
            # organizer
            ics_dict["organizer"] = component.get("ORGANIZER")
            # summary
            ics_dict["summary"] = component.get("SUMMARY")
            # alt_desc
            ics_dict["alt_desc"] = component.get("X-ALT-DESC")
            # dauer
            if is_date:
                ics_dict["days"] = _get_days(component)
            else:
                ics_dict["minutes"] = _get_minutes(component)
    g.close()
    return ics_dict


def _get_priority(priority):
    if priority.lower() == "normal":
        return todoist.Priority.NORMAL
    elif priority.lower() == "high":
        return todoist.Priority.HIGH
    elif priority.lower() == "low":
        return todoist.Priority.LOW
    elif priority.lower() == "very_high":
        return todoist.Priority.VERY_HIGH
    elif priority.lower() == "no":
        return todoist.Priority.NO
    else:
        print("priority {} unknown. Assign no priority".format(priority))
        return todoist.Priority.NO


def _get_project(project, user):
    projects = user.get_projects()
    for td_prj in projects:
        if project == td_prj.name:
            return td_prj
    else:
        print("Project {} unknown".format(project))
        print("Please choose on of the available projects:")
        for prj in projects:
            print(prj.name)
        raise ValueError("Project {} unknown".format(project))


def add_todoist_task(task_name, project="Inbox", priority="no", dtstart=None, note=None):
    """
    :param task_name: (str) Name of task in todoist
    :param project: (str, "Inbox") project to add to. Default is Inbox
    :param priority: (str, "normal"): priority of task. Can be: "normal", "no", "high", "low", "very_high"
    :param dtstart: (str, None) Start Date as date string
    :param note (str, None) additional notes

    """
    user = todoist.login(todoist_mail_adress, todoist_password)
    todoist_project = _get_project(project, user)
    task = todoist_project.add_task(task_name, priority=_get_priority(priority))
    print("Added task '{}' with priority '{}' to project '{}'".format(task_name, priority, project))
    if dtstart is not None:
        task.date_string = dtstart
        task.date_lang = 'en'
        task.update()
        print("Added start date: '{}'".format(dtstart))
    if note is not None:
        task.add_note(note)
        print("Added additional information as note")


def ics_to_todoist(ics_data, project="Inbox", priority="no"):
    task_name = ""
    note = ""
    dtstart = None
    for key, val in ics_data.items():
        if key == "dtstart":
            dtstart = val
        elif key == "summary":
            task_name = val
        elif key == "minutes":
            task_name += " - " + str(val) + "min"
        elif key == "days":
            task_name += " - " + str(val) + "days"
        else:
            # add all other information as a comment
            note += "\n"
            note += key + "\n"
            note += str(val) + "\n"
    if task_name != "":
        add_todoist_task(task_name, project=project, dtstart=dtstart, note=note, priority=priority)
    else:
        raise ValueError("Task name is empty")


def _get_ics_file(argv):
    # read ics file from command line
    inputfile = None
    project = "Inbox"
    priority = "no"
    try:
        opts, args = getopt.getopt(argv, ":i:p:y:h", ["ifile=", "project=", "priority=", "help="])
    except getopt.GetoptError:
        raise getopt.GetoptError()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Enter input like this, Bro:")
            print('ics_to_todoist.py -i <inputfile> -p project -y priority')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-p", "--project"):
            print(arg)
            project = arg
        elif opt in ("-y", "--priority"):
            print(arg)
            priority = arg
    print('Reading {} to project {} with priority {}: '.format(inputfile, project, priority))
    return inputfile, project, priority


if __name__ == "__main__":
    ics_file, project, priority = _get_ics_file(sys.argv[1:])
    if ics_file is not None:
        ics_data = ics_to_dict(ics_file)
        ics_to_todoist(ics_data, project=project, priority=priority)
    else:
        raise ValueError("ics file is None {}".format(ics_file))
