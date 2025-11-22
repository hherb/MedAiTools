# Synthetic Data Generation Modules

This document covers the synthetic health data generation capabilities in MedAiTools.

## Overview

MedAiTools can generate realistic synthetic patient data for:
- Testing healthcare applications
- Training machine learning models
- Educational purposes
- Research without privacy concerns

| Module | Purpose |
|--------|---------|
| synthetic_demographics | Australian population data |
| synthetic_health_record_generator | Clinical notes |
| SyntheticHealthData | Patient encounters |
| MedicalData | Medical reference data |
| RandomData | Random utilities |

---

## synthetic_demographics

**File:** `synthetic_demographics.py`

Generates realistic Australian demographic data.

### Main Function

#### create_synthetic_person()

```python
from synthetic_demographics import create_synthetic_person

person = create_synthetic_person(
    age: int | None = None,      # Specific age (or random)
    gender: str | None = None,   # 'M', 'F', or None for random
    state: str | None = None     # Australian state code
) -> dict
```

**Returns:**
```python
{
    "given_name": "John",
    "family_name": "Smith",
    "full_name": "John Smith",
    "date_of_birth": "1979-05-15",
    "age": 45,
    "gender": "M",
    "gender_string": "Male",
    "address": "42 Collins Street",
    "suburb": "Melbourne",
    "postcode": "3000",
    "state": "VIC",
    "full_address": "42 Collins Street, Melbourne VIC 3000",
    "medicare_number": "2345 67890 1",
    "phone": "0412 345 678",
    "email": "john.smith@email.com",
    "occupation": "Software Engineer",
    "marital_status": "Married",
    "emergency_contact": {
        "name": "Jane Smith",
        "relationship": "Spouse",
        "phone": "0423 456 789"
    }
}
```

**Example:**
```python
# Random person
person = create_synthetic_person()

# Specific demographics
person = create_synthetic_person(age=65, gender='F', state='NSW')

# Generate multiple
patients = [create_synthetic_person() for _ in range(100)]
```

### Supporting Functions

```python
from synthetic_demographics import (
    get_random_address,
    get_random_postcode,
    get_random_name,
    get_random_phone,
    get_random_email,
    get_random_medicare_number
)

# Get random address in specific state
address = get_random_address(state="VIC")

# Get random postcode for state
postcode = get_random_postcode(state="NSW")

# Get random name by gender
name = get_random_name(gender="F")  # Returns (given_name, family_name)

# Generate Medicare number
medicare = get_random_medicare_number()  # "1234 56789 0"
```

### State Codes

Australian state/territory codes:
- NSW - New South Wales
- VIC - Victoria
- QLD - Queensland
- SA - South Australia
- WA - Western Australia
- TAS - Tasmania
- NT - Northern Territory
- ACT - Australian Capital Territory

---

## synthetic_health_record_generator

**File:** `synthetic_health_record_generator.py`

Generates realistic clinical notes using LLM.

### Main Functions

#### generate_health_record()

```python
from synthetic_health_record_generator import generate_health_record

note = generate_health_record(
    person: dict,                    # Person from create_synthetic_person()
    encounter_type: str = "consultation",  # Type of encounter
    diagnosis: str | None = None,    # Specific diagnosis
    facility: dict | None = None,    # Healthcare facility
    provider: dict | None = None,    # Healthcare provider
    **kwargs
) -> str
```

**Example:**
```python
from synthetic_demographics import create_synthetic_person
from synthetic_health_record_generator import generate_health_record

# Create patient
person = create_synthetic_person(age=55, gender='M')

# Generate consultation note
note = generate_health_record(
    person,
    encounter_type="consultation",
    diagnosis="Type 2 Diabetes Mellitus"
)
print(note)
```

**Output (SOAP note format):**
```
CONSULTATION NOTE

Patient: John Smith
DOB: 1969-03-15 (Age: 55)
Medicare: 2345 67890 1
Date: 2024-01-20

SUBJECTIVE:
Mr. Smith presents today for routine follow-up of his Type 2 Diabetes.
He reports...

OBJECTIVE:
Vitals: BP 138/82, HR 76, Temp 36.8°C
Weight: 92kg, Height: 178cm, BMI: 29.0
Physical examination...

ASSESSMENT:
1. Type 2 Diabetes Mellitus - suboptimal control
2. Overweight

PLAN:
1. Continue metformin 1000mg BD
2. Lifestyle counseling provided
3. HbA1c in 3 months
4. Follow-up in 6 weeks
```

#### generate_synthetic_note()

Lower-level function for custom note generation:

```python
from synthetic_health_record_generator import generate_synthetic_note

note = generate_synthetic_note(
    template: str,      # Note template
    variables: dict,    # Template variables
    llm: LLM | None = None
) -> str
```

### Encounter Types

- `consultation` - GP consultation
- `emergency` - Emergency department visit
- `admission` - Hospital admission
- `discharge` - Discharge summary
- `referral` - Specialist referral letter
- `procedure` - Procedure note
- `progress` - Progress note

```python
# Emergency note
note = generate_health_record(
    person,
    encounter_type="emergency",
    diagnosis="Acute appendicitis"
)

# Discharge summary
note = generate_health_record(
    person,
    encounter_type="discharge",
    diagnosis="Myocardial infarction",
    admission_date="2024-01-15",
    discharge_date="2024-01-20"
)
```

### Custom Templates

```python
custom_template = """
PROGRESS NOTE

Patient: {patient_name}
Date: {date}
Ward: {ward}

Clinical Status:
{clinical_status}

Plan:
{plan}
"""

note = generate_synthetic_note(
    template=custom_template,
    variables={
        "patient_name": person["full_name"],
        "date": "2024-01-20",
        "ward": "Cardiology",
        "clinical_status": "Generate clinical status for post-MI day 3",
        "plan": "Generate appropriate plan"
    }
)
```

---

## SyntheticHealthData

**File:** `SyntheticHealthData.py`

Structured synthetic patient data generation.

### Main Functions

#### generate_patient()

```python
from SyntheticHealthData import generate_patient

patient = generate_patient(
    include_history: bool = True,
    num_conditions: int = 3
) -> dict
```

**Returns:**
```python
{
    "demographics": {...},  # From create_synthetic_person
    "conditions": [
        {"code": "E11", "name": "Type 2 Diabetes", "onset": "2020-01-15"},
        {"code": "I10", "name": "Essential Hypertension", "onset": "2018-06-01"},
        ...
    ],
    "medications": [
        {"name": "Metformin", "dose": "1000mg", "frequency": "BD"},
        ...
    ],
    "allergies": [
        {"substance": "Penicillin", "reaction": "Rash"}
    ],
    "immunizations": [...],
    "family_history": [...],
    "social_history": {...}
}
```

#### generate_encounter()

```python
from SyntheticHealthData import generate_encounter

encounter = generate_encounter(
    patient: dict,
    encounter_type: str = "consultation"
) -> dict
```

**Returns:**
```python
{
    "id": "ENC-12345",
    "patient_id": "PAT-67890",
    "type": "consultation",
    "date": "2024-01-20",
    "facility": {...},
    "provider": {...},
    "reason": "Routine diabetes follow-up",
    "diagnosis": [...],
    "procedures": [...],
    "medications_prescribed": [...],
    "notes": "Clinical note text..."
}
```

### Batch Generation

```python
from SyntheticHealthData import generate_patient_cohort

# Generate cohort with specific characteristics
cohort = generate_patient_cohort(
    size=100,
    age_range=(40, 70),
    conditions=["diabetes", "hypertension"],
    gender_ratio=0.5
)
```

---

## MedicalData

**File:** `MedicalData.py`

Medical reference data and random medical data generation.

### Functions

#### random_diagnosis()

```python
from MedicalData import random_diagnosis

diagnosis = random_diagnosis(
    category: str | None = None  # Optional category filter
) -> dict
```

**Returns:**
```python
{
    "code": "E11.9",
    "icd10": "E11.9",
    "icpc2": "T90",
    "name": "Type 2 diabetes mellitus without complications",
    "category": "Endocrine"
}
```

#### random_facility()

```python
from MedicalData import random_facility

facility = random_facility(
    type: int = 1  # 1=hospital, 2=clinic, 3=aged care
) -> dict
```

**Returns:**
```python
{
    "name": "Royal Melbourne Hospital",
    "type": "Hospital",
    "address": "300 Grattan Street, Parkville VIC 3050",
    "phone": "03 9342 7000"
}
```

#### random_speciality()

```python
from MedicalData import random_speciality

specialty = random_speciality()
# Returns: "Cardiology", "Neurology", etc.
```

#### random_medication()

```python
from MedicalData import random_medication

medication = random_medication(
    condition: str | None = None  # For condition-specific meds
)
```

**Returns:**
```python
{
    "name": "Metformin",
    "generic": "Metformin hydrochloride",
    "class": "Biguanide",
    "indication": "Type 2 Diabetes",
    "common_doses": ["500mg", "850mg", "1000mg"]
}
```

### Reference Data

The module loads reference data from `seed_data/`:

```python
from MedicalData import (
    get_all_diagnoses,
    get_all_facilities,
    get_all_specialities,
    get_all_medications
)

diagnoses = get_all_diagnoses()
facilities = get_all_facilities()
```

---

## RandomData

**File:** `RandomData.py`

Random data utilities.

### Functions

```python
from RandomData import (
    get_random_genderstring,
    get_random_date,
    randomize_date_format,
    get_random_time,
    get_random_weight,
    get_random_height,
    get_random_blood_pressure
)

# Random gender
gender = get_random_genderstring()  # "Male" or "Female"

# Random date in range
date = get_random_date(min_year=1950, max_year=2000)

# Randomize date format
formatted = randomize_date_format(date)  # Various formats

# Random vitals
weight = get_random_weight(gender="M", age=45)
height = get_random_height(gender="M")
bp = get_random_blood_pressure(age=45)  # (systolic, diastolic)
```

---

## RandomDateFormat

**File:** `RandomDateFormat.py`

Date formatting utilities.

```python
from RandomDateFormat import (
    format_date,
    parse_date,
    random_date_format
)

# Format to specific pattern
formatted = format_date("2024-01-15", "%d/%m/%Y")  # "15/01/2024"

# Parse various formats
date = parse_date("15/01/2024")  # datetime object

# Random format
formatted = random_date_format("2024-01-15")
# Could be: "15/01/2024", "January 15, 2024", "2024-01-15", etc.
```

---

## Complete Example

```python
from synthetic_demographics import create_synthetic_person
from synthetic_health_record_generator import generate_health_record
from MedicalData import random_diagnosis, random_facility
from SyntheticHealthData import generate_patient, generate_encounter

# Generate complete patient dataset
def generate_synthetic_dataset(num_patients: int = 100):
    """Generate a complete synthetic patient dataset."""

    dataset = []

    for i in range(num_patients):
        # Create patient
        patient = generate_patient(
            include_history=True,
            num_conditions=3
        )

        # Generate encounters
        num_encounters = random.randint(3, 10)
        encounters = []

        for _ in range(num_encounters):
            encounter = generate_encounter(
                patient,
                encounter_type=random.choice([
                    "consultation", "emergency", "procedure"
                ])
            )
            encounters.append(encounter)

        patient["encounters"] = encounters
        dataset.append(patient)

    return dataset

# Generate and save
dataset = generate_synthetic_dataset(100)

# Export to JSON
import json
with open("synthetic_patients.json", "w") as f:
    json.dump(dataset, f, indent=2, default=str)
```

---

## Privacy Note

All generated data is synthetic and does not correspond to real individuals. The data is designed to be statistically realistic but completely fictional.

## Related Modules

- [LLM](core-llm.md) - Used for clinical note generation
- [Settings](core-settings.md) - Configuration
