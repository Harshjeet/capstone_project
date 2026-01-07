import requests
import json

FHIR_BASE_URL = "https://hapi.fhir.org/baseR4"

patients = [
  { "resourceType": "Patient", "id": "p001", "name": [{ "given": ["Rahul"], "family": "Sharma" }], "gender": "male", "birthDate": "1980-05-12" },
  { "resourceType": "Patient", "id": "p002", "name": [{ "given": ["Anita"], "family": "Verma" }], "gender": "female", "birthDate": "1975-09-20" },
  { "resourceType": "Patient", "id": "p003", "name": [{ "given": ["Amit"], "family": "Singh" }], "gender": "male", "birthDate": "1990-02-10" },
  { "resourceType": "Patient", "id": "p004", "name": [{ "given": ["Neha"], "family": "Patel" }], "gender": "female", "birthDate": "1988-11-03" },
  { "resourceType": "Patient", "id": "p005", "name": [{ "given": ["Suresh"], "family": "Iyer" }], "gender": "male", "birthDate": "1965-07-18" },
  { "resourceType": "Patient", "id": "p006", "name": [{ "given": ["Pooja"], "family": "Mehta" }], "gender": "female", "birthDate": "1992-01-14" },
  { "resourceType": "Patient", "id": "p007", "name": [{ "given": ["Rakesh"], "family": "Kumar" }], "gender": "male", "birthDate": "1972-03-09" },
  { "resourceType": "Patient", "id": "p008", "name": [{ "given": ["Kavita"], "family": "Joshi" }], "gender": "female", "birthDate": "1985-06-22" },
  { "resourceType": "Patient", "id": "p009", "name": [{ "given": ["Manoj"], "family": "Gupta" }], "gender": "male", "birthDate": "1968-12-01" },
  { "resourceType": "Patient", "id": "p010", "name": [{ "given": ["Sunita"], "family": "Rao" }], "gender": "female", "birthDate": "1979-08-17" },

  { "resourceType": "Patient", "id": "p011", "name": [{ "given": ["Arjun"], "family": "Malhotra" }], "gender": "male", "birthDate": "1995-04-02" },
  { "resourceType": "Patient", "id": "p012", "name": [{ "given": ["Divya"], "family": "Nair" }], "gender": "female", "birthDate": "1983-10-10" },
  { "resourceType": "Patient", "id": "p013", "name": [{ "given": ["Vikas"], "family": "Bansal" }], "gender": "male", "birthDate": "1977-01-30" },
  { "resourceType": "Patient", "id": "p014", "name": [{ "given": ["Meena"], "family": "Chopra" }], "gender": "female", "birthDate": "1969-09-25" },
  { "resourceType": "Patient", "id": "p015", "name": [{ "given": ["Deepak"], "family": "Agarwal" }], "gender": "male", "birthDate": "1982-07-05" },

  { "resourceType": "Patient", "id": "p016", "name": [{ "given": ["Ritu"], "family": "Kapoor" }], "gender": "female", "birthDate": "1991-12-12" },
  { "resourceType": "Patient", "id": "p017", "name": [{ "given": ["Sanjay"], "family": "Mishra" }], "gender": "male", "birthDate": "1963-05-28" },
  { "resourceType": "Patient", "id": "p018", "name": [{ "given": ["Alka"], "family": "Pandey" }], "gender": "female", "birthDate": "1987-03-15" },
  { "resourceType": "Patient", "id": "p019", "name": [{ "given": ["Nitin"], "family": "Srivastava" }], "gender": "male", "birthDate": "1974-11-08" },
  { "resourceType": "Patient", "id": "p020", "name": [{ "given": ["Shweta"], "family": "Kulkarni" }], "gender": "female", "birthDate": "1993-02-21" },

  { "resourceType": "Patient", "id": "p021", "name": [{ "given": ["Rajesh"], "family": "Yadav" }], "gender": "male", "birthDate": "1967-06-19" },
  { "resourceType": "Patient", "id": "p022", "name": [{ "given": ["Monika"], "family": "Saxena" }], "gender": "female", "birthDate": "1984-09-14" },
  { "resourceType": "Patient", "id": "p023", "name": [{ "given": ["Pradeep"], "family": "Jain" }], "gender": "male", "birthDate": "1971-01-11" },
  { "resourceType": "Patient", "id": "p024", "name": [{ "given": ["Sneha"], "family": "Bose" }], "gender": "female", "birthDate": "1996-04-06" },
  { "resourceType": "Patient", "id": "p025", "name": [{ "given": ["Ashok"], "family": "Chatterjee" }], "gender": "male", "birthDate": "1959-10-29" },

  { "resourceType": "Patient", "id": "p026", "name": [{ "given": ["Payal"], "family": "Arora" }], "gender": "female", "birthDate": "1989-08-08" },
  { "resourceType": "Patient", "id": "p027", "name": [{ "given": ["Kunal"], "family": "Khanna" }], "gender": "male", "birthDate": "1994-06-02" },
  { "resourceType": "Patient", "id": "p028", "name": [{ "given": ["Bhavna"], "family": "Tiwari" }], "gender": "female", "birthDate": "1978-12-19" },
  { "resourceType": "Patient", "id": "p029", "name": [{ "given": ["Harish"], "family": "Menon" }], "gender": "male", "birthDate": "1966-03-27" },
  { "resourceType": "Patient", "id": "p030", "name": [{ "given": ["Nisha"], "family": "Goyal" }], "gender": "female", "birthDate": "1990-07-31" }
]

headers = {
    "Content-Type": "application/fhir+json"
}

for patient in patients:
    patient_id = patient["id"]
    url = f"{FHIR_BASE_URL}/Patient/{patient_id}"

    response = requests.put(url, headers=headers, json=patient)

    if response.status_code in [200, 201]:
        print(f" Uploaded Patient {patient_id}")
    else:
        print(f" Failed for {patient_id}: {response.status_code}")
        print(response.text)
