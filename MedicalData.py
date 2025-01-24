"""This module provides real data for the purpose of creating synthetic health records,
e.g. diagnosis names and codes, medical specialities, drug names etc
"""

import os
import random
import csv
from textwrap import dedent
import sqlite3
import ollama # type: ignore

DBNAME="medical.sql3"

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

    #medical specialities and sub-specialities
    cursor.execute("""CREATE TABLE IF NOT EXISTS medical_specialities (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   speciality TEXT,
                   subspeciality TEXT
                   )""")
    #data source: https://www.medicalboard.gov.au/Registration/Types/Specialist-Registration.aspx
    all_specialities=[]
    with open('./seed_data/medical_specialities.txt')  as f:
        """read code, issue from the csv file and insert it into the database"""
        for line in f:
            specs=line.strip().split(',')
            spec=specs[0]
            all_specialities.append(spec)
            cursor.execute("INSERT INTO medical_specialities (speciality) values (?)", (spec,))
            if len(specs)>1:
                for subspec in specs[1:]:
                     all_specialities.append(subspec)
                     cursor.execute("INSERT INTO medical_specialities (speciality, subspeciality) values (?, ?)", (spec, subspec))
            conn.commit()
    specialists=";".join(all_specialities)

    #ICPC2 diagnosis / medical problem codes
    cursor.execute("""CREATE TABLE IF NOT EXISTS icpc2 (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   code TEXT,
                   issue TEXT,
                   domain TEXT
                   )""")
    #data source: https://www.ehelse.no/kodeverk-og-terminologi/ICPC-2/icpc-2e-english-version 
    with open('./seed_data/icpc-2e-v7.0-shorttitle.csv')  as f:
        """read code, issue from the csv file and insert it into the database"""
        for line in f:
            code, issue = line.strip().split(';')
            prompt=f"""From the following list of medical specialities with their respective subspecialities, 
            I want you to assign the most appropriate speciality and/or subspeciality to the medical problem >{issue}<
            List of specialities: Addiction Medicine
            Anaesthesia
            Dermatology
            Emergency Medicine, Paediatric Emergency Medicine
            General Practice
            Intensive Care Medicine, Paediatric Intensive Care Medicine
            Medical Administration
            Obstetrics and Gynaecology, Gynaecological Oncology, Maternal-Fetal Medicine, Obstetrics and Gynaecological Ultrasound, Reproductive Endocrinology and Infertility, Urogynaecology
            Occupational and Environmental Medicine
            Ophthalmology
            Paediatrics and Child Health, Clinical Genetics, Community Child Health, General Paediatrics, Neonatal and Perinatal Medicine, Paediatric Cardiology, Paediatric Clinical Pharmacology, Paediatric Endocrinology, Paediatric Gastroenterology and Hepatology, Paediatric Haematology, Paediatric Immunology and Allergy, Paediatric Infectious Diseases, Paediatric Intensive Care Medicine, Paediatric Medical Oncology, Paediatric Nephrology, Paediatric Neurology, Paediatric Nuclear Medicine, Paediatric Palliative Medicine, Paediatric Rehabilitation Medicine, Paediatric Respiratory and Sleep Medicine, Paediatric Rheumatology
            Pain Medicine
            Palliative Medicine
            Pathology, General Pathology, Anatomical Pathology (including Cytopathology), Chemical Pathology, Haematology, Immunology, Microbiology, Forensic Pathology
            Physician, Cardiology, Clinical Genetics, Clinical Pharmacology, Endocrinology, Gastroenterology and Hepatology, General Medicine, Geriatric Medicine, Haematology, Immunology and Allergy, Infectious Diseases, Medical Oncology, Nephrology, Neurology, Nuclear Medicine, Respiratory and Sleep Medicine, Rheumatology
            Psychiatry
            Public Health Medicine
            Radiation Oncology
            Radiology, Diagnostic Radiology, Diagnostic Ultrasound, Nuclear Medicine
            Rehabilitation Medicine
            Sexual Health Medicine
            Sport and Exercise Medicine
            Surgery, Cardio-thoracic Surgery, General Surgery, Neurosurgery, Orthopaedic Surgery, Otolaryngology – Head and Neck Surgery, Oral and Maxillofacial Surgery, Paediatric Surgery, Plastic Surgery, Urology, Vascular Surgery

            RESPOND WITH ONLY THE SINGLE MOST APROPRIATE (SUB)SPECIALTY AND NOTHING ELSE"""
            domain = ollama.generate(model='qwen2.5:14b-instruct-q8_0', prompt=prompt, stream=False)['response']
            print(domain)
            cursor.execute("INSERT INTO icpc2 (code, issue, domain) VALUES (?, ?, ?)", (code, issue, domain))
    conn.commit()

def create_medical_facility_table(db_name=DBNAME):
    #data source https://www.health.gov.au/resources/publications/list-of-declared-hospitals?language=en
    conn=sqlite3.connect(db_name)
    cursor=conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS medical_facilities (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   facility INTEGER,
                   name text,
                   street_address TEXT,
                   suburb text,
                   state text,
                   postcode text,
                   provider_number text
                   phone text,
                   fax text,
                   website text,
                   email text,
                   domain TEXT,
                   FOREIGN KEY (facility) REFERENCES facility_types(id)
                   )""")
    conn.commit()
    with open('./seed_data/list_of_declared_hospitals.tsv')  as f:
        """read code, issue from the tsv file and insert it into the database"""
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            cursor.execute("INSERT INTO medical_facilities (facility, name, street_address, suburb, state, postcode, provider_number) values (?,?,?,?,?,?,?)", [1, row[2], row[4], row[5], row[1], row[6], row[3]])
            conn.commit()
    
    
def create_facility_types_table(db_name=DBNAME):
    """
    Creates a table of medical facility types

    Args:
        db_name (str): The name of the SQLite database.
    """
    conn=sqlite3.connect(db_name)
    cursor=conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS facility_types (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   type TEXT
                   )""")
    conn.commit()
    #data source: https://www.health.gov.au/resources/publications/list-of-declared-hospitals?language=en
    with open('./seed_data/facility_types.txt')  as f:
        """read code, issue from the csv file and insert it into the database"""
        for line in f:
            facility_type = line.strip()
            cursor.execute("INSERT INTO facility_types (type) values (?)", (facility_type,))
            conn.commit()
    conn.close()


def random_facility(type=1, postcode=None, state=None, db_name=DBNAME) -> dict:
    """
    Generates a random medical facility from the medical_facilities table.

    Args:
        type (int): The type of the medical facility, see table medical_facility_types(id).
        postcode (str): The postcode of the medical facility.
        state (str): The state of the medical facility.
        db_name (str): The name of the SQLite database.

    Returns:
        dict: A dictionary containing the name, street address, suburb, state, postcode, provider number, phone, fax, website, email, and domain of the random medical facility.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Set row_factory to sqlite3.Row
    cursor = conn.cursor()
    params = {}
    query = "SELECT * FROM medical_facilities"
    andclause=False
    if type:
        params['type'] = type
        query += " WHERE facility = :type"
        andclause = True
    if postcode:
        joinclause = " AND" if andclause else " WHERE" 
        query += joinclause
        query += " postcode = :postcode"
        params['postcode'] = postcode
        andclause = True
    if state:
        joinclause = " AND" if andclause else " WHERE" 
        query += joinclause
        query += " state = :state"
        params['state'] = state
    query += " ORDER BY RANDOM() LIMIT 1;"
    cursor.execute(query, params)
    result = cursor.fetchone()
    if result:
        return dict(result)
    else:
        return {}


def random_diagnosis(domain : str = None, include_female_only=False, include_paediatric=False, db_name=DBNAME) -> dict:
    """
    Generates a random diagnosis from the icpc2 table based on the given filters.

    Parameters:
        domain (str): include only diagnoses for the given domain (speciality or subspeciality)
        include_female_only (bool): If False, excludes diagnoses related to female-only issues.
        include_paediatric (bool): If False, excludes paediatric diagnoses.
        db_name (str): The name of the database file.

    Returns:
        dict: A dictionary containing the code, issue, and domain of the random diagnosis.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Set row_factory to sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT code, issue, domain  FROM icpc2" 
    andclause=False
    params={}
    if domain:
        params['domain'] = domain
        query += " WHERE domain = :domain"
        andclause = True
    if not include_paediatric:
        joinclause = " AND" if andclause else " WHERE" 
        query += joinclause
        query += " domain not like '%paed%'"
        andclause = True
    if not include_female_only:
        joinclause = " AND" if andclause else " WHERE" 
        query += joinclause
        query += " domain not like '%gynae%' AND domain not like '%obstet%'"
    query += " COLLATE NOCASE ORDER BY RANDOM() LIMIT 1;"
    cursor.execute(query, params)
    result = cursor.fetchone()
    if result:
        return dict(result)
    else:
        return {}    

   
def random_speciality(generalist_ratio : float = 0.7, db_name : str = DBNAME) -> str :
    """
    generates a random medical speciality based on the generalist-specialist ratio

    Parameters:
        generalist_ratio (float): The ratio of generalists to specialists.
        db_name (str): The name of the database file.

    Returns:
        str: The randomly selected medical speciality.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory  = sqlite3.Row   # Set row_factory to sqlite3.Row
    cursor = conn.cursor()
    #decide whether to generate specialist or generalist based on ratio odds:
    if random.random() < generalist_ratio:
        return("General Practice")
    #odds against a GP, select another speciality at random from the database
    query = "SELECT speciality, subspeciality FROM medical_specialities ORDER BY RANDOM() LIMIT 1;"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return(result['speciality'] if not result['subspeciality'] else result['subspeciality'])
    else:
        return 'General Practice'


if __name__ == "__main__":
    #create_database()
    #create_facility_types_table()
    #create_medical_facility_table()
    print(random_facility())
    print(random_diagnosis())
    print(random_speciality())
    print(random_speciality(generalist_ratio=0.5))
    print(random_speciality(generalist_ratio=0.3))
    print(random_speciality(generalist_ratio=0.1))
    print(random_speciality(generalist_ratio=0.9))