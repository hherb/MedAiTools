"""This library assists in generating a synthetic population for Australia
(c) 2024 Dr Horst Herb <horst.herb@me.com>
licensed under the GPL 3.0 license. You may obtain a copy of the License at gnu.org
Description: This library assists in generating a synthetic population for Australia
"""
import os
import json
import csv
import sqlite3
import random
from tqdm import tqdm
from pprint import pprint
import datetime

DBNAME = 'synthetic_demographics.sqlite3'
DATE_FORMAT = '%Y-%m-%d'

contact_relations=['father', 'mother', 'uncle', 'aunt', 'brother', 'sister', 'grandfather', 'grandmother', 'partner', 'friend', 'cousin', 'guardian']


def is_within_odds(odds : float) -> bool:
    """Returns True if a random choice is within the given odds, else False.    
    Args:
        odds (float): The odds (0.0 - 1.0) to check against.
    Returns:
        bool: True if within odds, else False.
    """
    return random.random() <= odds

def is_female(genderstring : str) -> bool:
    """ Returns true if the genderstring indicates the patient is female"""
    return genderstring.lower() in ['f', 'female', 'w', 'woman', 'girl', 'fem', 'xx']   

def get_random_dob(age : int = 30, min_age=0, max_age=105) -> str:
    """Returns a random date of birth for a given age.
    Args:
        age (int): The age in years to generate a date of birth for.
    Returns:
        str: A random date of birth in the format yyyy-mm-dd.
    """
    days_in_months=[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    now = datetime.datetime.now()
    if age:
        year = now.year - age
    else:
        year = now.year - random.randint(min_age, max_age) #make random age in years
    month = random.randint(1, 12)
    day = random.randint(1, days_in_months[month-1])
    dob= f"{year}-{month:02d}-{day:02d}"
    ndob = datetime.datetime.strptime(dob, DATE_FORMAT)
    if ndob > now: #cannot be born in the future
        dob = now.strftime(DATE_FORMAT)

    return(dob)


def get_random_postcode(state : str = None, db_name=DBNAME) -> str:
    """Returns a random postcode for a given state.
    Args:
        state (str): The state to fetch a postcode for.
    Returns:
        str: A random postcode.
    """
    if not state:
        state = random.choice(['QLD', 'NSW', 'VIC', 'TAS', 'SA', 'WA', 'NT', 'ACT'])
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT postcode FROM addresses WHERE state = ? ORDER BY RANDOM() LIMIT 1', (state,))
    postcode = cursor.fetchone()[0]
    return(postcode)


def get_random_address(state=None, postcode=None, how_many=1, db_name=DBNAME) -> list[dict]:
    """Fetches a random address from the database for a given state or postcode.
    
    Args:
        db_name (str): The name of the SQLite database.
        state (str): The state to filter addresses by.
        postcode (str): The postcode to filter addresses by.
    
    Returns:
        dict: A dictionary containing the address details.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()   
    query = "SELECT * FROM addresses WHERE 1=1"
    params = []  
    if state:   #select only addresses from this state
        query += " AND state = ?"
        params.append(state)
    if postcode: #select only addresses from this postcode
        query += " AND postcode = ?"
        params.append(postcode)
    query += f" ORDER BY RANDOM() LIMIT {how_many}"
    cursor.execute(query, params)
    addresses = cursor.fetchall()
    
    if not addresses: #should not happen!
        return []
    
    all_found = []
    for address in addresses: 
        addr =  {
            'id': address[0],               
            'number': address[1],
            'street': address[2],
            'unit': address[3],
            'suburb': address[4],
            'state': address[5],
            'postcode': address[6],
            'country': address[7] or 'AU'
        }
        all_found.append(addr)

    conn.close()
    return(all_found)



def get_random_names(how_many=10, gender=None, db_name=DBNAME) -> list[dict]:
    """Fetches a number of random names from the database, optionally filtered by gender.
    
    Args:
        db_name (str): The name of the SQLite database.
        how_many (int): The number of random names to fetch.
        gender (str): The gender to filter names by (optional). One of M, F, ?.
    
    Returns:
        list: A list of dictionaries containing the name details.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor() 
    params = {'how_many': how_many}
     #build the query 
    query = "SELECT firstname, surname FROM names"
    if gender is not None:
        assert(gender in "MF?")
        
        query += (" WHERE gender = :gender")
        params['gender'] = gender
    
    query += " ORDER BY RANDOM() LIMIT :how_many"
    cursor.execute(query, params)
    names  = cursor.fetchall()
    
    #build the return list of dictionaries
    all_found  = []
    for name in names:  
        n = {'firstname':name[0],
             'surname' : name[1], 
             'gender': gender or '?'
             } 
        all_found.append(n)
    conn.close()
    return(all_found)


def random_name(gender=None, db_name=DBNAME):
    name, = get_random_names(how_many=1, gender=gender, db_name=db_name)
    return(f"{name['firstname']} {name['surname']}")



def get_random_phone_number(area='mobile', country_code='61'):
    """Generates a random phone number.
    
    Args:
        area (str): The area of the phone number (e.g. 'mobile', 'landline').
        country_code (str): The country code for the phone number.
    
    Returns:
        str: The random phone number.
    """
    areacodes = {'mobile': 4, 'ACT': 2, 'NSW': 2, 'NT': 8, 'QLD': 7, 'SA': 8, 'TAS': 3, 'VIC': 3, 'WA': 8} 

    mobilepatterns = [f'040{random.randint(1000000,9999999 )}', 
                      f'04{random.randint(10000000,99999999 )}', 
                      f"04{random.randint(10, 99)} {random.randint(0, 999):03} {random.randint(0, 999):03}", 
                      f"04{random.randint(10, 99)}-{random.randint(0, 999):03}-{random.randint(0, 999):03}", 
                      f'+61 040{random.randint(1000000,9999999 )}', 
                      f'+614{random.randint(10000000,99999999 )}', 
                      f"+61 4{random.randint(10, 99)} {random.randint(0, 999):03} {random.randint(0, 999):03}", 
                      f"+61 (0)4{random.randint(10, 99)}-{random.randint(0, 999):03}-{random.randint(0, 999):03}",
    ] 

    landlinepatterns = [f"{random.randint(1000, 9999)}{random.randint(0, 9999):04}",
                        f"{random.randint(1000, 9999)} {random.randint(0, 9999):04}",
                        f"{random.randint(1000, 9999)}-{random.randint(0, 9999):04}",
                        f"0{areacodes[area]}{random.randint(1000, 9999)}{random.randint(0, 9999):04}",
                        f"0{areacodes[area]} {random.randint(1000, 9999)} {random.randint(0, 9999):04}",
                        f"0{areacodes[area]}-{random.randint(1000, 9999)}-{random.randint(0, 9999):04}",
                        f"(0{areacodes[area]}){random.randint(1000, 9999)} {random.randint(0, 9999):04}",
                        f"(0{areacodes[area]}) {random.randint(1000, 9999)} {random.randint(0, 9999):04}",
                        f"(0{areacodes[area]})-{random.randint(1000, 9999)}-{random.randint(0, 9999):04}",
                        f"{country_code}{areacodes[area]}{random.randint(1000, 9999):04}{random.randint(1000, 9999):04}",
                        f"{country_code} {areacodes[area]} {random.randint(1000, 9999):04}{random.randint(1000, 9999):04}",
                        f"+{country_code}{areacodes[area]}{random.randint(1000, 9999):04}{random.randint(1000, 9999):04}",
                        f"+{country_code} 0{areacodes[area]} {random.randint(1000, 9999):04}{random.randint(1000, 9999):04}",
                        f"+{country_code} (0{areacodes[area]}) {random.randint(1000, 9999)} {random.randint(0, 9999):04}",
                        f"+({country_code})-{areacodes[area]})-{random.randint(1000, 9999)}-{random.randint(0, 9999):04}",
    ]
    if area.lower() == 'mobile':
        return(random.choice(mobilepatterns))
    else:
        return f"{random.choice(landlinepatterns)}"

def get_random_email(first_name=None, surname=None, middle_name=None, provider=None):
    """Generates a random email address.
    
    Args:
        firstname (str): The first name to use in the email.
        surname (str): The surname to use in the email.
        provider (str): The email provider to use (optional).
    
    Returns:
        str: The random email address.
    """
    if not first_name:
        first_name = random.choice(['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Harry', 'Ivan', 'bunny', 'kitty', 'puppy', 'sunny', 'lucky', 'happy', 'funny', 'silly', 'billy', 'milly', 'dolly', 'holly', 'molly', 'polly', 'sally', 'tally', 'wally', 'daisy', 'lucy', 'ruby', 'sophie', 'lily', 'milly', 'tilly', 'billy', 'jilly', 'kelly', 'nelly', 'penny', 'sunny', 'bunny', 'danny', 'fanny', 'harry', 'jerry', 'kerry', 'larry', 'marty', 'nancy', 'patty', 'sally', 'tally', 'vicky', 'wally', 'zanny'])   
    if not surname:
        surname = random.choice(['buster', 'hopper', 'jumper', 'parker', 'walker', 'runner', 'dancer', 'singer', 'player', 
                                 'gamer', 'coder', 'builder', 'maker', 'shaker', 'baker', 'rocker', 'roller', 'rider', 'driver', 
                                 'sailor', 'flier', 'swimmer', 'diver', 'skater', 'skier', 'hiker', 'biker', 'racer', 'chaser', 
                                 'hunter', 'fisher', 'farmer', 'gardener', 'painter', 'writer', 'singer', 'actor', 'dancer', 'player', 
                                 'gamer', 'coder', 'builder', 'maker', 'shaker', 'baker', 'rocker', 'roller', 'rider', 'driver', 'sailor', 
                                 'flier', 'swimmer', 'diver', 'skater', 'skier', 'hiker', 'biker', 'racer', 'chaser', 'hunter', 'fisher', 
                                 'farmer', 'gardener', 'painter', 'writer', 'singer', 'actor', 'dancer', 'player', 'gamer', 'coder', 'builder', 
                                 'maker', 'shaker', 'baker', 'rocker', 'roller', 'rider', 'driver', 'sailor', 'flier', 'swimmer', 'diver', 
                                 'skater', 'skier', 'hiker', 'biker', 'racer', 'chaser', 'hunter', 'fisher', 'farmer', 'gardener', 'painter', 
                                 'writer', 'singer', 'actor', 'dancer', 'player', 'gamer', 'coder', 'builder', 'maker', 'shaker', 'baker', 
                                 'rocker', 'roller', 'rider', 'driver', 'sailor', 'flier', 'swimmer', 'diver', 'skater', 'skier', 'hiker', 
                                 'biker', 'racer', 'chaser', 'hunter', 'fisher', 'farmer', 'gardener', 'painter', 'writer', 'singer', 'actor', 
                                 'dancer', 'player', 'gamer', 'coder', 'builder', 'maker', 'shaker', 'baker', 'rocker', 'roller'])
    if not middle_name:
        letters= 30*' ' + 'abcdefghijklmnopqrstuvwxyz'  # a 24/(30+24) chance of having a middle name
        middle= list(letters)
        middle_name = random.choice(middle)
        if middle_name == ' ': #no middle name if ' ' has been randomly selected as a middle name
            middle_name = ''
    if not provider:
        provider = random.choice(['gmail.com', 'gmail.com', 'gmail.com', 'bigpond.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com', 'protonmail.com', 'me.com'])

    firstnamepatterns= [f"{first_name.lower()}",
                        f"{first_name.lower()}",
                        f"{first_name.lower()}",
                        f"{first_name.lower()}",
                        f"{first_name.lower()}",
                        f"{first_name[0].lower()}",
                        f"{first_name[0].lower()}",
                        f"{first_name[0].lower()}",
                        f"{first_name[0:2].lower()}",
                        f"{first_name.lower()}{random.randint(10, 99)}",
                        ]
    surnamepatterns=[f"{surname.lower()}",
                    f"{surname.lower()}",
                    f"{surname.lower()}",
                    f"{surname.lower()}",
                    f"{surname.lower()}",
                    f"{surname[0].lower()}",
                    f"{surname[0:2].lower()}",
                    f"{surname.lower()}{random.randint(10, 99)}",
                    f"{surname.lower()}{random.randint(10, 99)}",
                    f"{surname.lower()}{random.randint(10, 99)}",
                    ]

    connecting_patterns=['', '', '', '.', '_', '-']

    first= random.choice(firstnamepatterns)
    last= random.choice(surnamepatterns)
    connecting= random.choice(connecting_patterns)
    if middle_name:
        first=f"{first}{random.choice(connecting_patterns)}{middle_name}"
    filler=''
    if len(first)+len(last) < 6:
        filler= str(random.randint(10, 999))
    return f"{first}{connecting}{last}{filler}@{provider}"


def load_large_json(file_path : str):
    """Reads a large JSON file line by line and returns a generator.
    Args:
        file_path (str): The path to the JSON file.
    Returns:
        generator: A generator that yields a JSON object for each line in the file.
    """
    with open(file_path, 'r') as file:
        for line in file:
            yield json.loads(line)


def read_names_csv(file_path : str, limit : int=10000) -> list:
    """Reads a CSV file containing names and returns a list of dictionaries containing the data.
    The CSV file should have the following columns: firstname, surname, gender, [optional more columns] 
    and should not have a header row.
    Args:
        file_path (str): The path to the CSV file.
        limit (int): The maximum number of entries to read.
    Returns:
        list: A list of dictionaries containing the data from the CSV file.
    """
    entries = []
    seen=set()
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if limit>0  and i >= limit:
                break
            entry_tuple = (row[0], row[1], row[2])
            if entry_tuple not in seen: #exclude duplicates
                seen.add(entry_tuple)
                entries.append({
                    'firstname': row[0],
                    'surname': row[1],
                    'gender': row[2]
                })
    return entries




def import_names(file_path : str, limit : int=10000, db_name : str = DBNAME ):
    """Imports names from a CSV file into a SQLite database.
    Args:
        file_path (str): The path to the CSV file.
        db_name (str): The name of the SQLite database.
        limit (int): The maximum number of entries to import.
    """
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    names = read_names_csv(file_path, limit)
    for name in tqdm(names, desc="Inserting names into DB"):
        cursor.execute('''
            INSERT INTO names (firstname, surname, gender)
            VALUES (:firstname, :surname, :gender)
        ''', name)
    conn.commit()
    conn.close()


def import_addresses(file_path : str, limit : int=None, db_name : str = DBNAME):
    """Imports addresses from a json file into a SQLite database table 'addresses'.
    Args:
        file_path (str): The path to the json file.
        db_name (str): The name of the SQLite database.
        limit (int): The maximum number of entries to import.
    """
    conn = sqlite3.connect(db_name)
    cursor=conn.cursor()
    count=0
    for line in load_large_json(file_path):
        data= line['properties']
        address = {
            'number': data.get('number', ''),
            'street': data.get('street'),
            'unit': data.get('unit', ''),
            'suburb': data.get('city', ''),
            'state': data.get('region', ''),
            'postcode': data.get('postcode'),
            'country': data.get('country', 'AU')
        }
        cursor.execute('''
            INSERT INTO addresses (street_number, street, unit, suburb, state, postcode, country)
            VALUES (:number, :street, :unit, :suburb, :state, :postcode, :country)
        ''', address)
        count += 1
        if limit and count>limit:
            break
    conn.commit()
    conn.close()

def read_address(address_id : int, db_name : str = DBNAME) -> dict:
    """Fetches an address from the address table by ID.
    Args:
        address_id (int): The ID of the address to fetch.
        db_name (str): The name of the SQLite database.
    Returns:
        dict: A dictionary containing the address details.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Set row factory to sqlite3.Row in order to return dictionaries instead of tuples
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM addresses WHERE id = ?', (address_id,))
    address = cursor.fetchone()
    conn.close()
    return(dict(address))

def create_person(person_data : dict, db_name : str = DBNAME) -> int:
    """Inserts a new person into the person table.
    Args:
        person_data (dict): A dictionary containing the person details.
        db_name (str): The name of the SQLite database.
    Returns:
        int: The ID of the newly created person.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Ensure all fields are populated, defaulting to empty strings if not provided
    person_data = {
        'title': person_data.get('title', ''),
        'firstname': person_data.get('firstname', ''),
        'middlename': person_data.get('middlename', ''),
        'surname': person_data.get('surname', ''),
        'maidenname': person_data.get('maidenname', ''),
        'alias': person_data.get('alias', ''),
        'dob': person_data.get('dob', ''),
        'gender': person_data.get('gender', ''),
        'biological_gender': person_data.get('biological_gender', ''),
        'ethnicity': person_data.get('ethnicity', ''),
        'mobile_phone': person_data.get('mobile_phone', ''),
        'landline': person_data.get('landline', ''),
        'email': person_data.get('email', ''),
        'address_id': person_data.get('address_id', None),
        'medicare_number': f"{random.randint(2000, 9999)} {random.randint(10000, 99999)} {random.randint(1, 9)}",
    }
    
    cursor.execute('''
        INSERT INTO person (title, firstname, middlename, surname, maidenname, alias, dob, gender, biological_gender, ethnicity, mobile_phone, landline, email, address_id)
        VALUES (:title, :firstname, :middlename, :surname, :maidenname, :alias, :dob, :gender, :biological_gender, :ethnicity, :mobile_phone, :landline, :email, :address_id)
    ''', person_data)
    new_id = cursor.lastrowid  # Get the ID of the newly created record
    conn.commit()
    conn.close()
    return(new_id)


def find_people(gender:str=None, age:int=None, location:str=None, how_many:int=10, db_name:str=DBNAME) -> list[dict]:
    """Searches for a person in the person table including address details from the table addresses
    Args:
        gender (str): The gender of the person.
        age (int): Age of the person in years.
        location (str): if 3 letters, it is a state, if 4 digits, it is a postcode.
        how_many (int): The number of entries to return.
    Returns:
        list: A list of dictionaries containing the person details.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Set row factory to sqlite3.Row in order to return dictionaries instead of tuples
    cursor = conn.cursor()
    
    # SELECT CAST((julianday('now') - julianday(dob)) / 365.25 AS INTEGER) AS age FROM person WHERE id = 1;
    query = "SELECT p.*,  CAST((julianday('now') - julianday(dob)) / 365.25 AS INTEGER) AS age FROM person p JOIN addresses a ON p.address_id = a.id"
    conditions = []
    params = {}
    
    if gender is not None:
        conditions.append("p.gender = :gender")
        params['gender'] = gender
    
    
    if location is not None:
        if len(location) == 3:  # Assuming state is represented by 3 letters
            conditions.append("a.state = :location")
        elif len(location) == 4:  # Assuming postcode is represented by 4 digits
            conditions.append("a.postcode = :location")
        params['location'] = location
    
    if age is not None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=age*365)).strftime('%Y-%m-%d')
        end_date = (datetime.datetime.now() - datetime.timedelta(days=(age-1)*365)).strftime('%Y-%m-%d')
        conditions.append("p.dob BETWEEN :start_date AND :end_date")
        params['start_date'] = start_date
        params['end_date'] = end_date

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if how_many:
        query += f" ORDER BY RANDOM() LIMIT {how_many}"

    print(f"Query: {query}")
    print(f"Params: {params}")
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def read_person(person_id : int, db_name : str = DBNAME) -> dict:
    """Fetches a person from the person table by ID.
    Args:
        person_id (int): The ID of the person to fetch.
        db_name (str): The name of the SQLite database.
    Returns:
        dict: A dictionary containing the person details.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Set row factory to sqlite3.Row in order to return dictionaries instead of tuples
    cursor = conn.cursor()
    cursor.execute("SELECT *, CAST((julianday('now') - julianday(dob)) / 365.25 AS INTEGER) AS age FROM person WHERE id = ?", (person_id,))
    person = cursor.fetchone()
    conn.close()
    return dict(person)

def update_person(update_data, db_name=DBNAME):
    """Updates a person in the person table by ID.
    Args:
        update_data (dict): A dictionary containing the fields to update.
        db_name (str): The name of the SQLite database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    set_clause = ', '.join([f"{key} = :{key}" for key in update_data.keys() if key.lower() != 'id'])
    cursor.execute(f'''
        UPDATE person
        SET {set_clause}
        WHERE id = :id
    ''', update_data)
    conn.commit()
    conn.close()

def delete_person(person_id, db_name=DBNAME):
    """Deletes a person from the person table by ID.
    Args:
        person_id (int): The ID of the person to delete.
        db_name (str): The name of the SQLite database
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM person WHERE id = ?', (person_id,))
    conn.commit()
    conn.close()


def create_database(db_name=DBNAME, keep_existing=True):   
    """Creates a new SQLite database with the required tables if it doesn't already exist.
    Args:
        db_name (str): The name of the SQLite database.
        keep_existing (bool): Whether to keep the existing database if it already exists.
    """ 
    if os.path.exists(db_name) and keep_existing:
        print(f"Database {db_name} already exists. Keeping existing database.")
        return
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    #download data from https://www.ehelse.no/kodeverk-og-terminologi/ICPC-2/icpc-2e-english-version 
    cursor.execute("""CREATE TABLE IF NOT EXISTS icpc2 (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   code TEXT,
                   title TEXT,
                   description TEXT
                   )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            street_number TEXT,
            street TEXT,
            unit TEXT,
            suburb TEXT,
            state TEXT,
            postcode TEXT,
            country TEXT
            ) """)
    conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            surname TEXT NOT NULL,
            gender TEXT default '?',
            aka TEXT default ''
        )''')
    conn.commit()

     # Create person table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS person (
            id INTEGER PRIMARY KEY,
            title TEXT,
            firstname TEXT,
            middlename TEXT,
            surname TEXT,
            maidenname TEXT,
            alias TEXT,
            dob TEXT,
            gender TEXT CHECK(gender IN ('M', 'F', '?')),
            biological_gender TEXT CHECK(biological_gender IN ('M', 'F', '?')),
            ethnicity TEXT,
            mobile_phone TEXT,
            landline TEXT,
            email TEXT,
            medicare_number TEXT,
            address_id INTEGER,
            FOREIGN KEY (address_id) REFERENCES addresses (id)
        )
    ''')
    conn.commit()
    conn.close()


def empty_person() -> dict:
    """Returns an empty person dictionary with all fields set to empty strings."""
    return({
        'title': '',
        'firstname': '',
        'middlename': '',
        'surname': '',
        'maidenname': '',
        'alias': '',
        'dob': '',
        'gender': '?',
        'biological_gender': '?',
        'ethnicity': '',
        'mobile_phone': '',
        'landline': '',
        'email': ''
    })


def initialize_database(db_name=DBNAME, address_file=None, name_file=None, limit=0):
    create_database(db_name, keep_existing=False)
    if address_file:
        import_addresses(address_file, limit=limit)
    if name_file:
        import_names(name_file, limit=limit)

def create_synthetic_person(age=None, gender=None, state=None, postcode=None, db_name=DBNAME):
    person = empty_person()
    #allocate a birthday
    person['dob'] = get_random_dob(age=age)
    person['age'] = int((datetime.datetime.now() - datetime.datetime.strptime(person['dob'], DATE_FORMAT)).days / 365.25)
    #allocate a gender
    opposite_gender = {'M': 'F','F': 'M', '?': '?'}
    if gender is None:
        gender = random.choice(['M', 'F'])
        if is_within_odds(0.001):
            gender = '?'
    person['gender'] = gender
    if is_within_odds(0.002):
        person['biological_gender'] = opposite_gender[gender]
    else:
        person['biological_gender'] = gender
    
    if gender == 'F':
        if person['age'] > 20 and is_within_odds(0.5):
            person['maidenname'] = get_random_names(db_name=db_name, how_many=1)[0]['surname']
    
    person['title'] = 'Mr' if gender =='male' else 'Mrs' if is_within_odds(0.85) else 'Miss'
    
    #allocate names and addresses
    try:
        names = get_random_names(db_name=db_name, how_many=1, gender=gender)[0]
    except IndexError:
        names = {'firstname': 'Unknown', 'surname': 'Unknown'}
    person['firstname'] = names['firstname']
    person['surname'] = names['surname']
    if is_within_odds(0.7): #odds for having a middle name
        name = get_random_names(db_name=db_name, how_many=1, gender=gender)[0]
        person['middlename'] = name['firstname']
    if is_within_odds(0.5): #odds for having an alias
        genderparam=person['gender']
        if genderparam=='?': 
            genderparam=random.choice(['M', 'F'])
        name = get_random_names(1, gender=genderparam)[0]
        person['alias'] = f"{name['firstname']} {name['surname']}"
    #allocate an address
    if not state and not postcode:
        state = random.choice(['QLD', 'NSW', 'VIC', 'TAS', 'SA', 'WA', 'NT', 'ACT'])
        postcode = get_random_postcode(state)
    address = get_random_address(state=state, postcode=postcode, how_many=1)[0]
    person['address_id'] = address['id']
    if is_within_odds(0.95): #odds for havinga mobile phone
        person['mobile_phone'] = get_random_phone_number('mobile')
    if is_within_odds(0.4): #odds for having a landline 
        person['landline'] = get_random_phone_number(address['state'])
    if is_within_odds(0.9): #odds for having an email
        person['email'] = get_random_email(person['firstname'], person['surname'])
    return(person)

def person_details(id, db_name=DBNAME):
    person = read_person(id, db_name=db_name)
    address = read_address(person['address_id'], db_name=db_name)
    person['address'] = address
    return(dict(person))

def create_population(how_many=10, male2female_ratio=0.5, age_distribution=None, db_name=DBNAME):
    population = []
    for _ in tqdm(range(how_many), desc='Creating population'):
        gender = 'male' if is_within_odds(male2female_ratio) else 'female'
        age = random.choice(age_distribution) if age_distribution else random.randint(0, 105)
        person = create_synthetic_person(gender=gender, age=age, db_name=db_name)
        person_id = create_person(person, db_name=db_name)
        person['id'] = person_id
        population.append(person_id)
    return(population)

def count_population_in_database(postcode=None, state=None, db_name=DBNAME):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    params={}
    query = 'SELECT COUNT(*) FROM person p JOIN addresses a ON p.address_id = a.id'
    if postcode is not None:
        query += ' WHERE a.postcode = :postcode'
        params['postcode'] = postcode
    elif state is not None:
        query += ' WHERE a.state = :state'
        params['state'] = state
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return(count)

def get_population(how_many=10, state=None, postcode=None,  db_name=DBNAME):
    """Fetches a number of random addresses from the database.
    Args:
        db_name (str): The name of the SQLite database.
        how_many (int): The number of random addresses to fetch.
        state (str): The state to filter addresses by. Only used if postcode is not stated.
        postcode (str): The postcode to filter addresses by.
    Returns:
        list: A list of dictionaries containing the person and address details.
    """
    #do we have enough people in the database to fulfill request?
    people_missing = how_many -  count_population_in_database(state=state, postcode=postcode, db_name=DBNAME)
    if people_missing > 0:
        #we don't have enough people, we have to create some extra people first
        print(f"Generating {people_missing} synthetic people to make up the numbers")
        for _ in tqdm(range(0,people_missing), desc='Generating synthetic people'):
            #create a person along with address details
            person=create_synthetic_person(state=state, postcode=postcode, db_name=db_name)
            #store that person in our database
            create_person(person, db_name=db_name)

    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Set row factory to sqlite3.Row in order to return dictionaries instead of tuples
    cursor = conn.cursor()
    #fetch the requested number of people from the database
    query = """
    SELECT p.*, a.*
    FROM person p
    JOIN addresses a ON p.address_id = a.id
    ORDER BY RANDOM()
    LIMIT :n;
    """
    params = {'n': how_many} 
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    people = [dict(row) for row in results]
    assert(len(people) == how_many)
    return(people)


def convert_date_format(date_str):
    """Converts date from dd/mm/yyyy to yyyy-mm-dd format."""
    try:
        return datetime.datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        return date_str  # Return the original string if it doesn't match the expected format
    
def fix_dob():
    """Fixes the date of birth format in the person table."""
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, dob FROM person')
    people = cursor.fetchall()
    for person in tqdm(people, desc='Fixing date of birth format'):
        new_dob = convert_date_format(person[1])
        cursor.execute('UPDATE person SET dob = ? WHERE id = ?', (new_dob, person[0]))
    conn.commit()
    conn.close()

def get_random_diagnosis(domain:str = None, limit=1, db_name:str=DBNAME):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    params={'limit':limit}
    query = 'select code, issue  from icpc2'
    if domain:
        params['domain']=domain
        query +=' WHERE domain = :domain'
    query += ' order by random() limit :limit'
    cursor.execute(query, params)



if __name__ == "__main__":
    au_address_file = "/Users/hherb/AI/datasets/demographics/source.geojson"
    uk_name_file = "/Users/hherb/AI/datasets/demographics/name_dataset/data/GB.csv"
    dbfile = DBNAME
    if not os.path.exists(dbfile):
         initialize_database(db_name=dbfile, address_file=au_address_file, name_file=uk_name_file, limit=0)
    #population = get_population(how_many=100, db_name=dbfile)
    
    
    pprint(get_population(how_many=10, state='QLD', db_name=DBNAME))
    
