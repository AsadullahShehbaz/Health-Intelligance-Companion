# Week 1 Complete Guide: Data Collection
## Your First Step Toward FYP 🎯

---

Let's go step by step like a conversation. No jargon without explanation. Everything hands-on.

---

## 💬 First — Understand What You're Actually Doing

Think of it like this:

> You want to teach a student (BioMistral-7B) to become a doctor. But before teaching, you need **textbooks and practice questions.** That's exactly what datasets are — textbooks for your AI.

You need two types of data:

```
Type 1 → Fine-tuning data   (teaches HOW to think and respond)
Type 2 → RAG data           (gives it WHAT to know — Week 4)
```

This week you only focus on **Type 1 — Fine-tuning datasets.**

---

## 💬 What Datasets Are You Collecting?

Here are your 7 targets this week:

| # | Dataset | Why You Need It |
|---|---|---|
| 1 | ChatDoctor 100k | Real doctor-patient conversations |
| 2 | MedQA (USMLE) | Medical diagnostic reasoning |
| 3 | MedMCQA | South Asia medical context |
| 4 | MedDialog | Real clinical dialogues |
| 5 | iCliniq | Real patient questions + doctor answers |
| 6 | PubMedQA | Biomedical research reasoning |
| 7 | Disease-Symptom Dataset | Symptom to disease mapping |

All free. All on HuggingFace or Kaggle.

---

## 💬 Step 1 — Setup Your Environment First

Before touching any dataset, setup your workspace properly.

### On Your Local Machine

```bash
# Create project folder
mkdir health-companion-fyp
cd health-companion-fyp

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install what you need this week
pip install datasets pandas numpy huggingface_hub kaggle tqdm
```

### Your Project Folder Structure

```
health-companion-fyp/
│
├── data/
│   ├── raw/          ← downloaded datasets go here
│   ├── cleaned/      ← after cleaning goes here
│   └── final/        ← merged final dataset goes here
│
├── notebooks/
│   └── week1_data_collection.ipynb
│
├── src/
│   └── (empty for now, code goes here later)
│
└── README.md
```

Create this structure:

```bash
mkdir -p data/raw data/cleaned data/final notebooks src
```

---

## 💬 Step 2 — Download Dataset 1: ChatDoctor 100k

This is your most important dataset. Real doctor-patient conversations.

```python
# In your notebook or Python file
from datasets import load_dataset
import pandas as pd
import os

# Download ChatDoctor
print("Downloading ChatDoctor...")
dataset = load_dataset("avalon-studio/ChatDoctor-200k")

# See what's inside
print(dataset)
print("\nFirst sample:")
print(dataset['train'][0])
```

You'll see something like:
```
{
  "input": "Doctor, I have been having chest pain for 2 days",
  "output": "I understand your concern. Can you describe 
             the pain? Is it sharp or dull?..."
}
```

Save it:
```python
# Convert to pandas and save
df = pd.DataFrame(dataset['train'])
df.to_csv('data/raw/chatdoctor.csv', index=False)
print(f"Saved {len(df)} samples")
# Expected: ~200k rows
```

---

## 💬 Step 3 — Download Dataset 2: MedQA

This teaches diagnostic reasoning — exactly like a real medical exam.

```python
# Download MedQA
print("Downloading MedQA...")
dataset = load_dataset("bigbio/med_qa",
                       trust_remote_code=True)

print(dataset['train'][0])
```

You'll see:
```
{
  "question": "A 45 year old man presents with chest pain...",
  "options": {"A": "Myocardial Infarction", 
              "B": "Angina", ...},
  "answer": "A"
}
```

Save it:
```python
df_train = pd.DataFrame(dataset['train'])
df_test = pd.DataFrame(dataset['test'])
df_medqa = pd.concat([df_train, df_test])
df_medqa.to_csv('data/raw/medqa.csv', index=False)
print(f"Saved {len(df_medqa)} samples")
```

---

## 💬 Step 4 — Download Dataset 3: MedMCQA

South Asian medical context — closest to Pakistan's medical scenarios.

```python
print("Downloading MedMCQA...")
dataset = load_dataset("medmcqa")

print(dataset['train'][0])
```

Looks like:
```
{
  "question": "Which of the following is most common 
               cause of chest pain in young patients?",
  "opa": "Musculoskeletal",
  "opb": "Cardiac", 
  "opc": "GERD",
  "opd": "Anxiety",
  "cop": 0   ← correct option index
}
```

Save it:
```python
df = pd.DataFrame(dataset['train'])
df.to_csv('data/raw/medmcqa.csv', index=False)
print(f"Saved {len(df)} samples")
```

---

## 💬 Step 5 — Download Dataset 4: MedDialog

Real clinical dialogues between patients and doctors.

```python
print("Downloading MedDialog...")
dataset = load_dataset("medical_dialog",
                       "processed.en",
                       trust_remote_code=True)

print(dataset['train'][0])
```

Save it:
```python
df = pd.DataFrame(dataset['train'])
df.to_csv('data/raw/meddialog.csv', index=False)
print(f"Saved {len(df)} samples")
```

---

## 💬 Step 6 — Download Dataset 5: iCliniq

Real patients asking real doctors — very natural language, messy, authentic.

```python
print("Downloading iCliniq...")
dataset = load_dataset("lavita/ChatDoctor-iCliniq")

print(dataset['train'][0])

df = pd.DataFrame(dataset['train'])
df.to_csv('data/raw/icliniq.csv', index=False)
print(f"Saved {len(df)} samples")
```

---

## 💬 Step 7 — Download Dataset 6: PubMedQA

Biomedical research reasoning — teaches the model to think scientifically.

```python
print("Downloading PubMedQA...")
dataset = load_dataset("qiaojin/PubMedQA",
                       "pqa_labeled",
                       trust_remote_code=True)

print(dataset['train'][0])

df = pd.DataFrame(dataset['train'])
df.to_csv('data/raw/pubmedqa.csv', index=False)
print(f"Saved {len(df)} samples")
```

---

## 💬 Step 8 — Download Dataset 7: Disease-Symptom

Direct symptom to disease mapping — core diagnostic knowledge.

```python
print("Downloading Disease-Symptom dataset...")
dataset = load_dataset("QuyenAnhDE/Diseases_Symptoms")

print(dataset['train'][0])

df = pd.DataFrame(dataset['train'])
df.to_csv('data/raw/disease_symptoms.csv', index=False)
print(f"Saved {len(df)} samples")
```

---

## 💬 Step 9 — Verify Everything Downloaded

Run this checkpoint to confirm all 7 datasets are saved:

```python
import os

datasets = [
    'chatdoctor.csv',
    'medqa.csv',
    'medmcqa.csv',
    'meddialog.csv',
    'icliniq.csv',
    'pubmedqa.csv',
    'disease_symptoms.csv'
]

print("=" * 40)
print("DATASET DOWNLOAD CHECKPOINT")
print("=" * 40)

total_samples = 0
for name in datasets:
    path = f'data/raw/{name}'
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"✅ {name}: {len(df):,} samples")
        total_samples += len(df)
    else:
        print(f"❌ {name}: MISSING")

print("=" * 40)
print(f"Total samples collected: {total_samples:,}")
```

Expected output:
```
========================================
DATASET DOWNLOAD CHECKPOINT
========================================
✅ chatdoctor.csv:     200,000 samples
✅ medqa.csv:           12,723 samples
✅ medmcqa.csv:        182,822 samples
✅ meddialog.csv:       11,058 samples
✅ icliniq.csv:         30,000 samples
✅ pubmedqa.csv:         1,000 samples
✅ disease_symptoms.csv:   400 samples
========================================
Total samples collected: ~437,000 samples
```

---

## 💬 Step 10 — Basic Cleaning (Same Day)

Don't leave raw data dirty. Clean it the same day you download it.

### What to Clean

```
❌ Remove null/empty rows
❌ Remove rows where input or output is too short (< 10 chars)
❌ Remove duplicate rows
❌ Remove rows with only special characters
```

### Cleaning Code

```python
def clean_dataset(df, input_col, output_col, dataset_name):
    print(f"\nCleaning {dataset_name}...")
    original = len(df)

    # Step 1: Drop nulls
    df = df.dropna(subset=[input_col, output_col])

    # Step 2: Convert to string
    df[input_col] = df[input_col].astype(str)
    df[output_col] = df[output_col].astype(str)

    # Step 3: Remove too short
    df = df[df[input_col].str.len() > 10]
    df = df[df[output_col].str.len() > 10]

    # Step 4: Remove duplicates
    df = df.drop_duplicates(subset=[input_col])

    # Step 5: Strip whitespace
    df[input_col] = df[input_col].str.strip()
    df[output_col] = df[output_col].str.strip()

    cleaned = len(df)
    removed = original - cleaned
    print(f"  Before: {original:,}")
    print(f"  After:  {cleaned:,}")
    print(f"  Removed: {removed:,} bad rows")

    return df

# Clean ChatDoctor (most important one)
df_chat = pd.read_csv('data/raw/chatdoctor.csv')
df_chat_clean = clean_dataset(
    df_chat, 'input', 'output', 'ChatDoctor'
)
df_chat_clean.to_csv(
    'data/cleaned/chatdoctor_clean.csv', index=False
)
```

Apply same function to all 7 datasets with their correct column names.

---

## 💬 Step 11 — Explore Your Data

Before ending Week 1, always look at your data visually. This prevents surprises during training.

```python
# Load cleaned ChatDoctor
df = pd.read_csv('data/cleaned/chatdoctor_clean.csv')

# Check length distribution
df['input_length'] = df['input'].str.len()
df['output_length'] = df['output'].str.len()

print("Input length stats:")
print(df['input_length'].describe())

print("\nOutput length stats:")
print(df['output_length'].describe())

# Print 5 random samples to read manually
print("\n5 Random Samples:")
print("=" * 50)
for _, row in df.sample(5).iterrows():
    print(f"PATIENT: {row['input'][:200]}")
    print(f"DOCTOR:  {row['output'][:200]}")
    print("-" * 50)
```

**Why do this?** If you see garbage data here — broken text, HTML tags, random symbols — you catch it now before it corrupts your fine-tuned model.

---

## 💬 Week 1 Completion Checklist

```
Day 1 → Setup environment + project structure
Day 2 → Download datasets 1, 2, 3 (ChatDoctor, MedQA, MedMCQA)
Day 3 → Download datasets 4, 5, 6, 7 (MedDialog, iCliniq, PubMedQA, Disease-Symptom)
Day 4 → Run cleaning on all 7 datasets
Day 5 → Explore data, read samples manually, fix any issues
Day 6 → Push everything to GitHub
Day 7 → Buffer day (fix anything broken, rest)
```

---

## 💬 Common Problems & Fixes

**Problem:** `Dataset not found` error
```python
# Fix: Add trust_remote_code=True
dataset = load_dataset("dataset_name", trust_remote_code=True)
```

**Problem:** Download too slow or fails midway
```python
# Fix: Download in streaming mode
dataset = load_dataset("dataset_name", streaming=True)
# Then iterate and save manually
```

**Problem:** Not enough disk space
```
ChatDoctor alone = ~500MB
All 7 datasets = ~2-3GB total
Make sure you have 5GB free minimum
```

**Problem:** HuggingFace rate limit
```python
# Fix: Login with your HuggingFace token
from huggingface_hub import login
login(token="your_hf_token_here")
# Get free token at huggingface.co/settings/tokens
```

---

## 💬 End of Week 1 Goal

By Sunday night you should have:

```
✅ Project GitHub repo with proper structure
✅ All 7 datasets downloaded in data/raw/
✅ All 7 datasets cleaned in data/cleaned/
✅ You've manually read at least 20 samples from each dataset
✅ You know what columns each dataset has
✅ You understand what each dataset contributes to your FYP
```

When Week 1 is done, you're ready for Week 2 — converting all of this into the instruction format that BioMistral will actually learn from.

**One dataset at a time. One day at a time. You've got this. 🚀**