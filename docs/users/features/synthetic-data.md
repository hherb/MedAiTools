# Synthetic Data Generator

Generate realistic synthetic patient data for research, testing, and education.

## Overview

The Synthetic Data Generator creates:
- Realistic patient demographics
- Clinical notes and encounters
- Medical histories
- Test data without privacy concerns

## Why Synthetic Data?

### Benefits
- **No privacy concerns:** Data is completely fictional
- **Testing:** Test healthcare applications safely
- **Training:** Train ML models without real patient data
- **Education:** Teach clinical documentation
- **Research:** Develop algorithms before real data access

### Characteristics
- Demographically realistic (Australian population)
- Clinically plausible
- Properly formatted
- Customizable parameters

## Getting Started

### Basic Usage (Python)

```python
from synthetic_demographics import create_synthetic_person

# Create a random person
patient = create_synthetic_person()

print(f"Name: {patient['full_name']}")
print(f"DOB: {patient['date_of_birth']}")
print(f"Address: {patient['full_address']}")
print(f"Medicare: {patient['medicare_number']}")
```

### With Specific Parameters

```python
# Create specific demographics
patient = create_synthetic_person(
    age=65,
    gender='F',
    state='NSW'
)
```

## Patient Data Fields

Each synthetic patient includes:

### Personal Information
| Field | Example |
|-------|---------|
| `given_name` | "Jennifer" |
| `family_name` | "Smith" |
| `full_name` | "Jennifer Smith" |
| `date_of_birth` | "1959-03-15" |
| `age` | 65 |
| `gender` | "F" |
| `gender_string` | "Female" |

### Contact Details
| Field | Example |
|-------|---------|
| `address` | "42 Collins Street" |
| `suburb` | "Melbourne" |
| `postcode` | "3000" |
| `state` | "VIC" |
| `full_address` | "42 Collins Street, Melbourne VIC 3000" |
| `phone` | "0412 345 678" |
| `email` | "jennifer.smith@email.com" |

### Healthcare Identifiers
| Field | Example |
|-------|---------|
| `medicare_number` | "2345 67890 1" |

### Additional Information
| Field | Example |
|-------|---------|
| `occupation` | "Retired Teacher" |
| `marital_status` | "Widowed" |
| `emergency_contact` | {name, relationship, phone} |

## Generating Clinical Notes

### Consultation Notes

```python
from synthetic_demographics import create_synthetic_person
from synthetic_health_record_generator import generate_health_record

# Create patient
patient = create_synthetic_person(age=55, gender='M')

# Generate consultation note
note = generate_health_record(
    patient,
    encounter_type="consultation",
    diagnosis="Type 2 Diabetes Mellitus"
)

print(note)
```

### Sample Output

```
CONSULTATION NOTE

Patient: John Smith
DOB: 1969-05-15 (Age: 55)
Medicare: 2345 67890 1
Date: 2024-01-20

SUBJECTIVE:
Mr. Smith presents for routine diabetes follow-up. He reports
generally feeling well. He has been checking blood sugars at home
with readings mostly between 7-10 mmol/L fasting. He admits to
occasional dietary indiscretions but has been trying to exercise
more regularly. No symptoms of hypoglycemia. No chest pain,
shortness of breath, or peripheral edema.

OBJECTIVE:
Vitals: BP 138/82, HR 76, Temp 36.8°C
Weight: 92kg, Height: 178cm, BMI: 29.0
General: Well-appearing, no acute distress
CV: Regular rhythm, no murmurs
Resp: Clear to auscultation
Ext: No peripheral edema, normal pedal pulses

ASSESSMENT:
1. Type 2 Diabetes Mellitus - suboptimal control
2. Overweight (BMI 29)
3. Hypertension - borderline controlled

PLAN:
1. Continue metformin 1000mg BD
2. Add gliclazide MR 30mg daily
3. Lifestyle counseling: diet and exercise
4. Check HbA1c, lipids, UEC, ACR
5. Review in 6 weeks
```

### Different Encounter Types

```python
# Emergency visit
emergency_note = generate_health_record(
    patient,
    encounter_type="emergency",
    diagnosis="Chest pain, suspected ACS"
)

# Hospital discharge
discharge_summary = generate_health_record(
    patient,
    encounter_type="discharge",
    diagnosis="NSTEMI",
    admission_date="2024-01-15",
    discharge_date="2024-01-20"
)

# Referral letter
referral = generate_health_record(
    patient,
    encounter_type="referral",
    diagnosis="Chronic kidney disease",
    referral_to="Nephrologist"
)
```

## Generating Cohorts

### Basic Cohort

```python
from synthetic_demographics import create_synthetic_person

# Generate 100 random patients
patients = [create_synthetic_person() for _ in range(100)]

# Save to file
import json
with open("synthetic_patients.json", "w") as f:
    json.dump(patients, f, indent=2, default=str)
```

### Specific Population

```python
# Elderly cohort
elderly = [
    create_synthetic_person(
        age=random.randint(65, 90)
    )
    for _ in range(50)
]

# Gender-balanced cohort
balanced = []
for _ in range(50):
    balanced.append(create_synthetic_person(gender='M'))
    balanced.append(create_synthetic_person(gender='F'))
```

### With Medical Conditions

```python
from SyntheticHealthData import generate_patient

# Generate patient with conditions
patient = generate_patient(
    include_history=True,
    num_conditions=3
)

print("Conditions:", patient['conditions'])
print("Medications:", patient['medications'])
print("Allergies:", patient['allergies'])
```

## Data Formats

### JSON Export

```python
import json

patients = [create_synthetic_person() for _ in range(100)]

with open("patients.json", "w") as f:
    json.dump(patients, f, indent=2, default=str)
```

### CSV Export

```python
import pandas as pd

patients = [create_synthetic_person() for _ in range(100)]
df = pd.DataFrame(patients)
df.to_csv("patients.csv", index=False)
```

### FHIR-like Format

```python
def to_fhir_patient(patient):
    """Convert to FHIR-like structure."""
    return {
        "resourceType": "Patient",
        "name": [{
            "use": "official",
            "family": patient["family_name"],
            "given": [patient["given_name"]]
        }],
        "gender": "male" if patient["gender"] == "M" else "female",
        "birthDate": patient["date_of_birth"],
        "address": [{
            "line": [patient["address"]],
            "city": patient["suburb"],
            "state": patient["state"],
            "postalCode": patient["postcode"]
        }],
        "telecom": [{
            "system": "phone",
            "value": patient["phone"]
        }]
    }
```

## Common Use Cases

### 1. Application Testing

```python
# Generate test data for EMR system
test_patients = []
for i in range(1000):
    patient = create_synthetic_person()
    patient["id"] = f"TEST-{i:04d}"
    test_patients.append(patient)
```

### 2. ML Training Data

```python
# Generate training data with notes
training_data = []
for _ in range(500):
    patient = create_synthetic_person()
    note = generate_health_record(patient, diagnosis="Diabetes")
    training_data.append({
        "demographics": patient,
        "note": note,
        "label": "diabetes_consultation"
    })
```

### 3. Clinical Documentation Examples

```python
# Generate example notes for different scenarios
scenarios = [
    ("consultation", "Hypertension"),
    ("emergency", "Chest pain"),
    ("discharge", "Pneumonia"),
    ("referral", "Suspicious skin lesion")
]

for encounter_type, diagnosis in scenarios:
    patient = create_synthetic_person()
    note = generate_health_record(
        patient,
        encounter_type=encounter_type,
        diagnosis=diagnosis
    )
    print(f"\n{'='*50}")
    print(f"Example: {encounter_type} for {diagnosis}")
    print('='*50)
    print(note)
```

### 4. Teaching Resources

```python
# Generate cases for medical students
def generate_teaching_case():
    patient = create_synthetic_person()
    # Create presenting complaint
    note = generate_health_record(
        patient,
        encounter_type="consultation"
    )
    return {
        "patient": patient,
        "case_note": note,
        "questions": [
            "What is the most likely diagnosis?",
            "What investigations would you order?",
            "What is your management plan?"
        ]
    }
```

## Customization

### Custom Name Lists

```python
# Use custom name data
custom_names = {
    "given_names_m": ["John", "David", "Michael"],
    "given_names_f": ["Sarah", "Emma", "Jessica"],
    "family_names": ["Smith", "Jones", "Brown"]
}

# Modify in synthetic_demographics.py or pass as parameter
```

### Custom Address Data

The generator uses Australian address data by default. For other regions, modify the `seed_data/` files.

### Custom Medical Data

Modify `MedicalData.py` or `seed_data/` to add:
- Custom diagnosis codes
- Additional medications
- Specialty-specific data

## Limitations

### Data Realism
- Data is statistically plausible but not epidemiologically exact
- Medical content is generated by AI and should not be used for clinical training without review
- Some edge cases may produce implausible combinations

### Not For
- Clinical decision support system training without review
- Actual patient care
- Regulatory submissions requiring real data

## Privacy Note

All generated data is **completely synthetic**:
- Names are randomly generated
- Addresses are fictional combinations
- Medicare numbers are randomly generated (not valid)
- No correspondence to real individuals

## Related Features

- [PDF Q&A](pdf-qa.md) - Test with synthetic documents
- [Research Assistant](research.md) - Research synthetic data methods
