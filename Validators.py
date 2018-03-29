from datetime import datetime

"""
Custom validators used for form validation.
"""

def page_valid(page):
    return page.isdigit()


def id_valid(pid):
    return pid.isdigit()

def date_valid(date):

    if not len(date) == 10:
        return False

    exploded = date.split('-')
    if not len(exploded) == 3:
        return False

    for i in exploded:
        if not i.isdigit:
            return False
    current = datetime.now()
    if int(exploded[0]) < current.year or not len(exploded[0]) == 4:
        return False
    elif int(exploded[1]) < current.month or not len(exploded[1]) == 2:
        return False
    else:
        return len(exploded[2]) == 2

