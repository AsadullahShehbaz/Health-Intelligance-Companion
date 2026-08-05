# 🎉 Week 1 Perfect! Now Week 2 Begins.

First let me analyze your Week 1 output before planning Week 2.

---

## ✅ Week 1 Health Check

```
Total raw collected:     324,409  ✅ Excellent
Total after conversion:  338,613  ✅ (iCliniq tripled correctly)
Final training samples:   81,378  ✅ Perfect size for QLoRA
Validation samples:        9,043  ✅ Good 90/10 split
Null values:                   0  ✅ Perfect clean data
Duplicates:                    0  ✅ No contamination
Avg input length:            654  ✅ Good rich context
Avg output length:           780  ✅ Detailed responses
All columns present:         Yes  ✅ Fine-tuning ready
```

**One thing to note:** iCliniq shows 7,319 in final but 20,325 in cleaned. This is because the deduplication step removed inputs that already existed in ChatDoctor. That is perfectly normal and correct behavior.

**Your data is production quality. Week 1 = 100% complete.**

---

# 📅 Week 2 Complete Plan

## What Week 2 is About

```
Week 1 → Collected raw data
Week 2 → Make that data perfect for training

Three jobs this week:
Job 1 → Generate Urdu synthetic data (2 days)
Job 2 → Final format verification (1 day)
Job 3 → Upload to Kaggle + prepare notebook (2 days)
```

---

## 📅 Day by Day Plan

```
Day 1 → Understand Urdu synthetic data strategy
         Setup GPT-4o API
         Generate first 1000 Urdu samples (test batch)

Day 2 → Generate remaining 4000 Urdu samples
         Save + convert to instruction format

Day 3 → Final quality check on ALL data
         Length analysis, token counting
         Remove any remaining bad samples

Day 4 → Upload final dataset to Kaggle
         Setup Kaggle notebook environment
         Install all training libraries

Day 5 → Test load BioMistral-7B on Kaggle
         Verify GPU access and memory
         Week 2 complete ✅
```

---

# 📚 Job 1 — Urdu Synthetic Data Generation

## Why Urdu Data is Non-Negotiable

```
Your 81,378 training samples = 100% English

Your target patients in Pakistan speak:
→ Urdu: "mujhe bukhaar hai"
→ Roman Urdu: "mera sir dard kar raha hai"
→ Mixed: "Doctor, meri back mein severe pain hai"

Without Urdu training data:
Patient types in Urdu → model gives garbage response
Patient frustrated → project fails in real world
```

## What Urdu Synthetic Data Looks Like

```
ENGLISH SAMPLE (what you have):
Input:  "I have fever and headache for 3 days"
Output: "Based on your symptoms..."

URDU SAMPLE (what you need to generate):
Input:  "mujhe 3 din se bukhaar aur sir dard ho
         raha hai, kya karna chahiye"
Output: "Aap ke symptoms sun kar lagta hai ke
         aap ko viral fever ho sakta hai..."

MIXED SAMPLE (most realistic Pakistani input):
Input:  "Doctor mere stomach mein 2 din se
         bohot pain hai aur vomiting bhi ho
         rahi hai"
Output: "Main samajh sakta hoon ke aap
         uncomfortable feel kar rahe hain..."
```

## Setup GPT-4o API

```python
# Install OpenAI library
pip install openai

# Get your API key from:
# platform.openai.com → API Keys → Create new key
# Free $5 credit is enough for 5000 samples

import openai
client = openai.OpenAI(api_key="your-key-here")

# Test it works
response = client.chat.completions.create(
    model="gpt-4o-mini",  # cheapest, good enough
    messages=[
        {"role": "user", "content": "Say hello in Urdu"}
    ]
)
print(response.choices[0].message.content)
# Expected: آپ کا استقبال ہے / Aap ka istaqbal hai
```

**Use `gpt-4o-mini` not `gpt-4o`** — 10x cheaper, good enough for data generation. 5000 samples will cost roughly $1-2.

---

## Urdu Generation Strategy — 3 Types

```
Type 1 → Pure Urdu script    (1500 samples)
          "مجھے بخار ہے"

Type 2 → Roman Urdu          (2000 samples)
          "mujhe bukhaar hai"  ← most common in Pakistan

Type 3 → Mixed Urdu-English  (1500 samples)
          "Doctor mera fever 3 din se hai"
```

Roman Urdu gets the most samples because that is exactly how Pakistani patients actually type on their phones.

---

## Complete Urdu Generation Code

```python
import openai
import pandas as pd
import time
import json
import os

client = openai.OpenAI(api_key="your-api-key-here")

# ─────────────────────────────────────────
# Common Pakistani medical scenarios
# These are seeds — GPT will create variations
# ─────────────────────────────────────────

SCENARIOS = [
    "fever and headache",
    "stomach pain and vomiting",
    "chest pain and shortness of breath",
    "back pain",
    "diabetes management",
    "blood pressure issues",
    "cough and cold",
    "skin rash and itching",
    "eye pain and redness",
    "knee and joint pain",
    "weakness and fatigue",
    "sleep problems",
    "anxiety and stress",
    "dengue fever symptoms",
    "typhoid symptoms",
    "malaria symptoms",
    "hepatitis symptoms",
    "kidney stone pain",
    "toothache",
    "ear pain",
    "pregnancy related questions",
    "child fever and crying",
    "diarrhea and dehydration",
    "allergy symptoms",
    "weight gain and obesity",
]

INSTRUCTION = """You are an empathetic AI health companion and medical assistant. 
You help patients by carefully listening to their symptoms, asking relevant follow-up 
questions when needed, providing a possible diagnosis with reasoning, and recommending 
holistic treatment including medicines, diet, exercise, and natural remedies. 
Always respond in a warm, caring, and supportive tone."""


def generate_urdu_sample(scenario, sample_type):
    """Generate one Urdu medical QA sample"""

    if sample_type == "roman_urdu":
        prompt = f"""Generate a realistic medical conversation sample in Roman Urdu 
(Urdu written in English letters, like Pakistanis type on phones).

Topic: {scenario}

Return ONLY a JSON object with exactly these two keys:
{{
  "input": "patient question in Roman Urdu (2-4 sentences, natural Pakistani speaking style)",
  "output": "doctor AI response in Roman Urdu (4-8 sentences, warm empathetic, include possible diagnosis + medicine + diet advice)"
}}

Make it sound like a real Pakistani patient typing on their phone.
Do not add any explanation. Return only the JSON."""

    elif sample_type == "urdu_script":
        prompt = f"""Generate a realistic medical conversation sample in Urdu script.

Topic: {scenario}

Return ONLY a JSON object with exactly these two keys:
{{
  "input": "patient question in Urdu script (2-3 sentences)",
  "output": "doctor AI response in Urdu script (4-6 sentences, warm, includes diagnosis and advice)"
}}

Do not add any explanation. Return only the JSON."""

    else:  # mixed
        prompt = f"""Generate a realistic medical conversation where a Pakistani patient 
mixes English and Urdu (Roman Urdu). This is very common in Pakistan.

Topic: {scenario}

Return ONLY a JSON object with exactly these two keys:
{{
  "input": "patient question mixing English and Roman Urdu naturally (2-4 sentences)",
  "output": "AI doctor response also mixing English and Roman Urdu naturally (4-8 sentences, warm, includes diagnosis + medicines + diet)"
}}

Example style: "Doctor mera fever 3 din se hai aur body aches bhi hain"
Do not add any explanation. Return only the JSON."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,  # some creativity
            max_tokens=500
        )

        content = response.choices[0].message.content.strip()

        # Clean response — remove markdown if present
        content = content.replace('```json', '').replace('```', '').strip()

        # Parse JSON
        data = json.loads(content)

        # Validate keys exist
        if 'input' not in data or 'output' not in data:
            return None

        # Validate not too short
        if len(data['input']) < 20 or len(data['output']) < 50:
            return None

        return {
            'instruction': INSTRUCTION,
            'input': data['input'].strip(),
            'output': data['output'].strip(),
            'source': f'synthetic_urdu_{sample_type}'
        }

    except Exception as e:
        print(f"    Error: {e}")
        return None


# ─────────────────────────────────────────
# Generation loop — generates 5000 samples
# ─────────────────────────────────────────

# Sample type distribution
SAMPLE_PLAN = [
    ("roman_urdu",  2000),  # most common Pakistani typing style
    ("mixed",       1500),  # mixed Urdu-English
    ("urdu_script", 1500),  # pure Urdu script
]

all_samples = []
total_target = 5000

print("Starting Urdu synthetic data generation...")
print(f"Target: {total_target} samples")
print("=" * 50)

for sample_type, count in SAMPLE_PLAN:
    print(f"\nGenerating {count} {sample_type} samples...")
    type_samples = []
    attempts = 0
    max_attempts = count * 2  # allow retries

    while len(type_samples) < count and attempts < max_attempts:
        # Rotate through scenarios
        scenario = SCENARIOS[attempts % len(SCENARIOS)]

        sample = generate_urdu_sample(scenario, sample_type)

        if sample:
            type_samples.append(sample)

        attempts += 1

        # Progress update every 100 samples
        if len(type_samples) % 100 == 0 and len(type_samples) > 0:
            print(f"  ✅ {len(type_samples)}/{count} generated...")

        # Rate limit — be gentle with API
        time.sleep(0.5)

    all_samples.extend(type_samples)
    print(f"  ✅ {sample_type}: {len(type_samples)} samples done")

print(f"\nTotal generated: {len(all_samples)}")
```

```python
# ─────────────────────────────────────────
# Save Urdu dataset
# ─────────────────────────────────────────

df_urdu = pd.DataFrame(all_samples)

os.makedirs('data/cleaned', exist_ok=True)
df_urdu.to_csv(
    'data/cleaned/urdu_synthetic_instruction.csv',
    index=False
)

print(f"\n✅ Saved {len(df_urdu)} Urdu samples")
print(f"\nType distribution:")
print(df_urdu['source'].value_counts())

print(f"\nSample Roman Urdu example:")
roman = df_urdu[
    df_urdu['source'] == 'synthetic_urdu_roman_urdu'
].iloc[0]
print(f"INPUT:  {roman['input']}")
print(f"OUTPUT: {roman['output'][:200]}")
```

---

# 📚 Job 2 — Final Format Verification

Run this after Urdu data is generated:

```python
import pandas as pd

# Load everything including new Urdu data
df_train  = pd.read_csv('data/final/train.csv')
df_val    = pd.read_csv('data/final/val.csv')
df_urdu   = pd.read_csv(
    'data/cleaned/urdu_synthetic_instruction.csv'
)

# Add Urdu data to training set
df_train_final = pd.concat(
    [df_train, df_urdu], ignore_index=True
)

# Shuffle again after adding Urdu
df_train_final = df_train_final.sample(
    frac=1, random_state=42
).reset_index(drop=True)

# Token length check
# BioMistral max context = 2048 tokens
# Rough estimate: 1 token ≈ 4 characters
df_train_final['total_chars'] = (
    df_train_final['input'].str.len() +
    df_train_final['output'].str.len()
)
df_train_final['est_tokens'] = (
    df_train_final['total_chars'] / 4
).astype(int)

too_long = (df_train_final['est_tokens'] > 1800).sum()
print(f"Samples over token limit: {too_long}")

# Remove too long samples
df_train_final = df_train_final[
    df_train_final['est_tokens'] <= 1800
]

# Save final training file
df_train_final[['instruction','input','output']].to_csv(
    'data/final/train_final.csv', index=False
)

print(f"\n✅ Final training file ready")
print(f"   Training samples: {len(df_train_final):,}")
print(f"   Validation samples: {len(df_val):,}")
```

---

# 📚 Job 3 — Upload to Kaggle

## Step 1 — Zip your final data

```python
import zipfile
import os

with zipfile.ZipFile(
    'health_companion_dataset.zip', 'w',
    zipfile.ZIP_DEFLATED
) as zipf:
    zipf.write('data/final/train_final.csv', 'train_final.csv')
    zipf.write('data/final/val.csv', 'val.csv')

size = os.path.getsize('health_companion_dataset.zip')
print(f"✅ Zip created: {size/(1024*1024):.1f} MB")
```

## Step 2 — Upload to Kaggle

```
1. Go to kaggle.com
2. Click your profile → Datasets
3. Click "New Dataset"
4. Upload health_companion_dataset.zip
5. Name it: "health-companion-fyp-dataset"
6. Set to Private
7. Click Create
```

## Step 3 — Setup Kaggle Training Notebook

```
1. Go to kaggle.com → Notebooks → New Notebook
2. Click Settings (right panel)
3. Accelerator → GPU T4 x2
4. Internet → ON (needed to download model)
5. Add your dataset under "Add Data"
6. Name notebook: "health-companion-finetune"
```

## Step 4 — Install libraries in Kaggle notebook

```python
# Run this as first cell in Kaggle notebook
!pip install -q transformers peft bitsandbytes trl \
             accelerate datasets sentencepiece

import torch
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
print(f"GPU count: {torch.cuda.device_count()}")

# Expected output:
# GPU: Tesla T4
# VRAM: 15.8 GB
# GPU count: 2
```

---

# Week 2 Completion Checklist

```
Day 1 ✅ GPT-4o API setup + test batch 1000 samples
Day 2 ✅ Full 5000 Urdu samples generated + saved
Day 3 ✅ Token length check + final train_final.csv ready
Day 4 ✅ Dataset zipped + uploaded to Kaggle
Day 5 ✅ Kaggle notebook created + GPU verified + 
          libraries installed
```

---

# Week 2 → Week 3 Bridge

```
End of Week 2 you will have:

data/final/
├── train_final.csv  ← 86,000+ samples (81k + 5k Urdu)
└── val.csv          ←  9,043 samples

On Kaggle:
└── Notebook ready with GPU T4 x2
    Libraries installed
    Dataset loaded
    Ready to paste fine-tuning code

Week 3 Day 1 → Paste QLoRA config and press Run
```

Start with Day 1 — setting up GPT-4o API and generating your first test batch of 100 Urdu samples. Once those look good, scale to 5000. Share your first 3 generated samples and I will verify quality before you generate the full batch. 🚀