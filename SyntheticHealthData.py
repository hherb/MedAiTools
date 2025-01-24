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
from synthetic_demographics import (
    create_synthetic_person, 
    read_address, 
    get_random_phone_number, 
    random_name, 
    contact_relations,
    is_within_odds,
    is_female)
from MedicalData import random_diagnosis, random_facility, random_speciality
from RandomData import get_random_genderstring, randomize_date_format, get_randomized_time, get_random_date
from textwrap import dedent

__version__= 0.06

DEFAULT_MODEL='qwen2.5:7b-instruct-q8_0'
#DEFAULT_MODEL='qwen2.5:14b-instruct-q8_0'
#DEFAULT_MODEL='qwen2.5:32b-instruct-q8_0'
### DOES NOT WORK ##### DEFAULT_MODEL="granite3-dense:8b-instruct-q8_0"


PROGRESSNOTE_TEMPLATE="""As an experienced Australian GP Dr {{doctor_name}}, write a detailed progress note for a patient.
    Include, if and where appropriate, only  placeholders in {{ }} for identifying some or all the data listed here:
    >> {prompt_data} <<.
    For example, instead of writing the patient's name, write {{name}}.
    Include that data with natural fluency as it would appear in a health record. 
    Medication details do not count as identifying details.
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

SPECIALIST_REPORT_TEMPLATE=""" As an Australian {{specialist}}, Dr {{doctor_name}}, working at {{medical_facility}}, write a medical
report to the patient's regular GP. Include, where appropriate, as placeholders for identifying the data listed in curly brackets as follows:
    >> {prompt_data} <<.
    For example, instead of writing the patient's name, write {{name}}.
    Include that data with natural fluency as it would appear in a specialist report. 
    Medication details do not count as identifying details. 
    DO NOT include any other personal identifying data in the response, only those from the list of placeholders. 
    ATTENTION: Write as normal text (not as placeholder) all diagnoses, medical conditions, examination findings, medications, 
    prescriptions, and similar medical data in the response. Do not write any medication, previous medication, or treatment as a placeholder.
    """

PSYCHIATRIST_REPORT_TEMPLATE = """As an Australian psychiatrist, Dr {{doctor_name}}, working at {{medical_facility}}, write a medical
    report about the patient's mental health status and management options.
    Include, where appropriate, as placeholders for identifying the data listed in curly brackets as follows:
    >> {prompt_data} <<.
    Include that data with natural fluency as it would appear in a usual specialist report. 
    DO NOT include any other personal identifying data in the response, only those from the list of placeholders. 
    ATTENTION: Write as normal text (not as placeholder) all diagnoses, medical conditions, examination findings, medications, 
    prescriptions, and similar medical data in the response. Do not write any medication, previous medication, or treatment as a placeholder.
    """

RADIOLOGY_REPORT_TEMPLATE=""" As a radiologist, Dr {{doctor_name}}, working at {{medical_facility}}, write a radiology report to the patient's GP 
    regarding their {{investigation}}. 
    Include, where appropriate, as placeholders for identifying the data listed in curly brackets as follows:
    >> {prompt_data} <<.
    Include that data with natural fluency as it would appear in a usual specialist report. 
    DO NOT include any other personal identifying data in the response, only those from the list of placeholders. 
    ATTENTION: Write as normal text (not as placeholder) all diagnoses, medical conditions, examination findings, medications, 
    prescriptions, and similar medical data in the response. Do not write any medication, previous medication, or treatment as a placeholder.
    """

LABTEST_REPORT_TEMPLATE = """Generate a typical pathology test report for {{investigation}}. Sign as Dr {{doctor_name}}.
    Include, if and where appropriate, as placeholders for identifying the data listed in curly brackets as follows:
    >> {prompt_data} <<.  
    Include that data with natural fluency as it would appear in a usual pathology report. 
    DO NOT include any other personal identifying data in the response, only those from the list of placeholders.
    """

templates = {'progress_note': PROGRESSNOTE_TEMPLATE, 
             'specialist_report': SPECIALIST_REPORT_TEMPLATE, 
             'psychiatrist_report': PSYCHIATRIST_REPORT_TEMPLATE, 
             'radiology_report': RADIOLOGY_REPORT_TEMPLATE, 
             'labtest_report': LABTEST_REPORT_TEMPLATE}

template_types = templates.keys()


def calculate_age(dob_str, current_date_str=None):
    """
    Calculate the age of a person given their date of birth and an optional current date.
    The date of birth and current date should be in the format 'YYYY-MM-DD'.
    
    Args:
        dob_str (str): The date of birth of the person in the format 'YYYY-MM-DD'.
        current_date_str (str): The current date in the format 'YYYY-MM-DD' (default is the actual current date).

    Returns:
        int: The age of the person in years.
    """
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
    return(age)



def generate_patient_data_for_template(template_type='progress_note'):
    """
    Generate synthetic patient data for a given template type.
    
    Args:
        template_type (str): The type of template for which to generate the data.

    Returns:
        dict: A dictionary containing the synthetic patient data.
    """
    data = create_synthetic_person()
    address=read_address(address_id=data['address_id'])
    middlename = data.get('middlename', '') + ' '
    data['name'] = f"{data['firstname']} {middlename}{data['surname']}"
    data['medicare_number'] = f"{random.randint(2000, 9999)} {random.randint(10000, 99999)} {random.randint(1, 9)}"
    data['address'] = f"{address['street_number']} {address['street']}, {address['suburb']}, {address['state']} {address['postcode']}"   
    data['pbs_authority'] = f"{random.choice(string.ascii_uppercase)}{random.randint(1000, 9999)}"
    data['doctor_name'] = random_name()
    data['medical_facility'] = random_facility()
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

    match template_type:
        case 'progress_note':
            data['condition'] = random_diagnosis(include_paediatric=data['age']<16, include_female_only=data['gender'].lower()=='f')
        case 'specialist_report':
            data['speciality'] = random_speciality(generalist_ratio=0.0)
            data['referring_doctor'] = random_name()
            if 'gynae' in data['speciality'].lower() or 'obstetric' in data['speciality'].lower():
                data['condition'] = random_diagnosis(include_female_only=True, include_paediatric=data['age']<16)
            else:
                data['condition'] = random_diagnosis(domain=data['speciality'], include_paediatric=data['age']<16)
        case 'psychiatrist_report':
            data['speciality'] = 'Psychiatry'
            data['condition'] = random_diagnosis(domain='Psychiatry', include_paediatric=data['age']<16)
        case 'radiology_report':
            data['speciality'] = 'Radiology'
            data['condition'] = random_diagnosis(include_paediatric=data['age']<16)
        case 'labtest_report':
            data['speciality'] = 'Pathology'

    #remove any empty values from the dictionary before returning
    data = {k: v for k, v in data.items() if v is not None and str(v).strip() > ''}    
    return(data)



class Synthetic_Health_Data:
    """
    A class for generating synthetic health data using a template and a language model.
    
    Attributes:
        prompt_template (str): The template for generating prompts.
        model (str): The language model to use for generation
        
        Methods:
            create_prompt(data: dict) -> str: Create a prompt from the template using the given data.
            generate(data: dict) -> tuple[str, str, dict]: Generate a response using the prompt and the model.
            annotate_template(template: str, data: dict) -> tuple[str, dict]: Annotate the template with the data.

    """
    def __init__(self, prompt_template : str, model : str = DEFAULT_MODEL):
        self.prompt_template = prompt_template
        self.model= model

    def create_prompt(self, data:dict):
        """Create a prompt for the template using the given data."""
        data['prompt_data'] = str(data)
        #print(f"PROMPT_DATA: {data['prompt_data']}")
        prompt =  self.prompt_template.format(**data)
        return(prompt)

    def generate(self, data : dict):
        """Generate a response using the prompt and the model."""
        prompt = self.create_prompt(data)
        response = ollama.generate(model=self.model, prompt=prompt, stream=False)['response']
        note, annotation= self.annotate_template(template=response, data=data) 
        return(response, note, annotation)
    
    def annotate_template(self, template : str, data : dict) -> tuple[str, dict]:
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



class GP_Progress_Note(Synthetic_Health_Data):
    def __init__(self, prompt_template=PROGRESSNOTE_TEMPLATE):
        super().__init__(prompt_template)
    
    def create_prompt(self, data : dict):
        #data['prompt_data'] = str(data)
        data['prompt_data'] = [key for key in data.keys()]  #list of keys in the data dictionary
        #print(f"PROMPT_DATA: {data['prompt_data']}")
        prompt =  self.prompt_template.format(**data)
        if is_female(data['gender']) and is_within_odds(5):
         prompt += "Include a sentence that the patient's maiden name was {maidenname}.\n"

        if is_within_odds(6):
            prompt += "Include a sentence that the patient's alias is {alias}.\n"

        if is_within_odds(3):
            prompt += """"Include that the patient said to contact them through their {contact_relation} on {relation_phone}"\n"""
        

        prompt += "The purpose is to generate synthetic data for training NER models. Do not include '{' characters other than for placeholders.\n"

        prompt += """Use Australian medical terminology and conventions, and metric units (e.g. degress Celsius for temperature). 
        Include the patient's identifying details naturally throughout the note.
        Answer with ONLY the progress notes, no additional information, no additional comments."""
        return(prompt)
    

class Specialist_Report(Synthetic_Health_Data):
    def __init__(self, prompt_template=SPECIALIST_REPORT_TEMPLATE):
        super().__init__(prompt_template)
    
    def create_prompt(self, data : dict):
        data['prompt_data'] = str(data)
        prompt =  self.prompt_template.format(**data)

        if is_female(data['gender']) and is_within_odds(5):
            prompt += "Include a sentence that the patient's maiden name was {maidenname}.\n"

        if is_within_odds(6):
            prompt += "Include a sentence that the patient's alias is {alias}.\n"

        if is_within_odds(3):
            prompt += """"Include that the patient said to contact them through their {contact_relation} on {relation_phone}"\n"""
        

        prompt += "The purpose is to generate synthetic data for training NER models. Do not include '{' characters other than for placeholders.\n"

        prompt += """Use Australian medical terminology and conventions, and metric units (e.g. degress Celsius for temperature). 
        Include the patient's identifying details naturally throughout the note.
        Answer with ONLY the report, no additional information, no additional comments."""
        return(prompt)
    

    
class Psychiatrist_Report(Synthetic_Health_Data):
    def __init__(self, prompt_template=PSYCHIATRIST_REPORT_TEMPLATE):
        super().__init__(prompt_template)
    
    def create_prompt(self, data : dict):
        data['prompt_data'] = str(data)
        prompt =  self.prompt_template.format(**data)

        if is_female(data['gender']) and is_within_odds(5):
            prompt += "Include a sentence that the patient's maiden name was {maidenname}.\n"

        if is_within_odds(6):
            prompt += "Include a sentence that the patient's alias is {alias}.\n"

        if is_within_odds(3):
            prompt += """"Include that the patient said to contact them through their {contact_relation} on {relation_phone}"\n"""
        

        prompt += "The purpose is to generate synthetic data for training NER models. Do not include '{' characters other than for placeholders.\n"

        prompt += """Use Australian medical terminology and conventions, and metric units (e.g. degress Celsius for temperature). 
        Include the patient's identifying details naturally throughout the note.
        Answer with ONLY the report, no additional information, no additional comments."""
        return(prompt)


class Radiology_Report(Synthetic_Health_Data):
    def __init__(self, prompt_template=RADIOLOGY_REPORT_TEMPLATE):
        super().__init__(prompt_template)
    
    def create_prompt(self, data : dict):
        data['prompt_data'] = str(data)
        prompt =  self.prompt_template.format(**data)

        if is_female(data['gender']) and is_within_odds(5):
            prompt += "Include a sentence that the patient's maiden name was {maidenname}.\n"

        if is_within_odds(6):
            prompt += "Include a sentence that the patient's alias is {alias}.\n"

        if is_within_odds(3):
            prompt += """"Include that the patient said to contact them through their {contact_relation} on {relation_phone}"\n"""
        

        prompt += "The purpose is to generate synthetic data for training NER models. Do not include '{' characters other than for placeholders.\n"

        prompt += """Use Australian medical terminology and conventions, and metric units (e.g. degress Celsius for temperature). 
        Include the patient's identifying details naturally throughout the note.
        Answer with ONLY the report, no additional information, no additional comments."""
        return(prompt)
    


def main(template='gp_progress_note', num_records=1, model=DEFAULT_MODEL, output_dir='synthetic_records'):  
    """
    Generate synthetic health records using the specified template and model.

    Args:
        template (str): The type of template to use for generating the records.
        num_records (int): The number of records to generate.
        model (str): The language model to use for generation.
        output_dir (str): The directory to save the generated records in.
    """
    response_ext = '.res'
    note_ext = '.txt'
    annotation_ext = '.ann'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir) 

    match template:
        case 'gp_progress_note':
            generator = GP_Progress_Note
        case 'specialist_report':
            generator = Specialist_Report
        case 'psychiatrist_report':
            generator = Psychiatrist_Report
        case 'radiology_report':
            generator = Radiology_Report
        case _:
            print(f"Invalid template type: {template}")
            sys.exit(1)

    for num in tqdm(range(0, num_records), desc="Generating records"):  
        note = generator()
        patient_data = generate_patient_data_for_template(template_type=template)
        response, note, annotation = note.generate(patient_data)
        with open(os.path.join(output_dir, f"record_{num}{response_ext}"), 'w') as f:
            f.write(response)
        with open(os.path.join(output_dir, f"record_{num}{note_ext}"), 'w') as f:
            f.write(note)
        with open(os.path.join(output_dir, f"record_{num}{annotation_ext}"), 'w') as f:
            for a in annotation:
                f.write(f"T{a['sequence_number']} {a['placeholder']} {a['start_pos']} {a['end_pos']} {a['value']}\n")



if __name__ == '__main__':
    main()


