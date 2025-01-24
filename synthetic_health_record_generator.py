import os
import re
import string
import random
import datetime as dt
import argparse
import sys
from tqdm import tqdm
from pprint import pprint
import ollama
from synthetic_demographics import create_synthetic_person, read_address, get_random_phone_number
from annotation_categorizer import read_terms, categorize_annotations

__version__= 0.06
DEFAULT_MODEL='qwen2.5:7b-instruct-q8_0'

role_prompts = ["""You are an experienced Australian GP. Write a progress note for a patient.""",
                """You are an Australian General Surgeon. Write an operation report for a patient for whom you just performed a surgical procedure""",
                """you are a junior doctor at an Australian Hospital on the general medical ward. Write a dischare summary to the patient's GP""",
                """You are an Oncologist at an Australian provate practice. Write a report for a patient who has been diagnosed with cancer.""",
                """You are a psychiatrist at an Australian hospital. Write a diary entry for a patient who is suffering from psychosis.""",]


# Expanded sample data for Australian context
australian_suburbs = ['Bondi', 'St Kilda', 'Surry Hills', 'Carlton', 'West End', 'Fremantle', 'Newtown', 'Brunswick', 'Manly', 'South Brisbane', 'Fitzroy', 'Parramatta', 'Toowong', 'Northbridge', 'Randwick', 'Richmond', 'Paddington', 'North Adelaide', 'Darlinghurst', 'South Yarra']
common_conditions = ['Hypertension', 'Type 2 Diabetes', 'Asthma', 'Anxiety', 'Depression', 'Osteoarthritis', 'GERD', 'Hypothyroidism', 'Chronic Back Pain', 'Insomnia', 'Migraine', 'Allergic Rhinitis', 'Eczema', 'IBS', 'Hyperlipidemia']

# Expanded list of names with gender associations
common_names = {
    'male': ['Liam', 'Noah', 'Oliver', 'William', 'Elijah', 'James', 'Benjamin', 'Lucas', 'Henry', 'Alexander', 'Mason', 'Michael', 'Ethan', 'Daniel', 'Jacob', 'Logan', 'Jackson', 'Sebastian', 'Jack', 'Aiden', 'Owen', 'Samuel', 'Matthew', 'Joseph', 'Levi', 'Mateo', 'David', 'John', 'Wyatt', 'Carter', 'Julian', 'Luke', 'Grayson', 'Isaac', 'Jayden', 'Theodore', 'Gabriel', 'Anthony', 'Dylan', 'Leo', 'Lincoln', 'Jaxon', 'Asher', 'Christopher', 'Josiah', 'Andrew', 'Thomas', 'Joshua', 'Ezra', 'Hudson'],
    'female': ['Olivia', 'Emma', 'Ava', 'Charlotte', 'Sophia', 'Amelia', 'Isabella', 'Mia', 'Evelyn', 'Harper', 'Camila', 'Gianna', 'Abigail', 'Luna', 'Ella', 'Elizabeth', 'Sofia', 'Emily', 'Avery', 'Mila', 'Scarlett', 'Eleanor', 'Madison', 'Layla', 'Penelope', 'Aria', 'Chloe', 'Grace', 'Ellie', 'Nora', 'Hazel', 'Zoey', 'Riley', 'Victoria', 'Lily', 'Aurora', 'Violet', 'Nova', 'Hannah', 'Emilia', 'Zoe', 'Stella', 'Everly', 'Isla', 'Leah', 'Lillian', 'Addison', 'Willow', 'Lucy', 'Paisley']
}

common_last_names = ['Smith', 'Jones', 'Williams', 'Brown', 'Wilson', 'Taylor', 'Johnson', 'White', 'Martin', 'Anderson', 'Thompson', 'Nguyen', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Green', 'Baker', 'Adams', 'Nelson', 'Hill', 'Ramirez', 'Campbell', 'Mitchell', 'Roberts', 'Carter', 'Phillips', 'Evans', 'Turner', 'Torres', 'Parker', 'Collins', 'Edwards', 'Stewart', 'Flores', 'Morris', 'Nguyen', 'Murphy', 'Rivera', 'Cook', 'Rogers', 'Morgan', 'Peterson', 'Cooper', 'Reed', 'Bailey', 'Bell', 'Gomez', 'Kelly', 'Howard', 'Ward', 'Cox', 'Diaz', 'Richardson', 'Wood', 'Watson', 'Brooks', 'Bennett', 'Gray', 'James', 'Reyes', 'Cruz', 'Hughes', 'Price', 'Myers', 'Long', 'Foster', 'Sanders', 'Ross', 'Morales', 'Powell', 'Sullivan', 'Russell', 'Ortiz', 'Jenkins', 'Gutierrez', 'Perry', 'Butler', 'Barnes', 'Fisher', 'Henderson', 'Coleman', 'Simmons', 'Patterson', 'Jordan', 'Reynolds', 'Hamilton', 'Graham', 'Kim', 'Gonzales', 'Alexander', 'Ramos', 'Wallace', 'Griffin', 'West', 'Cole', 'Hayes', 'Chavez', 'Gibson', 'Bryant', 'Ellis', 'Stevens', 'Murray', 'Ford']
#add some hypened names
for i in range(int(len(common_last_names)/10)):
    common_last_names.append(f"{random.choice(common_last_names)}-{random.choice(common_last_names)}")


doctor_names = ['Smith', 'Campbell', 'Nguyen', 'Nayak', 'Myers', 'Hauser', 'Simon', 'Patel', 'Jones', 'Brown', 'Williams', 'Taylor', 'Johnson', 'White', 'Martin', 'Anderson', 'Thompson', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Green', 'Baker', 'Adams', 'Nelson', 'Hill', 'Ramirez', 'Campbell', 'Mitchell', 'Roberts', 'Carter', 'Phillips', 'Evans', 'Turner', 'Torres', 'Parker', 'Collins', 'Edwards', 'Stewart', 'Flores', 'Morris', 'Murphy', 'Rivera', 'Cook', 'Rogers', 'Morgan', 'Peterson', 'Cooper', 'Reed', 'Bailey', 'Bell', 'Gomez', 'Kelly', 'Howard', 'Ward', 'Cox', 'Diaz', 'Richardson', 'Wood', 'Watson', 'Brooks', 'Bennett', 'Gray', 'James', 'Reyes', 'Cruz', 'Hughes', 'Price', 'Myers', 'Long', 'Foster', 'Sanders', 'Ross', 'Morales', 'Powell', 'Sullivan', 'Russell', 'Ortiz', 'Jenkins', 'Gutierrez', 'Perry', 'Butler', 'Barnes', 'Fisher', 'Henderson', 'Coleman', 'Simmons', 'Patterson', 'Jordan', 'Reynolds', 'Hamilton', 'Graham', 'Kim', 'Gonzales', 'Alexander', 'Ramos', 'Wallace', 'Griffin', 'West', 'Cole', 'Hayes', 'Chavez', 'Gibson', 'Bryant', 'Ellis', 'Stevens', 'Murray', 'Ford']

contact_relations = ['father', 'mother', 'grandfather', 'grandmother', 'uncle', 'aunt', 'nephew', 'niece', 'cousin', 'friend', 'partner', 'spouse', 'sibling', 'child', 'son', 'daughter', 'brother', 'sister', 'friend']

medical_facilities = ['Cooktown Medical Centre', 'Cooktown Hospital', 'Wujal Wujal AMS', 'Royal Melbourne Hospital', 'St Vincent\'s Hospital', 'Royal Prince Alfred Hospital', 'Royal North Shore Hospital', 'Westmead Hospital', 'Royal Brisbane and Women\'s Hospital', 'Princess Alexandra Hospital', 'Royal Adelaide Hospital', 'Flinders Medical Centre', 'Fremantle Hospital', 'Royal Perth Hospital', 'Royal Hobart Hospital', 'Canberra Hospital', 'Royal Darwin Hospital']

def generate_australian_address():
    # Lists of common Australian street names, types, suburbs, and states
    street_names = ['High', 'Park', 'Church', 'Main', 'George', 'Victoria', 'Elizabeth', 'King', 'Queen', 'William',
                    'Wattle', 'Acacia', 'Banksia', 'Eucalyptus', 'Kangaroo', 'Wallaby', 'Koala', 'Emu', 'Kookaburra',
                    'Waratah', 'Bottlebrush', 'Jacaranda', 'Murray', 'Darling', 'Swan', 'Yarra', 'Brisbane', 'Paramatta']
    street_types = ['Street', 'Avenue', 'Road', 'Drive', 'Court', 'Place', 'Crescent', 'Way', 'Lane', 'Parade']
    suburbs = ['Southbank', 'Richmond', 'St Kilda', 'Bondi', 'Manly', 'Surry Hills', 'Newtown', 'Fremantle', 
               'West End', 'Fortitude Valley', 'New Farm', 'Glenelg', 'Henley Beach', 'Sandy Bay', 'Battery Point']
    states = {
        'NSW': ('2000', '2999'),
        'VIC': ('3000', '3999'),
        'QLD': ('4000', '4999'),
        'WA': ('6000', '6999'),
        'SA': ('5000', '5999'),
        'TAS': ('7000', '7999'),
        'NT': ('0800', '0899'),
        'ACT': ('2600', '2618')
    }

    # Generate random components
    street_number = random.randint(1, 999)
    street_name = random.choice(street_names)
    street_type = random.choice(street_types)
    suburb = random.choice(suburbs)
    state = random.choice(list(states.keys()))
    postcode = str(random.randint(int(states[state][0]), int(states[state][1])))

    # Construct the address
    address = f"{street_number} {street_name} {street_type}, {suburb} {state} {postcode}"
    return address

def odds_are_one_in(odds):
    return random.randint(1, odds) == 1

def is_female(genderstring):
    return genderstring.lower() in ['female', 'f', 'woman', 'fem', 'xx', 'girl']


def get_random_genderstring(gender : chr, is_adult:bool = True) -> str:
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


def get_random_date(from_days_ago=365):
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=365)  # one year ago
    return start_date + dt.timedelta(days=random.randint(0, from_days_ago))


def generate_patient_data():
    gender = random.choice(['male', 'female'])
    first_name = random.choice(common_names[gender])
    last_name = random.choice(common_last_names)
    dob = (dt.datetime.now() - dt.timedelta(days=random.randint(6570, 31025))).strftime("%Y-%m-%d")  # 18 to 85 years old
    address= generate_australian_address()
    condition = random.choice(common_conditions)
    medicare_number = f"{random.randint(2000, 9999)} {random.randint(10000, 99999)} {random.randint(1, 9)}"
    phone = f"04{random.randint(10000000, 99999999)}"
    
    return {
        "doctor_name": random.choice(list(doctor_names)),
        "first_name": first_name,
        "last_name": last_name,
        "name": f"{first_name} {last_name}",
        "dob": dob,
        "gender": gender,
        "address": address,
        "condition": condition,
        "medicare": medicare_number,
        "phone": phone
    }

def calculate_age(dob_str, current_date_str=None):
    # Parse the date of birth string into a datetime object
    dob = dt.datetime.strptime(dob_str, "%Y-%m-%d")
    
    # Use the current date if not provided
    if current_date_str:
        current_date = dt.datetime.strptime(current_date_str, "%Y-%m-%d")
    else:
        current_date = dt.datetime.now()
    
    # Calculate the difference in years
    age = current_date.year - dob.year
    
    # Adjust if the current date is before the birthday in the current year
    if (current_date.month, current_date.day) < (dob.month, dob.day):
        age -= 1
    
    return age

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

def generate_patient_data_for_template():
    data = create_synthetic_person()
    address=read_address(address_id=data['address_id'])
    middlename = data.get('middlename', '') + ' '
    data['name'] = f"{data['firstname']} {middlename}{data['surname']}"
    data['medicare_number'] = f"{random.randint(2000, 9999)} {random.randint(10000, 99999)} {random.randint(1, 9)}"
    data['condition'] = random.choice(common_conditions)
    data['address'] = f"{address['street_number']} {address['street']}, {address['suburb']}, {address['state']} {address['postcode']}"   
    data['pbs_authority'] = f"{random.choice(string.ascii_uppercase)}{random.randint(1000, 9999)}"
    data['doctor_name'] = random.choice(doctor_names)
    data['medical_facility'] = random.choice(medical_facilities)
    data['consultation_date'] = randomize_date_format(get_random_date().strftime("%Y-%m-%d"))
    data['consultation_time'] = get_randomized_time(working_hours_only=False)
    data['contact_relation'] = random.choice(contact_relations)
    data['relation_phone'] = get_random_phone_number()
    data['age'] = calculate_age(data['dob'])
    data['dob'] = randomize_date_format(data['dob'])
    data['gender'] = get_random_genderstring(data['gender'], is_adult=data['age'] > 16) 
    for key in address.keys():
        if key.lower() not in ['id', 'address_id']:
            data[key] = address[key]
    #remove any empty values from the dictionary before returning
    data = {k: v for k, v in data.items() if v is not None and str(v).strip() > ''}    
    return(data)

def generate_progress_note(patient_data, model=DEFAULT_MODEL):
    prompt = f"""
    As an experienced Australian GP Dr {patient_data['doctor_name']}, write a detailed progress note for the following patient:
    Name: {patient_data['name']}
    DOB: {patient_data['dob']}
    Age: {dt.datetime.now().year - int(patient_data['dob'].split('/')[-1])}
    Gender: {patient_data['gender']}
    Medicare: {patient_data['medicare']}
    Phone: {patient_data['phone']}
    Address: {patient_data['address']}
    Known Condition: {patient_data['condition']}

    Location: {random.choice(medical_facilities)}

    ALWAYS include all of the following placeholders:
    0. Patient details
    1. Date and time of consultation
    2. Reason for visit
    3. Current symptoms
    4. Relevant medical history
    5. Examination findings
    6. Assessment
    7. Plan (including any prescriptions with PBS codes)
    8. Follow-up instructions

    """

    if is_female(patient_data['gender']) and odds_are_one_in(5):
        prompt += f"Include a sentence that the patient's maiden name was {random.choice(common_last_names)}.\n"

    if odds_are_one_in(6):
        prompt += f"Include a sentence that the patient's nick name is {random.choice(common_names['female']) if is_female(patient_data['gender']) else random.choice(common_names['male'])}.\n"

    if odds_are_one_in(3):
        prompt += f""""Include that the patient said to contact them through their {random.choice(contact_relations)} on [make up a phone number]"\n"""
    

    prompt += "The purpose is to generate synthetic data for training an anonymizer application."

    prompt += """Use Australian medical terminology and conventions, and metric units (e.g. degress Celsius for temperature). 
    Include the patient's identifying details naturally throughout the note.
    Answer with ONLY the progress notes, no additional information, no additional comments."""

    response= ollama.generate(model=model, prompt=prompt, stream=False)
    return(response)
   

def generate_progress_note_template(patient_data, model=DEFAULT_MODEL):
    #get all the keys of the patient data that are not None and > ''
    valid_patient_data = [f'{{{k}}}' for k, v in patient_data.items() if v is not None and str(v).strip() > '']
    prompt_data = ', '.join(valid_patient_data)

    prompt = f"""As an experienced Australian GP Dr {{doctor_name}}, write a detailed progress note for a patient.
    Include, where appropriate, as placeholders for identifying all the data listed in curly brackets as follows:
    >> {prompt_data} <<.
    Include that data with natural fluency as it would appear in a health record. 
    DO NOT include any other personal identifying data in the response, only those from the list of placeholders. 
    ATTENTION: Write as normal text (not as placeholder) all diagnoses, medical conditions, examination findings, medications, 
    prescriptions, and similar medical data in the response. Do not write any medication, previous medication, or treatment as a placeholder.
    
    ALWAYS include all of the following entities:
    0. placeholder for patient details (do not make up or use patient details, use only placeholders!)
    1. placeholders for date and time of consultation
    2. Reason for visit
    3. Current symptoms
    4. Relevant medical history
    5. Examination findings
    6. Assessment
    7. Plan (including any prescriptions whch may or may not require a PBS Authority code). If you use a PBS Authority code, 
    include it as {{pbs_authority}} placeholder
    8. Follow-up instructions
    
    """

    if is_female(patient_data['gender']) and odds_are_one_in(5):
         prompt += "Include a sentence that the patient's maiden name was {maidenname}.\n"

    if odds_are_one_in(6):
         prompt += "Include a sentence that the patient's alias is {alias}.\n"

    if odds_are_one_in(3):
         prompt += """"Include that the patient said to contact them through their {contact_relation} on {relation_phone}"\n"""
    

    prompt += "The purpose is to generate synthetic data for training NER models. Do not include '{' characters other than for placeholders.\n"

    prompt += """Use Australian medical terminology and conventions, and metric units (e.g. degress Celsius for temperature). 
    Include the patient's identifying details naturally throughout the note.
    Answer with ONLY the progress notes, no additional information, no additional comments."""

    response= ollama.generate(model=model, prompt=prompt, stream=False)['response']
    note, annotation= annotate_template(template=response, data=patient_data) 
    return(response, note, annotation)   


def annotate_template(template : str, data : dict) -> tuple[str, dict]:
    """add annotations to the template

    Args:
        template (str): a template text with placeholders in {}
        data (dict): data to replace the placeholders in the template

    Returns:
        tuple[str, dict]: annotated template and annotation data in the format F"T{n} {entity} (startpos) {endpos} {text}"
    """
    replacements = []
    sequence_number = 1
    offset=0
    #pprint(data)
    

    
    def replacement(match):
        nonlocal sequence_number
        nonlocal offset
        placeholder = match.group(1) #find something embedded with curly braces
        key = placeholder.strip('{}') #whatever is between the curly braces needs to be repalced with our data
        value = str(data.get(key, 'N/A'))  #if the key is not found in our data, we will just use a blank space
        if not value:
            value = placeholder
        start_pos = match.start()+offset
        end_pos = start_pos + len(value)
        replacements.append({
            'sequence_number': sequence_number,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'placeholder': key.upper(),
            'value': value
        })

        sequence_number += 1
        offset += len(value) - len(match.group(0))  # Adjust the offset

        return value
    
    pattern = re.compile(r'\{(\w+)\}')
    annotated_template = pattern.sub(replacement, template)
    
    return annotated_template, replacements


def get_most_recent_txt_file(directory='.', extension='.txt'):
    txt_files = [f for f in os.listdir(directory) if f.endswith(extension)]
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the directory")
    most_recent_file = max(txt_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
    return most_recent_file


def extract_digits_from_filename(filename, number_of_digits=6):
    # Use regex to find 6 digits before the '.txt' extension
    searchstr = f"(\\d{{{number_of_digits}}})\\.txt$"
    match = re.search(searchstr, filename)
    if match:
        # Convert the matched digits to an integer
        return int(match.group(1))
    else:
        raise ValueError(f"Filename does not contain {number_of_digits} digits before the '.txt' extension")


def get_next_record_number(directory='.', extension='.txt', number_of_digits=6):
    try:
        most_recent_file = get_most_recent_txt_file(directory=directory, extension=extension)
        return extract_digits_from_filename(most_recent_file, number_of_digits=number_of_digits) + 1
    except FileNotFoundError:
        return 1


def main_template(num_records=1, model=DEFAULT_MODEL, output_dir='synthetic_records'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #valid annotation terms ofr BERT training
    try:
        annotation_terms = read_terms()
        #pprint(annotation_terms)
    except FileNotFoundError:
        annotation_terms = {}
    
    start_record_number = get_next_record_number(directory=output_dir)

    for i in tqdm(range(start_record_number, start_record_number+num_records+1), desc="Generating records"):  
        patient_data = generate_patient_data_for_template()  
        template, note, annotation = generate_progress_note_template(patient_data, model=model)
        output_fname = f"{output_dir}/synthetic_record_{i:06}" 
        #pprint(annotation)
        #WSsys.exit()
        with open(output_fname+'.tpl', 'w') as f:
                f.write(template)
        with open(output_fname+'.txt', 'w') as f:
            f.write(note)
        with open(output_fname+'.anf', 'w') as f:
            for a in annotation:
                f.write(f"T{a['sequence_number']}\t {a['placeholder']} {a['start_pos']} {a['end_pos']}\t{a['value']}\n")
        with open(output_fname+'.ann', 'w') as f:
            sequence_number = 1
            for a in annotation:
                term=annotation_terms.get(a['placeholder'].upper(), '')
                if term:
                    f.write(f"T{sequence_number}:\t {term} {a['start_pos']} {a['end_pos']}\t{a['value']}\n")
                    sequence_number += 1



def main(num_records=1, model=DEFAULT_MODEL, output_file='synthetic_record.txt', append=True):  
    if output_file:
        with open(output_file, 'a' if append else 'w') as f:
            f.write("_"*80 + "\n")
            f.write(f"""Generated with generator version={__version__} on {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} with model {model}\n""")
            f.write("_"*80 + "\n")
    else:
        print("_"*80)
        print(f"""Generated with generator version={__version__} on {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} with model {model}""")
        print("_"*80)

    for i in tqdm(range(0, num_records), desc="Generating records"):  
        #patient_data = generate_patient_data()  
        patient_data = create_synthetic_person()
        template, note, annotation = generate_progress_note_template(patient_data, model=model)
        output_fname = f"{output_file}_{i:06}" if output_file else None
        if output_fname:
            with open(output_fname+'.txt', 'w') as f:
                f.write(note)
            with open(output_fname+'.ann', 'w') as f:
                for a in annotation:
                    f.write(f"T{a['sequence_number']} {a['entity']} {a['start_pos']} {a['end_pos']} {a['value']}\n")    
        else:
            print(note)
            print(annotation)
            print("_"*80)

def test(model=DEFAULT_MODEL):
    patient_data = generate_patient_data_for_template()
    template, note, annotation = generate_progress_note_template(patient_data, model=model)
    for a in annotation:
        print(f"T{a['sequence_number']} {a['placeholder']} {a['start_pos']} {a['end_pos']} {a['value']}")
        print(f"extracted from note: {note[a['start_pos']:a['end_pos']]}")
        assert a['value'] == note[a['start_pos']:a['end_pos']]
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate synthetic patient progress notes.')
    parser.add_argument('--annotate', type=str, default='N', required=False,  help='Annotate the generated notes (Y/N), default is "N"')
    parser.add_argument('--model', type=str, required=False, default=DEFAULT_MODEL, help='Model to use for generating notes')
    parser.add_argument('--num_records', type=int,  default=1, help='Number of records to create')
    parser.add_argument('--outfile', type=str, required=False, default='data', help='Output file prefix for generated records. If not specified, output to terminal')
    parser.add_argument('--out_dir', type=str, required=False, default='./synth', help='Output directory for generated records')
    parser.add_argument('--append', type=str, default='Y', help='Append to output file if exists (Y/N), default is "Y"')

        
    args = parser.parse_args()
    
    model = args.model or DEFAULT_MODEL  
    test(model=model)  #will fail if the annotations are not correct, and terminate the program
    num_records = args.num_records or 1
    output_dir=args.out_dir 
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    append = args.append.lower() == 'y'
    if args.annotate.lower() == 'y':
        main_template(num_records=num_records, model=model, output_dir=output_dir)
    else:
        main(num_records=num_records, model=model, output_dir=output_dir, output_file=args.outfile, append=append)   
    