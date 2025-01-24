from datetime import datetime, timedelta
import random


def get_random_date_within_last_n_years(n):
    """
    Generate a random date within the last n years.
    
    Args:
        n (int): Number of years
    
    Returns:
        datetime: Random date within the last n years
    """
    current_date = datetime.now()
    start_date = current_date - timedelta(days=n*365)
    
    random_date = start_date + (current_date - start_date) * random.random()
    return random_date


def get_random_date_format(date):
    """
    Generate a random date format string for a given date.
    
    Args:
        date (datetime): Input date
        
    Returns:
        str: Formatted date string in a random format
    """
    
    # Define possible date separators
    separators = ['-', '/', '.', ' ']
    
    # Define possible month formats
    month_formats = {
        'numeric': [
            '%m',           # 01
            '%-m',          # 1
        ],
        'text': [
            '%B',          # January
            '%b',          # Jan
        ]
    }
    
    # Define possible year formats
    year_formats = [
        '%Y',              # 2024
        '%y'               # 24
    ]
    
    # Define possible day formats
    day_formats = [
        '%d',              # 20
        '%d{}',           # 20th (will be formatted with suffix)
    ]
    
    # Define complete format patterns
    patterns = [
        # Numeric patterns
        '{day}{sep}{month}{sep}{year}',          # 20-01-2024
        '{month}{sep}{day}{sep}{year}',          # 01-20-2024
        '{year}{sep}{month}{sep}{day}',          # 2024-01-20
        
        # Text patterns
        '{day} {month} {year}',                  # 20 January 2024
        '{month} {day}, {year}',                 # January 20, 2024
        '{day}th of {month} {year}',             # 20th of January 2024
        
        # Mixed patterns
        '{day}{sep}{month_short} {year}',        # 20-Jan 2024
        '{month_short} {day}, {year}'            # Jan 20, 2024
    ]
    
    def get_day_suffix(day):
        """Return appropriate suffix for day."""
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return suffix
    
    # Choose random pattern
    pattern = random.choice(patterns)
    
    # Generate format components
    day = date.day
    day_suffix = get_day_suffix(day)
    sep = random.choice(separators)
    
    # Choose year format based on pattern
    if pattern.startswith('{year}'):
        year = date.strftime('%Y')  # Always use 4-digit year when year comes first
    else:
        year = date.strftime(random.choice(year_formats))
    
    # Format string based on pattern type
    if 'month_short' in pattern:
        month = date.strftime('%b')
        result = pattern.format(
            day=day,
            month_short=month,
            year=year,
            sep=sep
        )
    elif pattern.count('month') == 1 and 'th of' in pattern:
        month = date.strftime('%B')
        result = pattern.format(
            day=day,
            month=month,
            year=year
        )
    elif '{month}' in pattern and random.choice([True, False]):
        # Randomly choose between text and numeric month
        month_format = random.choice(month_formats['text'] if ' ' in pattern else month_formats['numeric'])
        month = date.strftime(month_format)
        result = pattern.format(
            day=day,
            month=month,
            year=year,
            sep=sep
        )
    else:
        month = date.strftime(random.choice(month_formats['numeric']))
        result = pattern.format(
            day=day,
            month=month,
            year=year,
            sep=sep
        )
    
    return result

# Example usage
if __name__ == "__main__":
    sample_date = datetime(2024, 1, 20)
    for i in range(10):
        print(get_random_date_format(get_random_date_within_last_n_years(10)))
    