"""This module generates random data such as varieties of strings representing dates, time, gender etc
for the purpose of creating synthetic datasets
(c) Dr Horst Herb 2024, licensed under the GPL 3.0 license whcih can be obtained at http://gnu.org """

import random
import datetime as dt

def get_random_genderstring(gender : chr, is_adult:bool = True) -> str:
    """
    Generates a random gender string based on the input gender and age group.

    Parameters:
        gender (chr): The gender character ('M' for male, 'F' for female, '?' for unknown).
        is_adult (bool): Flag indicating if the person is an adult (default is True).

    Returns:
        str: A random gender string.
    """
    if gender == '?':
        return(random.choice(['intersex', 'unknown', 'transgender']))
    adult_males= ['male', 'male', 'male', 'male', 'male', 'man', 'man', 'man', 'man', 'm', 'M', 'Male', 'xy', 'XY']
    junior_males = ['boy', 'boy', 'boy', 'boy', 'Boy', 'male', 'male', 'male', 'male', 'male', 'Male', 'm', 'M', 'xy', 'XY']    
    adult_females = ['female', 'female', 'female', 'female', 'female', 'female', 'f', 'F',  'woman',  'woman',  'woman',  'woman',  'woman', 'fem', 'xx', 'XX']
    junior_females = ['female', 'female', 'female', 'female', 'female', 'female', 'girl', 'girl', 'girl', 'girl', 'girl', 'woman', 'woman', 'fem', 'xx', 'XX']
    
    if gender == 'M':
        return random.choice(adult_males) if is_adult else random.choice(junior_males)
    else:
        return random.choice(adult_females) if is_adult else random.choice(junior_females)


def is_female(genderstring):
    """
    Returns true if the gendestring indicates female gender
    """
    return genderstring.lower() in ['female', 'f', 'woman', 'fem', 'xx', 'girl']


def get_random_date(from_days_ago=365):
    """
    Generates a random date within the past specified number of days.

    Parameters:
    from_days_ago (int): The number of days ago from today to start the date range (default is 365).

    Returns:
    datetime.date: A random date within the specified range.
    """
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=365)  # one year ago
    return start_date + dt.timedelta(days=random.randint(0, from_days_ago))


def randomize_date_format(date_str):
    """Randomize the date format of the input string.
    
    Args:
        date_str (str): A date string in the format 'YYYY-MM-DD'.
        
    Returns:
        str: A date string in a different format."""
    date = dt.datetime.strptime(date_str, "%Y-%m-%d")
    date_format = random.choice(['%d/%m/%Y', '%d/%m/%y', '%-d/%-m/%Y', '%-d/%-m/%y', '%-d/%m/%Y', '%-d/%m/%y',
                                 '%d.%m.%Y', '%d.%m.%y', '%-d.%-m.%Y', '%-d.%-m.%y', '%-d.%m.%Y', '%-d.%m.%y',
                                 "%d-%m-%Y", "%d-%m-%y", "%-d-%-m-%Y", "%-d-%-m-%y", "%-d-%m-%Y", "%-d-%m-%y",
                                 "%Y/%m/%d", "%y/%m/%d", "%Y/%-m/%-d", "%y/%-m/%-d", "%Y/%-m/%-d", "%y/%-m/%-d",
                                 ])
    return date.strftime(date_format)


def get_randomized_time(working_hours_only=False, working_hours=range(8, 18)):
    """Generate a random time string in a randomtime format.
    
    Args:
        working_hours_only (bool): If True, only generate times between workinghours range.
        working_hours (range): The range of working hours to generate times for."""
    
    if working_hours_only:
        hour = random.choice(working_hours)
    else:
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
    time=dt.time(hour, minute)
    #create a string with random time formats, varying between 24hr and 12 hr with am/pm etc, while minding the working hours, and also varying leading zeros
    #do it similar to the randomized_date_format function, using the hour and minute generated above
    timeformats = [f"%H:%M", f"%I:%M %p", f"%-H:%M", f"%-I:%M %p", f"%-H:%M",]
    time_format = random.choice(timeformats)
    return time.strftime(time_format)


def randomize_time_format(time_str):
    """Randomize the time format of the input string.
    
    Args:
        time_str (str): A time string in the format 'HH:MM'.
        
    Returns:
        str: A time string in a different format."""
    time = dt.datetime.strptime(time_str, "%H:%M")
    time_format = random.choice(['%H:%M', '%I:%M %p', '%-H:%M', '%-I:%M %p', '%-H:%M'])
    return time.strftime(time_format)

