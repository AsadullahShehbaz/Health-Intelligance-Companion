# Week 3 — Fine-Tuning BioMistral-7B on Kaggle

## Before Writing Any Code — Understand the Plan

```
What you are doing this week:
Taking BioMistral-7B (already knows medicine)
Teaching it NEW behaviors using YOUR dataset:
  → Talk like a caring companion not a robot
  → Understand Urdu and Roman Urdu
  → Output structured diagnosis + treatment
  → Ask follow-up questions like a real doctor

Method: QLoRA (train only 1% of parameters)
Platform: Kaggle (2x T4 GPU, free)
Time: 6-10 hours of training
```

---

## Day 1 — Setup Kaggle Notebook Correctly

### Step 1 — Create Notebook

```
1. Go to kaggle.com
2. Click "Create" → "New Notebook"
3. Right panel Settings:
   → Accelerator: GPU T4 x2  ← CRITICAL
   → Internet: ON            ← CRITICAL
   → Persistence: Files only
4. Click "Add Data" → find your 
   health-companion-fyp-dataset
5. Name notebook: biomistral-finetune-fyp
```

### Step 2 — Verify Everything Before Starting

```python
# Cell 1 — Run this FIRST before anything else

import os
import torch

print("=" * 50)
print("  KAGGLE ENVIRONMENT CHECK")
print("=" * 50)

# GPU check
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(i)
        mem  = torch.cuda.get_device_properties(i).total_memory
        print(f"✅ GPU {i}: {name} — {mem/1e9:.1f} GB")
else:
    print("❌ NO GPU — Check accelerator settings")

# Dataset check
dataset_path = '/kaggle/input/health-companion-fyp-dataset'
for f in ['train_final.csv', 'val.csv']:
    full = os.path.join(dataset_path, f)
    if os.path.exists(full):
        import pandas as pd
        df = pd.read_csv(full)
        print(f"✅ {f}: {len(df):,} samples")
    else:
        print(f"❌ {f}: NOT FOUND")

# Disk space
statvfs = os.statvfs('/')
free_gb = (statvfs.f_frsize * statvfs.f_bavail) / 1e9
print(f"✅ Free disk: {free_gb:.1f} GB")

print("=" * 50)
```

Expected output:
```
✅ GPU 0: Tesla T4 — 15.8 GB
✅ GPU 1: Tesla T4 — 15.8 GB
✅ train_final.csv: 83,000+ samples
✅ val.csv: 9,043 samples
✅ Free disk: 18.5 GB
```

---

## Day 1 — Install All Libraries

```python
# Cell 2 — Install everything needed

!pip install -q \
    transformers==4.40.0 \
    peft==0.10.0 \
    bitsandbytes==0.43.1 \
    trl==0.8.6 \
    accelerate==0.29.3 \
    datasets==2.19.0 \
    sentencepiece==0.2.0 \
    einops==0.7.0

print("✅ All libraries installed")
```

```python
# Cell 3 — Verify imports work

import torch
import transformers
import peft
import trl
import bitsandbytes as bnb
from datasets import Dataset
import pandas as pd

print(f"✅ transformers: {transformers.__version__}")
print(f"✅ peft:         {peft.__version__}")
print(f"✅ trl:          {trl.__version__}")
print(f"✅ torch:        {torch.__version__}")
print(f"✅ bitsandbytes: {bnb.__version__}")
```

---

## Day 2 — Load and Prepare Dataset

```python
# Cell 4 — Load your dataset

import pandas as pd
from datasets import Dataset

DATASET_PATH = '/kaggle/input/health-companion-fyp-dataset'

# Load train and val
df_train = pd.read_csv(f'{DATASET_PATH}/train_final.csv')
df_val   = pd.read_csv(f'{DATASET_PATH}/val.csv')

print(f"Train samples: {len(df_train):,}")
print(f"Val samples:   {len(df_val):,}")

# Quick quality check
print(f"\nNull check:")
print(f"  Train nulls: {df_train.isnull().sum().sum()}")
print(f"  Val nulls:   {df_val.isnull().sum().sum()}")

# Preview one sample
sample = df_train.sample(1).iloc[0]
print(f"\nSample preview:")
print(f"INSTRUCTION: {sample['instruction'][:100]}...")
print(f"INPUT:       {sample['input'][:150]}...")
print(f"OUTPUT:      {sample['output'][:150]}...")
```

```python
# Cell 5 — Format into prompt template
# This is how BioMistral expects input during training

def format_prompt(row):
    """
    Convert instruction/input/output into
    single training text that BioMistral understands
    """
    prompt = f"""### Instruction:
{row['instruction']}

### Input:
{row['input']}

### Response:
{row['output']}"""
    return prompt


# Apply formatting
df_train['text'] = df_train.apply(format_prompt, axis=1)
df_val['text']   = df_val.apply(format_prompt, axis=1)

# Convert to HuggingFace Dataset format
train_dataset = Dataset.from_pandas(
    df_train[['text']].reset_index(drop=True)
)
val_dataset = Dataset.from_pandas(
    df_val[['text']].reset_index(drop=True)
)

print(f"✅ Train dataset: {len(train_dataset):,} samples")
print(f"✅ Val dataset:   {len(val_dataset):,} samples")

# Check one formatted sample
print(f"\nFormatted sample preview:")
print(train_dataset[0]['text'][:400])
```

```python
# Cell 6 — Analyze token lengths
# Critical: samples longer than 1024 tokens get truncated
# You want to know how many samples are affected

from transformers import AutoTokenizer

MODEL_NAME = "BioMistral/BioMistral-7B"

print("Loading tokenizer to check lengths...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

# Sample 2000 rows for speed
sample_texts = df_train['text'].sample(
    2000, random_state=42
).tolist()

lengths = [
    len(tokenizer.encode(t)) 
    for t in sample_texts
]

import numpy as np
print(f"\nToken length analysis (sample of 2000):")
print(f"  Min:    {min(lengths)}")
print(f"  Max:    {max(lengths)}")
print(f"  Mean:   {np.mean(lengths):.0f}")
print(f"  Median: {np.median(lengths):.0f}")
print(f"  >1024 tokens: "
      f"{sum(1 for l in lengths if l > 1024)} samples "
      f"({sum(1 for l in lengths if l>1024)/20:.1f}%)")
print(f"  >512 tokens:  "
      f"{sum(1 for l in lengths if l > 512)} samples")
```

---

## Day 2 — Configure QLoRA + Load Model

```python
# Cell 7 — QLoRA Configuration
# This is the heart of your fine-tuning setup

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, TaskType
import torch

# ── 4-bit Quantization Config ─────────────────────
# This reduces BioMistral from 14GB → 4GB in memory
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",       # best quantization type
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True   # extra memory saving
)

# ── LoRA Config ───────────────────────────────────
# r=16: how many parameters to train
# Higher r = more capacity but more memory
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,          # scaling factor (2x r is standard)
    target_modules=[        # which layers to fine-tune
        "q_proj",           # query projection
        "k_proj",           # key projection
        "v_proj",           # value projection
        "o_proj",           # output projection
        "gate_proj",        # MLP layers
        "up_proj",
        "down_proj"
    ],
    lora_dropout=0.05,      # prevent overfitting
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

print("✅ QLoRA configuration ready")
print(f"   Quantization: 4-bit NF4")
print(f"   LoRA rank: 16")
print(f"   LoRA alpha: 32")
print(f"   Target modules: q,k,v,o,gate,up,down projections")
```

```python
# Cell 8 — Load BioMistral-7B Model
# This will take 5-10 minutes to download
# BioMistral is already pre-trained on PubMed medical data

print("Loading BioMistral-7B...")
print("(This takes 5-10 minutes — downloading ~14GB model)")

MODEL_NAME = "BioMistral/BioMistral-7B"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",          # auto-distribute across 2 GPUs
    trust_remote_code=True,
    torch_dtype=torch.float16
)

# Disable cache for training (saves memory)
model.config.use_cache = False
model.config.pretraining_tp = 1

print("✅ BioMistral-7B loaded successfully")

# Check memory usage
for i in range(torch.cuda.device_count()):
    allocated = torch.cuda.memory_allocated(i) / 1e9
    total     = torch.cuda.get_device_properties(i)\
                    .total_memory / 1e9
    print(f"   GPU {i}: {allocated:.1f}GB / {total:.1f}GB used")
```

```python
# Cell 9 — Apply LoRA to model
# This adds the trainable adapter layers

from peft import get_peft_model, prepare_model_for_kbit_training

# Prepare model for QLoRA training
model = prepare_model_for_kbit_training(model)

# Apply LoRA adapters
model = get_peft_model(model, lora_config)

# Show trainable parameters
model.print_trainable_parameters()

# Expected output:
# trainable params: 41,943,040
# all params: 3,794,366,464
# trainable%: 1.1054%
# 
# Only 1.1% of parameters are trained — very efficient!
```

---

## Day 3 — Training Arguments + Start Training

```python
# Cell 10 — Training Arguments
# Every number here is carefully chosen for T4 x2 GPU

from transformers import TrainingArguments

OUTPUT_DIR = '/kaggle/working/biomistral-health-companion'

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    # ── Batch settings ─────────────────────────────
    per_device_train_batch_size=4,    # 4 samples per GPU
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,    # effective batch = 4×4×2 = 32

    # ── Training duration ──────────────────────────
    num_train_epochs=3,               # 3 full passes through data
    max_steps=-1,                     # -1 means use epochs not steps

    # ── Learning rate ──────────────────────────────
    learning_rate=2e-4,               # standard for LoRA
    warmup_ratio=0.03,                # warm up for first 3%
    lr_scheduler_type="cosine",       # smooth decay

    # ── Precision ──────────────────────────────────
    fp16=True,                        # half precision saves memory
    bf16=False,                       # T4 doesn't support bf16

    # ── Logging ────────────────────────────────────
    logging_steps=25,                 # log every 25 steps
    logging_dir=f'{OUTPUT_DIR}/logs',

    # ── Saving ─────────────────────────────────────
    save_strategy="steps",
    save_steps=200,                   # save checkpoint every 200 steps
    save_total_limit=2,               # keep only 2 checkpoints
    load_best_model_at_end=True,

    # ── Evaluation ─────────────────────────────────
    evaluation_strategy="steps",
    eval_steps=200,

    # ── Optimization ───────────────────────────────
    optim="paged_adamw_32bit",        # memory-efficient optimizer
    group_by_length=True,             # group similar lengths = faster
    dataloader_num_workers=2,

    # ── Misc ───────────────────────────────────────
    report_to="none",                 # no wandb logging needed
    remove_unused_columns=True,
)

print("✅ Training arguments configured")
print(f"   Epochs:         3")
print(f"   Batch size:     4 × 4 steps × 2 GPUs = 32 effective")
print(f"   Learning rate:  2e-4")
print(f"   Save every:     200 steps")
```

```python
# Cell 11 — Create SFT Trainer
# SFT = Supervised Fine-Tuning
# This is the standard approach for instruction tuning

from trl import SFTTrainer
from transformers import DataCollatorForSeq2Seq

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    dataset_text_field="text",    # column name in your dataset
    max_seq_length=1024,          # max tokens per sample
    packing=False,                # don't pack multiple samples
)

print("✅ SFT Trainer created")
print(f"   Training samples: {len(train_dataset):,}")
print(f"   Validation samples: {len(val_dataset):,}")

# Estimate training time
steps_per_epoch = len(train_dataset) // 32
total_steps     = steps_per_epoch * 3
print(f"\n   Steps per epoch: ~{steps_per_epoch:,}")
print(f"   Total steps:     ~{total_steps:,}")
print(f"   Est. time:       6-10 hours on T4 x2")
```

```python
# Cell 12 — START TRAINING
# This is the big moment
# Do NOT close Kaggle tab while this runs

print("🔥 Starting fine-tuning...")
print("Monitor loss in the logs below")
print("Good loss curve: starts ~2.5, drops to ~0.8-1.2")
print("=" * 50)

# Start training
trainer.train()

print("\n✅ Training complete!")
```

---

## What to Watch During Training

```
Good signs:
✅ Loss starts around 2.0-2.5
✅ Loss steadily decreases each epoch
✅ Validation loss follows training loss closely
✅ No CUDA out of memory errors

Bad signs — what to do:
❌ CUDA OOM → reduce batch size from 4 to 2
❌ Loss not decreasing → reduce lr to 1e-4
❌ Loss goes to 0 too fast → model overfitting,
                              reduce epochs to 2
❌ Validation loss increasing → early stopping needed
```

---

## Day 3-4 — Save Model After Training

```python
# Cell 13 — Save the fine-tuned adapter weights

SAVE_PATH = '/kaggle/working/biomistral-fyp-adapter'

# Save LoRA adapter (small file ~100MB)
model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)

print(f"✅ Model adapter saved to {SAVE_PATH}")

# Check what was saved
import os
files = os.listdir(SAVE_PATH)
for f in files:
    size = os.path.getsize(f'{SAVE_PATH}/{f}')
    print(f"   {f}: {size/1e6:.1f} MB")
```

```python
# Cell 14 — Push to HuggingFace Hub
# So you can access it from anywhere later

from huggingface_hub import login

# Get token from huggingface.co/settings/tokens
login(token="your-hf-token-here")

# Push adapter weights
model.push_to_hub(
    "your-username/biomistral-health-companion-fyp",
    private=True    # keep private for now
)
tokenizer.push_to_hub(
    "your-username/biomistral-health-companion-fyp",
    private=True
)

print("✅ Model pushed to HuggingFace Hub")
print("Access at: huggingface.co/your-username/"
      "biomistral-health-companion-fyp")
```

---

## Day 4-5 — Test Your Fine-Tuned Model

```python
# Cell 15 — Load and test the model

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

print("Loading fine-tuned model for testing...")

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "BioMistral/BioMistral-7B",
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16
)

# Load your fine-tuned adapter on top
ft_model = PeftModel.from_pretrained(
    base_model,
    SAVE_PATH
)
ft_model.eval()

print("✅ Fine-tuned model loaded")
```

```python
# Cell 16 — Test function

def ask_health_companion(patient_input, max_tokens=500):
    """Test your fine-tuned model"""

    prompt = f"""### Instruction:
You are an empathetic AI health companion and medical assistant. 
You help patients by carefully listening to their symptoms, asking relevant follow-up 
questions when needed, providing a possible diagnosis with reasoning, and recommending 
holistic treatment including medicines, diet, exercise, and natural remedies. 
Always respond in a warm, caring, and supportive tone.

### Input:
{patient_input}

### Response:"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    ).to("cuda")

    with torch.no_grad():
        outputs = ft_model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(
        outputs[0][inputs['input_ids'].shape[1]:],
        skip_special_tokens=True
    )
    return response.strip()
```

```python
# Cell 17 — Run test cases

test_cases = [
    # English test
    "I have been having severe headache and fever \
for 3 days. I also feel very weak and tired.",

    # Roman Urdu test
    "Doctor mujhe 2 din se bukhaar hai aur sar \
bhi dard kar raha hai, kya karna chahiye?",

    # Mixed test
    "Mera stomach 3 din se pain kar raha hai \
aur vomiting bhi ho rahi hai. Main kya karoon?",

    # Complex case
    "I am diabetic and my blood sugar has been \
very high lately. I also have swelling in my feet \
and feel dizzy sometimes."
]

print("=" * 55)
print("  FINE-TUNED MODEL TEST RESULTS")
print("=" * 55)

for i, test in enumerate(test_cases, 1):
    print(f"\nTEST {i}:")
    print(f"PATIENT: {test}")
    print(f"\nAI COMPANION:")
    response = ask_health_companion(test)
    print(response)
    print("-" * 55)
```

---

## Week 3 Success Criteria

```
✅ Training completed without crashing
✅ Final training loss below 1.2
✅ Model responds in Urdu when asked in Urdu
✅ Model gives structured diagnosis + treatment
✅ Model asks follow-up questions
✅ Model adapter saved to HuggingFace
✅ All 4 test cases give sensible responses
```

---

## Week 3 Complete Schedule

```
Day 1 (Apr 10) → Setup notebook + verify GPU
                  Install libraries + run checks

Day 2 (Apr 11) → Load dataset + format prompts
                  Configure QLoRA + Load BioMistral

Day 3 (Apr 12) → Start training (press run, monitor)
                  Training runs 6-10 hours

Day 4 (Apr 13) → Training finishes
                  Save adapter + push to HuggingFace

Day 5 (Apr 14) → Run all test cases
                  Verify Urdu + English responses
                  Fix issues if any
                  Week 3 complete ✅
```

---

Start with Cell 1 — environment check. Run it and share the output. We confirm GPU is working before touching any training code. 🚀