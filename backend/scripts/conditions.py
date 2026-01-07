import requests

FHIR_BASE_URL = "https://hapi.fhir.org/baseR4"

conditions = [

  { "resourceType":"Condition","id":"c001","subject":{"reference":"Patient/p001"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c002","subject":{"reference":"Patient/p001"},"code":{"text":"Type 2 Diabetes Mellitus"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c003","subject":{"reference":"Patient/p001"},"code":{"text":"Hyperlipidemia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c004","subject":{"reference":"Patient/p001"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c005","subject":{"reference":"Patient/p001"},"code":{"text":"Fatty Liver Disease"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c006","subject":{"reference":"Patient/p002"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c007","subject":{"reference":"Patient/p002"},"code":{"text":"Coronary Artery Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c008","subject":{"reference":"Patient/p002"},"code":{"text":"Chronic Kidney Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c009","subject":{"reference":"Patient/p002"},"code":{"text":"Hyperlipidemia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c010","subject":{"reference":"Patient/p002"},"code":{"text":"Anemia"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c011","subject":{"reference":"Patient/p003"},"code":{"text":"Asthma"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c012","subject":{"reference":"Patient/p003"},"code":{"text":"Allergic Rhinitis"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c013","subject":{"reference":"Patient/p003"},"code":{"text":"Anxiety Disorder"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c014","subject":{"reference":"Patient/p004"},"code":{"text":"Hypothyroidism"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c015","subject":{"reference":"Patient/p004"},"code":{"text":"Vitamin D Deficiency"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c016","subject":{"reference":"Patient/p004"},"code":{"text":"Prediabetes"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c017","subject":{"reference":"Patient/p004"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c018","subject":{"reference":"Patient/p005"},"code":{"text":"Coronary Artery Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c019","subject":{"reference":"Patient/p005"},"code":{"text":"Heart Failure"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c020","subject":{"reference":"Patient/p005"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c021","subject":{"reference":"Patient/p005"},"code":{"text":"Chronic Kidney Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c022","subject":{"reference":"Patient/p005"},"code":{"text":"Hyperlipidemia"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c023","subject":{"reference":"Patient/p006"},"code":{"text":"Iron Deficiency Anemia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c024","subject":{"reference":"Patient/p006"},"code":{"text":"Menorrhagia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c025","subject":{"reference":"Patient/p006"},"code":{"text":"Vitamin B12 Deficiency"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c026","subject":{"reference":"Patient/p007"},"code":{"text":"Chronic Kidney Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c027","subject":{"reference":"Patient/p007"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c028","subject":{"reference":"Patient/p007"},"code":{"text":"Hyperkalemia"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c029","subject":{"reference":"Patient/p008"},"code":{"text":"Migraine"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c030","subject":{"reference":"Patient/p008"},"code":{"text":"Anxiety Disorder"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c031","subject":{"reference":"Patient/p008"},"code":{"text":"Insomnia"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c032","subject":{"reference":"Patient/p009"},"code":{"text":"Hyperlipidemia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c033","subject":{"reference":"Patient/p009"},"code":{"text":"Fatty Liver Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c034","subject":{"reference":"Patient/p009"},"code":{"text":"Prediabetes"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c035","subject":{"reference":"Patient/p010"},"code":{"text":"Osteoarthritis"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c036","subject":{"reference":"Patient/p010"},"code":{"text":"Vitamin D Deficiency"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c037","subject":{"reference":"Patient/p010"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c038","subject":{"reference":"Patient/p011"},"code":{"text":"Anxiety Disorder"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c039","subject":{"reference":"Patient/p011"},"code":{"text":"Insomnia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c040","subject":{"reference":"Patient/p011"},"code":{"text":"Migraine"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c041","subject":{"reference":"Patient/p012"},"code":{"text":"Hypothyroidism"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c042","subject":{"reference":"Patient/p012"},"code":{"text":"Vitamin D Deficiency"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c043","subject":{"reference":"Patient/p012"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c044","subject":{"reference":"Patient/p013"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c045","subject":{"reference":"Patient/p013"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c046","subject":{"reference":"Patient/p013"},"code":{"text":"Prediabetes"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c047","subject":{"reference":"Patient/p014"},"code":{"text":"Type 2 Diabetes Mellitus"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c048","subject":{"reference":"Patient/p014"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c049","subject":{"reference":"Patient/p014"},"code":{"text":"Hyperlipidemia"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c050","subject":{"reference":"Patient/p015"},"code":{"text":"Fatty Liver Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c051","subject":{"reference":"Patient/p015"},"code":{"text":"Prediabetes"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c052","subject":{"reference":"Patient/p015"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c053","subject":{"reference":"Patient/p016"},"code":{"text":"PCOS"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c054","subject":{"reference":"Patient/p016"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c055","subject":{"reference":"Patient/p016"},"code":{"text":"Insulin Resistance"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c056","subject":{"reference":"Patient/p017"},"code":{"text":"COPD"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c057","subject":{"reference":"Patient/p017"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c058","subject":{"reference":"Patient/p017"},"code":{"text":"Chronic Bronchitis"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c059","subject":{"reference":"Patient/p018"},"code":{"text":"Depression"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c060","subject":{"reference":"Patient/p018"},"code":{"text":"Anxiety Disorder"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c061","subject":{"reference":"Patient/p018"},"code":{"text":"Insomnia"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c062","subject":{"reference":"Patient/p019"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c063","subject":{"reference":"Patient/p019"},"code":{"text":"Hyperlipidemia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c064","subject":{"reference":"Patient/p019"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c065","subject":{"reference":"Patient/p020"},"code":{"text":"Hypothyroidism"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c066","subject":{"reference":"Patient/p020"},"code":{"text":"Goiter"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c067","subject":{"reference":"Patient/p020"},"code":{"text":"Vitamin D Deficiency"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c068","subject":{"reference":"Patient/p021"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c069","subject":{"reference":"Patient/p021"},"code":{"text":"Hyperlipidemia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c070","subject":{"reference":"Patient/p021"},"code":{"text":"Prediabetes"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c071","subject":{"reference":"Patient/p022"},"code":{"text":"Rheumatoid Arthritis"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c072","subject":{"reference":"Patient/p022"},"code":{"text":"Osteopenia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c073","subject":{"reference":"Patient/p022"},"code":{"text":"Vitamin D Deficiency"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c074","subject":{"reference":"Patient/p023"},"code":{"text":"Gout"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c075","subject":{"reference":"Patient/p023"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c076","subject":{"reference":"Patient/p023"},"code":{"text":"Hyperuricemia"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c077","subject":{"reference":"Patient/p024"},"code":{"text":"Allergic Rhinitis"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c078","subject":{"reference":"Patient/p024"},"code":{"text":"Mild Asthma"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c079","subject":{"reference":"Patient/p024"},"code":{"text":"Eczema"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c080","subject":{"reference":"Patient/p025"},"code":{"text":"Alzheimer’s Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c081","subject":{"reference":"Patient/p025"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c082","subject":{"reference":"Patient/p025"},"code":{"text":"Osteoporosis"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c083","subject":{"reference":"Patient/p026"},"code":{"text":"Vitamin B12 Deficiency"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c084","subject":{"reference":"Patient/p026"},"code":{"text":"Anemia"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c085","subject":{"reference":"Patient/p026"},"code":{"text":"Fatigue"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c086","subject":{"reference":"Patient/p027"},"code":{"text":"Obesity"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c087","subject":{"reference":"Patient/p027"},"code":{"text":"Prediabetes"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c088","subject":{"reference":"Patient/p027"},"code":{"text":"Sleep Apnea"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c089","subject":{"reference":"Patient/p028"},"code":{"text":"Hypertension"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c090","subject":{"reference":"Patient/p028"},"code":{"text":"Anxiety Disorder"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c091","subject":{"reference":"Patient/p028"},"code":{"text":"Migraine"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c092","subject":{"reference":"Patient/p029"},"code":{"text":"Chronic Liver Disease"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c093","subject":{"reference":"Patient/p029"},"code":{"text":"Alcohol Use Disorder"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c094","subject":{"reference":"Patient/p029"},"code":{"text":"Malnutrition"},"clinicalStatus":{"text":"Active"}},

  { "resourceType":"Condition","id":"c095","subject":{"reference":"Patient/p030"},"code":{"text":"Vitamin B12 Deficiency"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c096","subject":{"reference":"Patient/p030"},"code":{"text":"Peripheral Neuropathy"},"clinicalStatus":{"text":"Active"}},
  { "resourceType":"Condition","id":"c097","subject":{"reference":"Patient/p030"},"code":{"text":"Chronic Fatigue Syndrome"},"clinicalStatus":{"text":"Active"}}

]

headers = {
    "Content-Type": "application/fhir+json"
}

success = 0
failure = 0

for condition in conditions:
    condition_id = condition["id"]
    url = f"{FHIR_BASE_URL}/Condition/{condition_id}"

    response = requests.put(url, headers=headers, json=condition)

    if response.status_code in (200, 201):
        print(f"✅ Uploaded Condition {condition_id}")
        success += 1
    else:
        print(f"❌ Failed Condition {condition_id}")
        print(response.status_code, response.text)
        failure += 1

print("\n===== SUMMARY =====")
print(f"✅ Success: {success}")
print(f"❌ Failed: {failure}")
