TEST_CASES = [

# ======================================================
# IN-DISTRIBUTION (30)
# Reference answers are short, general medical-knowledge
# summaries — written to match the style/granularity of
# your disease_db + MedQA + PubMed knowledge base, so
# ROUGE/BERTScore comparisons are meaningful.
# ======================================================

{
    "query": "What are the symptoms of vitamin D deficiency?",
    "reference": "Common symptoms include fatigue, bone pain, muscle weakness, mood changes, and increased risk of fractures.",
    "category": "in_distribution",
},
{
    "query": "What are the common symptoms of diabetes mellitus?",
    "reference": "Common symptoms include frequent urination, excessive thirst, unexplained weight loss, fatigue, and blurred vision.",
    "category": "in_distribution",
},
{
    "query": "What causes hypertension?",
    "reference": "Hypertension is caused by factors such as excess salt intake, obesity, physical inactivity, chronic stress, genetics, and kidney disease.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of anemia?",
    "reference": "Symptoms include fatigue, pale skin, shortness of breath, dizziness, cold hands and feet, and irregular heartbeat.",
    "category": "in_distribution",
},
{
    "query": "What are the warning signs of a heart attack?",
    "reference": "Warning signs include chest pain or pressure, pain radiating to the arm or jaw, shortness of breath, cold sweat, and nausea.",
    "category": "in_distribution",
},
{
    "query": "How is asthma diagnosed?",
    "reference": "Asthma is diagnosed through medical history, physical examination, spirometry to measure lung function, and peak flow measurement.",
    "category": "in_distribution",
},
{
    "query": "What foods should diabetic patients avoid?",
    "reference": "Diabetic patients should limit sugary drinks, refined carbohydrates, white bread, processed snacks, and foods high in saturated fat.",
    "category": "in_distribution",
},
{
    "query": "What is hypothyroidism?",
    "reference": "Hypothyroidism is a condition where the thyroid gland does not produce enough thyroid hormone, causing fatigue, weight gain, and cold intolerance.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of dengue fever?",
    "reference": "Symptoms include high fever, severe headache, joint and muscle pain, rash, and pain behind the eyes.",
    "category": "in_distribution",
},
{
    "query": "How can dehydration be treated?",
    "reference": "Dehydration is treated with oral rehydration solutions, increased fluid intake, and in severe cases, intravenous fluids.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of pneumonia?",
    "reference": "Symptoms include cough with phlegm, fever, chills, difficulty breathing, and chest pain when breathing or coughing.",
    "category": "in_distribution",
},
{
    "query": "What is chronic kidney disease?",
    "reference": "Chronic kidney disease is the gradual loss of kidney function over time, often caused by diabetes and hypertension.",
    "category": "in_distribution",
},
{
    "query": "How is tuberculosis diagnosed?",
    "reference": "Tuberculosis is diagnosed using sputum smear microscopy, chest X-ray, tuberculin skin test, and molecular tests like GeneXpert.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of migraine?",
    "reference": "Symptoms include throbbing headache, sensitivity to light and sound, nausea, and sometimes visual disturbances called aura.",
    "category": "in_distribution",
},
{
    "query": "What are common causes of chest pain?",
    "reference": "Common causes include heart disease, acid reflux, muscle strain, anxiety, and lung conditions such as pneumonia.",
    "category": "in_distribution",
},
{
    "query": "How can obesity be managed?",
    "reference": "Obesity is managed through a balanced diet, regular physical activity, behavioral changes, and in some cases, medication or surgery.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of urinary tract infection?",
    "reference": "Symptoms include a burning sensation during urination, frequent urge to urinate, cloudy urine, and lower abdominal pain.",
    "category": "in_distribution",
},
{
    "query": "What is gastroesophageal reflux disease (GERD)?",
    "reference": "GERD is a digestive disorder where stomach acid frequently flows back into the esophagus, causing heartburn and regurgitation.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of appendicitis?",
    "reference": "Symptoms include sudden pain near the navel that shifts to the lower right abdomen, nausea, vomiting, and fever.",
    "category": "in_distribution",
},
{
    "query": "How is high cholesterol treated?",
    "reference": "High cholesterol is treated with dietary changes, regular exercise, weight management, and medications such as statins.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of influenza?",
    "reference": "Symptoms include fever, chills, muscle aches, cough, sore throat, fatigue, and headache.",
    "category": "in_distribution",
},
{
    "query": "What are the complications of untreated diabetes?",
    "reference": "Complications include nerve damage, kidney disease, vision loss, cardiovascular disease, and poor wound healing.",
    "category": "in_distribution",
},
{
    "query": "What is osteoporosis?",
    "reference": "Osteoporosis is a condition where bones become weak and brittle due to loss of bone density, increasing fracture risk.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of liver cirrhosis?",
    "reference": "Symptoms include fatigue, jaundice, easy bruising, swelling in the legs and abdomen, and confusion in advanced stages.",
    "category": "in_distribution",
},
{
    "query": "How can iron deficiency be prevented?",
    "reference": "Iron deficiency can be prevented by eating iron-rich foods such as red meat, leafy greens, and legumes, along with vitamin C to aid absorption.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of COVID-19?",
    "reference": "Symptoms include fever, cough, fatigue, loss of taste or smell, sore throat, and difficulty breathing in severe cases.",
    "category": "in_distribution",
},
{
    "query": "How is malaria diagnosed?",
    "reference": "Malaria is diagnosed through blood smear microscopy, rapid diagnostic tests, and PCR testing to detect parasite presence.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of epilepsy?",
    "reference": "Symptoms include recurrent seizures, temporary confusion, staring spells, and uncontrollable jerking movements.",
    "category": "in_distribution",
},
{
    "query": "What causes peptic ulcers?",
    "reference": "Peptic ulcers are commonly caused by Helicobacter pylori infection and long-term use of NSAIDs such as ibuprofen or aspirin.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of anxiety disorder?",
    "reference": "Symptoms include excessive worry, restlessness, rapid heartbeat, difficulty concentrating, and sleep disturbances.",
    "category": "in_distribution",
},

# ======================================================
# OUT-OF-DISTRIBUTION (12)
# No reference answer — these test whether the correction
# step (web fallback) kicks in and whether grounding holds
# up, not ROUGE/BERTScore. Scored separately (see
# eval/hallucination_check.py).
# ======================================================

{
    "query": "What is the latest WHO guidance on mpox vaccination?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest treatments for Alzheimer's disease approved this year?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest CDC recommendations for RSV vaccination?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest updates in long COVID treatment?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest WHO recommendations for avian influenza?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest hypertension treatment guidelines?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest recommendations for childhood obesity management?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest breast cancer screening recommendations?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest diabetes medications introduced recently?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest recommendations for HPV vaccination?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest migraine treatments available?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest WHO recommendations on antimicrobial resistance?",
    "reference": None,
    "category": "out_of_distribution",
},

# ======================================================
# AMBIGUOUS (8)
# Vague, symptom-only phrasing a real patient would type.
# References describe the *appropriate response pattern*
# (acknowledge + ask clarifying info / advise seeking care)
# rather than a diagnosis, since a single-line query alone
# isn't enough to diagnose anything. This keeps reference
# answers medically responsible.
# ======================================================

{
    "query": "I have a headache. What should I do?",
    "reference": "Rest, stay hydrated, and consider over-the-counter pain relief; seek medical attention if the headache is severe, sudden, or accompanied by other symptoms.",
    "category": "ambiguous",
},
{
    "query": "Why do I feel tired all the time?",
    "reference": "Persistent fatigue can result from poor sleep, stress, anemia, thyroid issues, or an underlying medical condition; a doctor can help identify the cause.",
    "category": "ambiguous",
},
{
    "query": "My stomach hurts after eating.",
    "reference": "Pain after eating can be caused by indigestion, acid reflux, food intolerance, or gastritis; persistent or severe pain should be evaluated by a doctor.",
    "category": "ambiguous",
},
{
    "query": "I have chest pain.",
    "reference": "Chest pain can have many causes ranging from muscle strain to heart-related issues; sudden or severe chest pain requires immediate medical attention.",
    "category": "ambiguous",
},
{
    "query": "I feel dizzy.",
    "reference": "Dizziness can be caused by dehydration, low blood pressure, inner ear issues, or low blood sugar; frequent or severe dizziness should be checked by a doctor.",
    "category": "ambiguous",
},
{
    "query": "My child has a fever.",
    "reference": "Monitor the child's temperature, ensure hydration, and use age-appropriate fever-reducing medication; seek medical care if fever is high, persistent, or accompanied by other symptoms.",
    "category": "ambiguous",
},
{
    "query": "I keep coughing.",
    "reference": "Persistent cough can be caused by infections, allergies, asthma, or acid reflux; a cough lasting more than a few weeks should be evaluated by a doctor.",
    "category": "ambiguous",
},
{
    "query": "My blood pressure is high.",
    "reference": "High blood pressure should be monitored regularly and managed through diet, exercise, and medication as prescribed; consistently high readings warrant medical evaluation.",
    "category": "ambiguous",
},

]