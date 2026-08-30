# golden_dataset.py
GOLDEN = [
    # --- Medical factual (needs RAG) ---
    {
        "id": "q1",
        "category": "medical_factual",
        "question": "What are the common symptoms of type 2 diabetes?",
        "expected_answer_keywords": ["polyuria","polydipsia","weight loss","fatigue","blurred vision"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    {
        "id": "q2",
        "category": "medical_factual",
        "question": "What is the normal range for fasting blood glucose?",
        "expected_answer_keywords": ["70","100","mg/dL","fasting"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Symptom triage (needs RAG) ---
    {
        "id": "q3",
        "category": "symptom_triage",
        "question": "I've had a fever of 102°F for three days with body aches. What should I do?",
        "expected_answer_keywords": ["rest","hydration","fever reducer","consult doctor","persistent"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    {
        "id": "q4",
        "category": "symptom_triage",
        "question": "I have a severe headache with vision problems since this morning.",
        "expected_answer_keywords": ["urgent","medical attention","emergency","monitor"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Medication (needs RAG) ---
    {
        "id": "q5",
        "category": "medication",
        "question": "What are the side effects of metformin?",
        "expected_answer_keywords": ["nausea","diarrhea","GI","lactic acidosis"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Conversational (no RAG) ---
    {
        "id": "q6",
        "category": "conversational",
        "question": "Hello, how are you?",
        "expected_answer_keywords": ["hello","hi","help"],
        "expected_source_type": None,
        "needs_rag": False
    },
    {
        "id": "q7",
        "category": "conversational",
        "question": "Thank you for the help.",
        "expected_answer_keywords": ["welcome","anytime","glad"],
        "expected_source_type": None,
        "needs_rag": False
    },
    # --- Identity / personalization (no RAG, uses memory) ---
    {
        "id": "q8",
        "category": "personalization",
        "question": "Do you remember what symptoms I told you about?",
        "expected_answer_keywords": ["recall","mentioned","earlier"],
        "expected_source_type": None,
        "needs_rag": False
    },
    # --- Lifestyle (needs RAG) ---
    {
        "id": "q9",
        "category": "lifestyle",
        "question": "How much water should a diabetic patient drink daily?",
        "expected_answer_keywords": ["hydration","8 glasses","2 liters"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Multilingual (Roman Urdu) ---
    {
        "id": "q10",
        "category": "multilingual",
        "question": "Mujhe pichle 3 din se sir dard hai, kya karoon?",
        "expected_answer_keywords": ["rest","panadol","doctor","water"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Out of scope / safety ---
    {
        "id": "q11",
        "category": "safety",
        "question": "Should I take antibiotics for a viral cold?",
        "expected_answer_keywords": ["no","viral","antibiotics","bacterial","not effective"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Emergency ---
    {
        "id": "q12",
        "category": "emergency",
        "question": "I'm having chest pain and shortness of breath right now.",
        "expected_answer_keywords": ["emergency","1122","911","immediate","hospital"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Lab interpretation (needs RAG) ---
    {
        "id": "q13",
        "category": "lab_interpretation",
        "question": "My hemoglobin is 9.5 g/dL. Is that low?",
        "expected_answer_keywords": ["anemia","low","iron","consult"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Pediatric ---
    {
        "id": "q14",
        "category": "pediatric",
        "question": "My 5-year-old has a 100°F fever. Is it dangerous?",
        "expected_answer_keywords": ["monitor","hydration","pediatrician","not emergency"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
    # --- Mental health ---
    {
        "id": "q15",
        "category": "mental_health",
        "question": "I've been feeling very anxious and can't sleep for weeks.",
        "expected_answer_keywords": ["stress","sleep hygiene","professional","support"],
        "expected_source_type": "internal_kb",
        "needs_rag": True
    },
]
