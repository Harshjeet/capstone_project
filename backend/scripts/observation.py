import requests

FHIR_BASE_URL = "https://hapi.fhir.org/baseR4"

observations = [
  { "resourceType":"Observation","id":"o001","subject":{"reference":"Patient/p001"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":154,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o002","subject":{"reference":"Patient/p001"},"code":{"text":"Blood Pressure (Diastolic)"},"valueQuantity":{"value":96,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o003","subject":{"reference":"Patient/p001"},"code":{"text":"HbA1c"},"valueQuantity":{"value":7.9,"unit":"%"}},
  { "resourceType":"Observation","id":"o004","subject":{"reference":"Patient/p001"},"code":{"text":"BMI"},"valueQuantity":{"value":31.4,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o005","subject":{"reference":"Patient/p002"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":168,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o006","subject":{"reference":"Patient/p002"},"code":{"text":"Serum Creatinine"},"valueQuantity":{"value":2.4,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o007","subject":{"reference":"Patient/p002"},"code":{"text":"LDL Cholesterol"},"valueQuantity":{"value":182,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o008","subject":{"reference":"Patient/p002"},"code":{"text":"Hemoglobin"},"valueQuantity":{"value":10.1,"unit":"g/dL"}},

  { "resourceType":"Observation","id":"o009","subject":{"reference":"Patient/p003"},"code":{"text":"Oxygen Saturation"},"valueQuantity":{"value":92,"unit":"%"}},
  { "resourceType":"Observation","id":"o010","subject":{"reference":"Patient/p003"},"code":{"text":"Peak Expiratory Flow"},"valueQuantity":{"value":395,"unit":"L/min"}},
  { "resourceType":"Observation","id":"o011","subject":{"reference":"Patient/p003"},"code":{"text":"Respiratory Rate"},"valueQuantity":{"value":23,"unit":"breaths/min"}},
  { "resourceType":"Observation","id":"o012","subject":{"reference":"Patient/p003"},"code":{"text":"Heart Rate"},"valueQuantity":{"value":104,"unit":"bpm"}},

  { "resourceType":"Observation","id":"o013","subject":{"reference":"Patient/p004"},"code":{"text":"TSH"},"valueQuantity":{"value":6.9,"unit":"mIU/L"}},
  { "resourceType":"Observation","id":"o014","subject":{"reference":"Patient/p004"},"code":{"text":"Vitamin D"},"valueQuantity":{"value":14,"unit":"ng/mL"}},
  { "resourceType":"Observation","id":"o015","subject":{"reference":"Patient/p004"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":116,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o016","subject":{"reference":"Patient/p004"},"code":{"text":"BMI"},"valueQuantity":{"value":29.1,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o017","subject":{"reference":"Patient/p005"},"code":{"text":"Total Cholesterol"},"valueQuantity":{"value":248,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o018","subject":{"reference":"Patient/p005"},"code":{"text":"LDL Cholesterol"},"valueQuantity":{"value":176,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o019","subject":{"reference":"Patient/p005"},"code":{"text":"ECG"},"valueString":"ST depression noted"},
  { "resourceType":"Observation","id":"o020","subject":{"reference":"Patient/p005"},"code":{"text":"Heart Rate"},"valueQuantity":{"value":96,"unit":"bpm"}},

  { "resourceType":"Observation","id":"o021","subject":{"reference":"Patient/p006"},"code":{"text":"Hemoglobin"},"valueQuantity":{"value":9.2,"unit":"g/dL"}},
  { "resourceType":"Observation","id":"o022","subject":{"reference":"Patient/p006"},"code":{"text":"Serum Ferritin"},"valueQuantity":{"value":8,"unit":"ng/mL"}},
  { "resourceType":"Observation","id":"o023","subject":{"reference":"Patient/p006"},"code":{"text":"Vitamin B12"},"valueQuantity":{"value":160,"unit":"pg/mL"}},
  { "resourceType":"Observation","id":"o024","subject":{"reference":"Patient/p006"},"code":{"text":"BMI"},"valueQuantity":{"value":22.0,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o025","subject":{"reference":"Patient/p007"},"code":{"text":"Serum Creatinine"},"valueQuantity":{"value":2.7,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o026","subject":{"reference":"Patient/p007"},"code":{"text":"eGFR"},"valueQuantity":{"value":28,"unit":"mL/min"}},
  { "resourceType":"Observation","id":"o027","subject":{"reference":"Patient/p007"},"code":{"text":"Potassium"},"valueQuantity":{"value":5.9,"unit":"mmol/L"}},
  { "resourceType":"Observation","id":"o028","subject":{"reference":"Patient/p007"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":162,"unit":"mmHg"}},

  { "resourceType":"Observation","id":"o029","subject":{"reference":"Patient/p008"},"code":{"text":"Pain Score"},"valueQuantity":{"value":8,"unit":"/10"}},
  { "resourceType":"Observation","id":"o030","subject":{"reference":"Patient/p008"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":138,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o031","subject":{"reference":"Patient/p008"},"code":{"text":"Sleep Duration"},"valueQuantity":{"value":4,"unit":"hours"}},
  { "resourceType":"Observation","id":"o032","subject":{"reference":"Patient/p008"},"code":{"text":"Heart Rate"},"valueQuantity":{"value":92,"unit":"bpm"}},

  { "resourceType":"Observation","id":"o033","subject":{"reference":"Patient/p009"},"code":{"text":"Triglycerides"},"valueQuantity":{"value":286,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o034","subject":{"reference":"Patient/p009"},"code":{"text":"HDL Cholesterol"},"valueQuantity":{"value":32,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o035","subject":{"reference":"Patient/p009"},"code":{"text":"ALT"},"valueQuantity":{"value":82,"unit":"U/L"}},
  { "resourceType":"Observation","id":"o036","subject":{"reference":"Patient/p009"},"code":{"text":"BMI"},"valueQuantity":{"value":30.8,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o037","subject":{"reference":"Patient/p010"},"code":{"text":"Knee X-Ray"},"valueString":"Joint space narrowing"},
  { "resourceType":"Observation","id":"o038","subject":{"reference":"Patient/p010"},"code":{"text":"Vitamin D"},"valueQuantity":{"value":15,"unit":"ng/mL"}},
  { "resourceType":"Observation","id":"o039","subject":{"reference":"Patient/p010"},"code":{"text":"BMI"},"valueQuantity":{"value":30.3,"unit":"kg/m2"}},
  { "resourceType":"Observation","id":"o040","subject":{"reference":"Patient/p010"},"code":{"text":"Pain Score"},"valueQuantity":{"value":6,"unit":"/10"}},

  { "resourceType":"Observation","id":"o041","subject":{"reference":"Patient/p011"},"code":{"text":"Heart Rate"},"valueQuantity":{"value":110,"unit":"bpm"}},
  { "resourceType":"Observation","id":"o042","subject":{"reference":"Patient/p011"},"code":{"text":"Anxiety Score"},"valueQuantity":{"value":8,"unit":"/10"}},
  { "resourceType":"Observation","id":"o043","subject":{"reference":"Patient/p011"},"code":{"text":"Sleep Duration"},"valueQuantity":{"value":5,"unit":"hours"}},
  { "resourceType":"Observation","id":"o044","subject":{"reference":"Patient/p011"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":132,"unit":"mmHg"}},

  { "resourceType":"Observation","id":"o045","subject":{"reference":"Patient/p012"},"code":{"text":"TSH"},"valueQuantity":{"value":7.1,"unit":"mIU/L"}},
  { "resourceType":"Observation","id":"o046","subject":{"reference":"Patient/p012"},"code":{"text":"Vitamin D"},"valueQuantity":{"value":16,"unit":"ng/mL"}},
  { "resourceType":"Observation","id":"o047","subject":{"reference":"Patient/p012"},"code":{"text":"BMI"},"valueQuantity":{"value":29.4,"unit":"kg/m2"}},
  { "resourceType":"Observation","id":"o048","subject":{"reference":"Patient/p012"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":118,"unit":"mg/dL"}},

  { "resourceType":"Observation","id":"o049","subject":{"reference":"Patient/p013"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":148,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o050","subject":{"reference":"Patient/p013"},"code":{"text":"BMI"},"valueQuantity":{"value":31.0,"unit":"kg/m2"}},
  { "resourceType":"Observation","id":"o051","subject":{"reference":"Patient/p013"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":121,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o052","subject":{"reference":"Patient/p013"},"code":{"text":"LDL Cholesterol"},"valueQuantity":{"value":164,"unit":"mg/dL"}},

  { "resourceType":"Observation","id":"o053","subject":{"reference":"Patient/p014"},"code":{"text":"HbA1c"},"valueQuantity":{"value":8.2,"unit":"%"}},
  { "resourceType":"Observation","id":"o054","subject":{"reference":"Patient/p014"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":156,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o055","subject":{"reference":"Patient/p014"},"code":{"text":"LDL Cholesterol"},"valueQuantity":{"value":172,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o056","subject":{"reference":"Patient/p014"},"code":{"text":"BMI"},"valueQuantity":{"value":32.5,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o057","subject":{"reference":"Patient/p015"},"code":{"text":"ALT"},"valueQuantity":{"value":88,"unit":"U/L"}},
  { "resourceType":"Observation","id":"o058","subject":{"reference":"Patient/p015"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":126,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o059","subject":{"reference":"Patient/p015"},"code":{"text":"BMI"},"valueQuantity":{"value":33.1,"unit":"kg/m2"}},
  { "resourceType":"Observation","id":"o060","subject":{"reference":"Patient/p015"},"code":{"text":"Triglycerides"},"valueQuantity":{"value":298,"unit":"mg/dL"}},

  { "resourceType":"Observation","id":"o061","subject":{"reference":"Patient/p016"},"code":{"text":"Fasting Insulin"},"valueQuantity":{"value":28,"unit":"µIU/mL"}},
  { "resourceType":"Observation","id":"o062","subject":{"reference":"Patient/p016"},"code":{"text":"BMI"},"valueQuantity":{"value":34.2,"unit":"kg/m2"}},
  { "resourceType":"Observation","id":"o063","subject":{"reference":"Patient/p016"},"code":{"text":"Testosterone"},"valueQuantity":{"value":78,"unit":"ng/dL"}},
  { "resourceType":"Observation","id":"o064","subject":{"reference":"Patient/p016"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":119,"unit":"mg/dL"}},

  { "resourceType":"Observation","id":"o065","subject":{"reference":"Patient/p017"},"code":{"text":"FEV1"},"valueQuantity":{"value":58,"unit":"% predicted"}},
  { "resourceType":"Observation","id":"o066","subject":{"reference":"Patient/p017"},"code":{"text":"Oxygen Saturation"},"valueQuantity":{"value":90,"unit":"%"}},
  { "resourceType":"Observation","id":"o067","subject":{"reference":"Patient/p017"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":150,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o068","subject":{"reference":"Patient/p017"},"code":{"text":"Respiratory Rate"},"valueQuantity":{"value":24,"unit":"breaths/min"}},

  { "resourceType":"Observation","id":"o069","subject":{"reference":"Patient/p018"},"code":{"text":"Depression Score"},"valueQuantity":{"value":9,"unit":"/10"}},
  { "resourceType":"Observation","id":"o070","subject":{"reference":"Patient/p018"},"code":{"text":"Sleep Duration"},"valueQuantity":{"value":4,"unit":"hours"}},
  { "resourceType":"Observation","id":"o071","subject":{"reference":"Patient/p018"},"code":{"text":"Heart Rate"},"valueQuantity":{"value":98,"unit":"bpm"}},
  { "resourceType":"Observation","id":"o072","subject":{"reference":"Patient/p018"},"code":{"text":"BMI"},"valueQuantity":{"value":27.8,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o073","subject":{"reference":"Patient/p019"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":158,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o074","subject":{"reference":"Patient/p019"},"code":{"text":"LDL Cholesterol"},"valueQuantity":{"value":168,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o075","subject":{"reference":"Patient/p019"},"code":{"text":"BMI"},"valueQuantity":{"value":31.7,"unit":"kg/m2"}},
  { "resourceType":"Observation","id":"o076","subject":{"reference":"Patient/p019"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":124,"unit":"mg/dL"}},

  { "resourceType":"Observation","id":"o077","subject":{"reference":"Patient/p020"},"code":{"text":"TSH"},"valueQuantity":{"value":8.0,"unit":"mIU/L"}},
  { "resourceType":"Observation","id":"o078","subject":{"reference":"Patient/p020"},"code":{"text":"Vitamin D"},"valueQuantity":{"value":13,"unit":"ng/mL"}},
  { "resourceType":"Observation","id":"o079","subject":{"reference":"Patient/p020"},"code":{"text":"BMI"},"valueQuantity":{"value":28.9,"unit":"kg/m2"}},
  { "resourceType":"Observation","id":"o080","subject":{"reference":"Patient/p020"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":117,"unit":"mg/dL"}},

  { "resourceType":"Observation","id":"o081","subject":{"reference":"Patient/p021"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":146,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o082","subject":{"reference":"Patient/p021"},"code":{"text":"LDL Cholesterol"},"valueQuantity":{"value":158,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o083","subject":{"reference":"Patient/p021"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":122,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o084","subject":{"reference":"Patient/p021"},"code":{"text":"BMI"},"valueQuantity":{"value":30.6,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o085","subject":{"reference":"Patient/p022"},"code":{"text":"ESR"},"valueQuantity":{"value":48,"unit":"mm/hr"}},
  { "resourceType":"Observation","id":"o086","subject":{"reference":"Patient/p022"},"code":{"text":"CRP"},"valueQuantity":{"value":12,"unit":"mg/L"}},
  { "resourceType":"Observation","id":"o087","subject":{"reference":"Patient/p022"},"code":{"text":"Vitamin D"},"valueQuantity":{"value":17,"unit":"ng/mL"}},
  { "resourceType":"Observation","id":"o088","subject":{"reference":"Patient/p022"},"code":{"text":"Pain Score"},"valueQuantity":{"value":7,"unit":"/10"}},

  { "resourceType":"Observation","id":"o089","subject":{"reference":"Patient/p023"},"code":{"text":"Uric Acid"},"valueQuantity":{"value":9.1,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o090","subject":{"reference":"Patient/p023"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":150,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o091","subject":{"reference":"Patient/p023"},"code":{"text":"Creatinine"},"valueQuantity":{"value":1.6,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o092","subject":{"reference":"Patient/p023"},"code":{"text":"BMI"},"valueQuantity":{"value":29.9,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o093","subject":{"reference":"Patient/p024"},"code":{"text":"Oxygen Saturation"},"valueQuantity":{"value":95,"unit":"%"}},
  { "resourceType":"Observation","id":"o094","subject":{"reference":"Patient/p024"},"code":{"text":"Peak Expiratory Flow"},"valueQuantity":{"value":420,"unit":"L/min"}},
  { "resourceType":"Observation","id":"o095","subject":{"reference":"Patient/p024"},"code":{"text":"Eosinophils"},"valueQuantity":{"value":620,"unit":"cells/µL"}},
  { "resourceType":"Observation","id":"o096","subject":{"reference":"Patient/p024"},"code":{"text":"BMI"},"valueQuantity":{"value":24.1,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o097","subject":{"reference":"Patient/p025"},"code":{"text":"MMSE Score"},"valueQuantity":{"value":18,"unit":"/30"}},
  { "resourceType":"Observation","id":"o098","subject":{"reference":"Patient/p025"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":142,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o099","subject":{"reference":"Patient/p025"},"code":{"text":"Vitamin D"},"valueQuantity":{"value":19,"unit":"ng/mL"}},
  { "resourceType":"Observation","id":"o100","subject":{"reference":"Patient/p025"},"code":{"text":"BMI"},"valueQuantity":{"value":26.8,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o101","subject":{"reference":"Patient/p026"},"code":{"text":"Vitamin B12"},"valueQuantity":{"value":148,"unit":"pg/mL"}},
  { "resourceType":"Observation","id":"o102","subject":{"reference":"Patient/p026"},"code":{"text":"Hemoglobin"},"valueQuantity":{"value":10.4,"unit":"g/dL"}},
  { "resourceType":"Observation","id":"o103","subject":{"reference":"Patient/p026"},"code":{"text":"MCV"},"valueQuantity":{"value":72,"unit":"fL"}},
  { "resourceType":"Observation","id":"o104","subject":{"reference":"Patient/p026"},"code":{"text":"BMI"},"valueQuantity":{"value":23.4,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o105","subject":{"reference":"Patient/p027"},"code":{"text":"Apnea Hypopnea Index"},"valueQuantity":{"value":22,"unit":"events/hr"}},
  { "resourceType":"Observation","id":"o106","subject":{"reference":"Patient/p027"},"code":{"text":"BMI"},"valueQuantity":{"value":34.8,"unit":"kg/m2"}},
  { "resourceType":"Observation","id":"o107","subject":{"reference":"Patient/p027"},"code":{"text":"Fasting Blood Glucose"},"valueQuantity":{"value":128,"unit":"mg/dL"}},
  { "resourceType":"Observation","id":"o108","subject":{"reference":"Patient/p027"},"code":{"text":"Triglycerides"},"valueQuantity":{"value":305,"unit":"mg/dL"}},

  { "resourceType":"Observation","id":"o109","subject":{"reference":"Patient/p028"},"code":{"text":"Blood Pressure (Systolic)"},"valueQuantity":{"value":148,"unit":"mmHg"}},
  { "resourceType":"Observation","id":"o110","subject":{"reference":"Patient/p028"},"code":{"text":"Anxiety Score"},"valueQuantity":{"value":7,"unit":"/10"}},
  { "resourceType":"Observation","id":"o111","subject":{"reference":"Patient/p028"},"code":{"text":"Migraine Frequency"},"valueQuantity":{"value":5,"unit":"days/month"}},
  { "resourceType":"Observation","id":"o112","subject":{"reference":"Patient/p028"},"code":{"text":"BMI"},"valueQuantity":{"value":29.7,"unit":"kg/m2"}},

  { "resourceType":"Observation","id":"o113","subject":{"reference":"Patient/p029"},"code":{"text":"ALT"},"valueQuantity":{"value":94,"unit":"U/L"}},
  { "resourceType":"Observation","id":"o114","subject":{"reference":"Patient/p029"},"code":{"text":"AST"},"valueQuantity":{"value":88,"unit":"U/L"}},
  { "resourceType":"Observation","id":"o115","subject":{"reference":"Patient/p029"},"code":{"text":"Albumin"},"valueQuantity":{"value":2.9,"unit":"g/dL"}},
  { "resourceType":"Observation","id":"o116","subject":{"reference":"Patient/p029"},"code":{"text":"INR"},"valueQuantity":{"value":1.6,"unit":"ratio"}},

  { "resourceType":"Observation","id":"o117","subject":{"reference":"Patient/p030"},"code":{"text":"Vitamin B12"},"valueQuantity":{"value":132,"unit":"pg/mL"}},
  { "resourceType":"Observation","id":"o118","subject":{"reference":"Patient/p030"},"code":{"text":"Nerve Conduction Velocity"},"valueQuantity":{"value":34,"unit":"m/s"}},
  { "resourceType":"Observation","id":"o119","subject":{"reference":"Patient/p030"},"code":{"text":"Hemoglobin"},"valueQuantity":{"value":11.2,"unit":"g/dL"}},
  { "resourceType":"Observation","id":"o120","subject":{"reference":"Patient/p030"},"code":{"text":"BMI"},"valueQuantity":{"value":25.1,"unit":"kg/m2"}}
]

headers = {
    "Content-Type": "application/fhir+json"
}

success = 0
failure = 0

for obs in observations:
    obs_id = obs["id"]
    url = f"{FHIR_BASE_URL}/Observation/{obs_id}"

    response = requests.put(url, headers=headers, json=obs)

    if response.status_code in (200, 201):
        print(f"✅ Uploaded Observation {obs_id}")
        success += 1
    else:
        print(f"❌ Failed Observation {obs_id}")
        print(response.status_code, response.text)
        failure += 1

print("\n===== SUMMARY =====")
print(f"✅ Success: {success}")
print(f"❌ Failed: {failure}")
