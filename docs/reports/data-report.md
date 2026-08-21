
# Phase 1 Data Collection
       
### 📦 RAW DATASETS DOWNLOADED:
  ✅ ChatDoctor           112,165 samples
  ✅ MedQA                 11,451 samples
  ✅ MedMCQA              182,822 samples
  ✅ MedDialog              9,250 samples
  ✅ iCliniq                7,321 samples
  ✅ PubMedQA               1,000 samples
  ✅ DiseaseSymptoms          400 samples
  ────────────────────────────────────────
  TOTAL RAW            324,409 samples

### 🧹 CLEANED & CONVERTED DATASETS:
  ✅ ChatDoctor           112,165 samples  | format: OK
  ✅ MedQA                 11,451 samples  | format: OK
  ✅ MedMCQA              182,822 samples  | format: OK
  ✅ MedDialog              9,250 samples  | format: OK
  ✅ iCliniq               20,325 samples  | format: OK
  ✅ PubMedQA               1,000 samples  | format: OK
  ✅ DiseaseSymptoms        1,600 samples  | format: OK
  ────────────────────────────────────────
  TOTAL CLEANED        338,613 samples

### 🎯 FINAL MERGED DATASET:

  ✅ merged_full.csv       90,421 samples
  ✅ train.csv             81,378 samples
  ✅ val.csv                9,043 samples

### 📊 SOURCE DISTRIBUTION IN FINAL DATASET:

  MedMCQA              30,000 ( 33.2%) ████████████████
  ChatDoctor           29,827 ( 33.0%) ████████████████
  MedQA                11,451 ( 12.7%) ██████
  MedDialog             9,250 ( 10.2%) █████
  iCliniq               7,319 (  8.1%) ████
  DiseaseSymptoms       1,574 (  1.7%) 
  PubMedQA              1,000 (  1.1%) 

### 🔍 DATA QUALITY CHECKS:

  Null inputs:               0  ✅
  Null outputs:              0  ✅
  Duplicate inputs:          0  ✅
  Too short inputs:          0  ✅
  Too short outputs:         0  ✅
  Avg input length:        654  chars
  Avg output length:       780  chars

### ✅ COLUMN VERIFICATION:

  ✅ 'instruction' column: Present
  ✅ 'input' column: Present
  ✅ 'output' column: Present

💾 FILE SIZES ON DISK:

  Raw        folder:   421.4 MB
  Cleaned    folder:   477.9 MB
  Final      folder:   313.0 MB


  📅 Phase 1 MILESTONE SUMMARY

  ✅ Environment setup
  ✅ All 7 datasets downloaded
  ✅ All datasets converted
  ✅ Instruction format applied
  ✅ Datasets balanced
  ✅ Dataset shuffled
  ✅ Train/val split done
  ✅ Final files saved


  Phase 1 STATUS: COMPLETE ✅
# Phase 2 → Urdu Synthetic Data Generation
        + Final format verification
        + Upload to Kaggle for training


Total samples:    2,209
After dedup:      1,858
Duplicates removed: 351

✅ Final Urdu dataset saved!
   1,858 samples ready

### Distribution:
source
synthetic_urdu_roman_urdu    1858
Name: count, dtype: int64

### Sample preview:
- INPUT:  Mujhe kal raat se bukhar hai aur sar bhi bohat heavy lag raha hai. Body bhi toot rahi hai aur kamzori feel ho rahi hai.
- OUTPUT: Aap ki symptoms se lagta hai ke viral fever ho sakta hai. Aap Paracetamol le sakte hain bukhar aur dard ke liye. Pani aur fresh juices zyada piyen taake hydration rahe. Adrak wali chai aur yakhni bhi 
# BUILDING 10K TRAIN + 500 TEST + 10.5K FULL DATASET

======================================================================
 BUILDING 10K TRAIN + 500 TEST + 10.5K FULL DATASET
======================================================================

Processing: chatdoctor
  Required train : 3,500
  Required test  : 175
  Required total : 3,675
  Valid samples   : 111,386
  ✅ Selected       : 3,675
  ✅ Train          : 3,500
  ✅ Test           : 175

Processing: disease_symptoms
  Required train : 700
  Required test  : 35
  Required total : 735
  Valid samples   : 800
  ✅ Selected       : 735
  ✅ Train          : 700
  ✅ Test           : 35

Processing: icliniq
  Required train : 2,000
  Required test  : 100
  Required total : 2,100
  Valid samples   : 7,316
  ✅ Selected       : 2,100
  ✅ Train          : 2,000
  ✅ Test           : 100

Processing: meddialog
  Required train : 800
  Required test  : 40
  Required total : 840
  Valid samples   : 9,250
  ✅ Selected       : 840
  ✅ Train          : 800
  ✅ Test           : 40

Processing: medmcqa
  Required train : 1,500
  Required test  : 75
  Required total : 1,575
  Valid samples   : 182,822
  ✅ Selected       : 1,575
  ✅ Train          : 1,500
  ✅ Test           : 75

Processing: medqa
  Required train : 1,000
  Required test  : 50
  Required total : 1,050
  Valid samples   : 11,451
  ✅ Selected       : 1,050
  ✅ Train          : 1,000
  ✅ Test           : 50

Processing: pubmedqa
  Required train : 500
  Required test  : 25
  Required total : 525
  Valid samples   : 1,000
  ✅ Selected       : 525
  ✅ Train          : 500
  ✅ Test           : 25

======================================================================
 FINAL VALIDATION
======================================================================

Train samples : 10,000
Test samples  : 500
Full samples  : 10,500

TRAIN DISTRIBUTION
--------------------------------------------------
chatdoctor           3,500 / 3,500
icliniq              2,000 / 2,000
medmcqa              1,500 / 1,500
medqa                1,000 / 1,000
meddialog              800 /   800
disease_symptoms       700 /   700
pubmedqa               500 /   500

TEST DISTRIBUTION
--------------------------------------------------
chatdoctor             175 /   175
icliniq                100 /   100
medmcqa                 75 /    75
medqa                   50 /    50
meddialog               40 /    40
disease_symptoms        35 /    35
pubmedqa                25 /    25

TRAIN / TEST OVERLAP
--------------------------------------------------
Duplicate samples: 0
✅ No train/test overlap
✅ Train distribution correct
✅ Test distribution correct
✅ Full dataset contains train + test

======================================================================
 DATASETS SUCCESSFULLY CREATED
======================================================================

Train:
  File    : data/final10\train.csv
  Samples : 10,000

Test:
  File    : data/final10\test.csv
  Samples : 500

Full:
  File    : data/final10\full_dataset.csv
  Samples : 10,500

TRAIN SOURCE DISTRIBUTION
source
chatdoctor          3500
disease_symptoms     700
icliniq             2000
meddialog            800
medmcqa             1500
medqa               1000
pubmedqa             500
Name: count, dtype: int64

TEST SOURCE DISTRIBUTION
source
chatdoctor          175
disease_symptoms     35
icliniq             100
meddialog            40
medmcqa              75
medqa                50
pubmedqa             25
Name: count, dtype: int64

FULL SOURCE DISTRIBUTION
source
chatdoctor          3675
disease_symptoms     735
icliniq             2100
meddialog            840
medmcqa             1575
medqa               1050
pubmedqa             525
Name: count, dtype: int64

======================================================================
 ✅ DATASET READY FOR FINE-TUNING
======================================================================

# %% [markdown]
# <!-- ===== Gradient Header ===== -->
# <p style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#          font-family: 'Montserrat', sans-serif;
#          font-size: 26px;
#          text-align: center;
#          color: #ffffff;
#          padding: 28px 48px;
#          border-radius: 40px;
#          border: none;
#          box-shadow: 0 12px 24px rgba(0,0,0,0.2);
#          letter-spacing: 1.5px;
#          font-weight: 700;
#          text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
#          margin: 10px 0 20px;">
#   🧬 BioMistral-7B Fine‑tuning for Medical QA (5K Samples)
# </p>
# 
# <!-- ===== Meta Badges ===== -->
# <div style="display:flex; gap:12px; flex-wrap:wrap; font-family:'Montserrat',sans-serif; margin: 0 2px 20px;">
#   <span style="background:#f0f4ff; border:1px solid #c7d9ff; color:#1e3a8a;
#                padding:8px 16px; border-radius:999px; font-size:13px; font-weight:500;">
#     👤 <b>Author:</b> Ali Asadullah Shehbaz
#   </span>
#   <span style="background:#eef9f3; border:1px solid #b8e0ce; color:#166534;
#                padding:8px 16px; border-radius:999px; font-size:13px; font-weight:500;">
#     🧠 <b>Project Type:</b> LLM Fine‑tuning (Medical QA)
#   </span>
#   <span style="background:#fef7e0; border:1px solid #fde047; color:#713f12;
#                padding:8px 16px; border-radius:999px; font-size:13px; font-weight:500;">
#     ⏱️ <b>Time:</b> ~1.5–2 hours (GPU P100/T4)
#   </span>
#   <span style="background:#f3e8ff; border:1px solid #d8b4fe; color:#4c1d95;
#                padding:8px 16px; border-radius:999px; font-size:13px; font-weight:500;">
#     📊 <b>Samples:</b> 5,000 (balanced)
#   </span>
# </div>
# 
# <!-- ===== Objective Card ===== -->
# <p style="font-family: 'Montserrat', sans-serif;
#           font-size: 16px;
#           line-height: 1.7;
#           color: #1f2937;
#           background: linear-gradient(120deg, #f9fafc, #ffffff);
#           padding: 18px 22px;
#           border-radius: 20px;
#           border-left: 6px solid #764ba2;
#           box-shadow: 0 4px 14px rgba(0,0,0,0.05);
#           margin: 0 0 18px;">
#   🎯 <b>Objective:</b> Fine‑tune <b>BioMistral‑7B</b> – a biomedical domain‑adapted LLM – on a medical question‑answering dataset (5,000 examples) using <b>QLoRA (4‑bit + LoRA)</b>. Evaluate performance with three gold‑standard metrics: <b>Perplexity</b>, <b>ROUGE</b> (1/2/L) and <b>BERTScore</b>. The goal is to achieve a production‑ready biomedical QA assistant that runs on a single GPU.
# </p>
# 
# <!-- ===== Deliverables Card ===== -->
# <div style="font-family:'Montserrat',sans-serif;
#             background:#ffffff;
#             padding:18px 24px;
#             border-radius:20px;
#             border:1px solid #e9eef5;
#             box-shadow:0 8px 20px rgba(0,0,0,0.06);
#             color:#1e293b;">
#   <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
#     <span style="font-size:22px;">📦</span>
#     <h3 style="margin:0; font-size:18px; font-weight:700; color:#334155;">What You’ll Get from This Notebook</h3>
#   </div>
#   <ul style="margin:8px 0 0 20px; padding:0; line-height:1.8; font-size:15px;">
#     <li>🧬 <b>Fine‑tuned BioMistral‑7B</b> with QLoRA – only 0.1% of parameters trained</li>
#     <li>📈 <b>Full evaluation suite:</b> Perplexity, ROUGE-1/2/L, BERTScore (semantic similarity)</li>
#     <li>⚡ <b>Optimised training:</b> 4‑bit loading, gradient checkpointing, packing – fits in 16GB VRAM</li>
#     <li>💾 <b>Save & push to Hugging Face Hub</b> – ready for inference anywhere</li>
#     <li>🔁 <b>Reusable code structure</b> – easily scale to larger datasets or other Mistral‑based models</li>
#   </ul>
# </div>
# 
# <!-- ===== Quick Tip Visual ===== -->
# <div style="font-family:'Montserrat',sans-serif;
#             background:#fefce8;
#             border-left: 5px solid #eab308;
#             padding: 12px 18px;
#             border-radius: 14px;
#             margin: 20px 0 10px;
#             font-size: 14px;
#             color: #854d0e;">
#   💡 <b>Tip:</b> This notebook is designed to run on <b>Kaggle GPU (P100 or T4)</b>. The entire fine‑tuning takes about 1.5–2 hours for 5,000 samples. You can easily increase <code>NUM_SAMPLES</code> further if you have more time/GPU memory.
# </div>
# 
# <p style="margin-top: 24px; text-align:center; font-family: 'Montserrat'; font-size:14px;">
#   ⬇️ <b>Scroll down</b> – everything is ready: install → load data → QLoRA fine‑tune → evaluate → push to Hub.
# </p>

# %% [markdown]
# <p style="background: linear-gradient(90deg, #fde2e4, #fad2e1); font-family: 'Montserrat', sans-serif; font-size: 22px; text-align: center; color: #1f1f1f; padding: 18px 40px; border-radius: 30px; border: 4px solid #f8ad9d; box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15); letter-spacing: 1px; font-weight: 600; margin-top: 25px;">🧑‍💻 About the Author</p>
# 
# <div style="font-family: 'Montserrat', sans-serif; background: #ffffff; border-radius: 20px; padding: 25px; border: 1px solid #e5e7eb; box-shadow: 0 6px 20px rgba(0,0,0,0.08);">
#   <p>Hi, I’m <strong>Asadullah Shehbaz</strong> — an aspiring Data Scientist passionate about uncovering insights through data. I’m on a journey to master machine learning, analytical thinking, and real-world problem solving, one project at a time.</p>
#   <blockquote style="background: #f1f5f9; border-left: 5px solid #38b000; padding: 12px 16px; font-style: italic; border-radius: 8px;">“I believe community drives innovation — by learning together, we grow faster, think deeper, and build stronger solutions.”</blockquote>
#   <p>Feel free to connect, share feedback, or explore my other notebooks below! 👇</p>
# </div>
# 
# <p style="background: linear-gradient(90deg, #caf0f8, #ade8f4); font-family: 'Montserrat', sans-serif; font-size: 22px; text-align: center; color: #1f1f1f; padding: 18px 40px; border-radius: 30px; border: 4px solid #90e0ef; box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15); letter-spacing: 1px; font-weight: 600; margin-top: 25px;">🌐 Contact & Profiles</p>
# 
# <div style="font-family: 'Montserrat', sans-serif; background: #ffffff; border-radius: 20px; padding: 25px; border: 1px solid #e5e7eb; box-shadow: 0 6px 20px rgba(0,0,0,0.08);">
#   <ul style="list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 12px;">
#     <li><a href="mailto:asadullahcreative@gmail.com" style="background: #f3f4f6; padding: 8px 14px; border-radius: 6px; text-decoration: none; color: #2563eb; font-weight: 600;">📧 Email</a></li>
#     <li><a href="https://www.linkedin.com/in/asadullah-shehbaz-18172a2bb/" target="_blank" style="background: #f3f4f6; padding: 8px 14px; border-radius: 6px; text-decoration: none; color: #2563eb; font-weight: 600;">🔗 LinkedIn</a></li>
#     <li><a href="https://github.com/AsadullahShehbaz" target="_blank" style="background: #f3f4f6; padding: 8px 14px; border-radius: 6px; text-decoration: none; color: #2563eb; font-weight: 600;">💻 GitHub</a></li>
#     <li><a href="https://www.kaggle.com/asadullahcreative" target="_blank" style="background: #f3f4f6; padding: 8px 14px; border-radius: 6px; text-decoration: none; color: #2563eb; font-weight: 600;">🧠 Kaggle</a></li>
#     <li><a href="https://x.com/C786Asadullah" target="_blank" style="background: #f3f4f6; padding: 8px 14px; border-radius: 6px; text-decoration: none; color: #2563eb; font-weight: 600;">🐦 Twitter (X)</a></li>
#   </ul>
# </div>

# %% [markdown]
# # 1.Import Libraries

# %%
%pip install bert_score unsloth

# %%
import os 
import torch
import numpy as np 
import pandas as pd 

from datasets import Dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer,SFTConfig
from rouge_score import rouge_scorer
from bert_score import score as bert_score
from huggingface_hub import login 
from kaggle_secrets import UserSecretsClient

print("All Libraries imported !")

# %%
# !pip install bert_score --quiet

# %%
# !pip show unsloth 
# !pip show transformers
# !pip show torch
# !pip show trl
# !pip show pandas
# !pip show datasets
# !pip show rouge_score
# !pip show bert_score
# !pip show numpy
# !pip show huggingface_hub

# %% [markdown]
# # 2.Configuration

# %%
DATASET_PATH = "/kaggle/input/datasets/asadullahcreative/medicaldata/balanced_medical_dataset.csv"
OUTPUT_DIR   = "/kaggle/working/biomistral-finetuned"
ADAPTER_PATH = "/kaggle/working/biomistral-adapter"
HF_REPO_ID   = "asadullahshehbaz/biomistral-health"   # your HF repo

MODEL_NAME   = "BioMistral/BioMistral-7B"
MAX_SEQ_LEN  = 1024
LORA_R = 16
LORA_ALPHA = 32
BATCH_SIZE = 4
GRAD_ACCUM = 4
EPOCHS = 1
LR = 2e-4  # 0.0002
WARMUP_STEPS = 20
EFFECTIVE_BATCH_SIZE = BATCH_SIZE * GRAD_ACCUM  # = 16
NUM_SAMPLES  = 5000   # only 1K samples
EVAL_SAMPLES = 500     # samples used for ROUGE + BERTScore
print("✅ Config ready!")

# %% [markdown]
# # 3.Login to HuggingFace

# %%
# ─────────────────────────────────────────────
# STEP 3 — LOGIN TO HUGGINGFACE
# ─────────────────────────────────────────────
token = UserSecretsClient().get_secret("token")
login(token=token)
print("✅ Logged in to HuggingFace!")


# %% [markdown]
# # 4.GPU Check

# %%
# ─────────────────────────────────────────────
# STEP 4 — GPU CHECK
# ─────────────────────────────────────────────
if not torch.cuda.is_available():
    raise RuntimeError("❌ No GPU found! Enable GPU in settings.")

for i in range(torch.cuda.device_count()):
    name = torch.cuda.get_device_name(i)
    mem  = torch.cuda.get_device_properties(i).total_memory / 1e9
    print(f"✅ GPU {i}: {name} — {mem:.1f} GB")


# %% [markdown]
# # 5.Load Dataset

# %%
# ─────────────────────────────────────────────
# STEP 5 — LOAD DATASET (1K samples only)
# ─────────────────────────────────────────────
df = pd.read_csv(DATASET_PATH).fillna("")

# Randomly pick 1000 samples
df = df.sample(n=NUM_SAMPLES, random_state=42).reset_index(drop=True)

# 90% train / 10% validation split
split    = int(0.9 * len(df))
train_ds = Dataset.from_pandas(df[:split][["text"]])
val_ds   = Dataset.from_pandas(df[split:][["text"]])

print(f"✅ Train: {len(train_ds)} | Val: {len(val_ds)}")

# %% [markdown]
# 
# # 6.Load Model 

# %%
# ─────────────────────────────────────────────
# STEP 6 — LOAD MODEL + APPLY QLoRA
# ─────────────────────────────────────────────
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name     = MODEL_NAME,
    max_seq_length = MAX_SEQ_LEN,
    dtype          = None,      # auto-detect bfloat16 or float16
    load_in_4bit   = True,      # 4-bit = less VRAM = faster
)

# Add LoRA adapters — only these layers will train
model = FastLanguageModel.get_peft_model(
    model,
    r              = LORA_R,
    lora_alpha     = LORA_ALPHA,
    target_modules = [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout   = 0.05,
    bias           = "none",
    use_gradient_checkpointing = "unsloth",
    random_state   = 42,
)

# Fix padding token
tokenizer.pad_token    = tokenizer.eos_token
tokenizer.pad_token_id = tokenizer.eos_token_id
tokenizer.padding_side = "right"

model.print_trainable_parameters()
print("✅ Model + QLoRA ready!")


# %% [markdown]
# # 7.Train

# %% [markdown]
# ## 7.1 Configuration

# %%
# ─────────────────────────────────────────────
# STEP 7 — TRAIN
# ─────────────────────────────────────────────
config = SFTConfig(
    output_dir                  = OUTPUT_DIR,
    num_train_epochs            = EPOCHS,
    per_device_train_batch_size = BATCH_SIZE,
    gradient_accumulation_steps = GRAD_ACCUM,
    learning_rate               = LR,
    warmup_steps                = WARMUP_STEPS,
    lr_scheduler_type           = "cosine",
    fp16                        = not torch.cuda.is_bf16_supported(),
    bf16                        = torch.cuda.is_bf16_supported(),
    optim                       = "adamw_8bit",
    gradient_checkpointing      = True,
    logging_steps               = 10,
    save_strategy               = "epoch",
    eval_strategy               = "epoch",
    load_best_model_at_end      = True,
    dataset_text_field          = "text",
    max_seq_length              = MAX_SEQ_LEN,
    packing                     = True,   # packs short texts = 2x faster
    report_to                   = "none",
)
print("Configuration Ready !")

# %% [markdown]
# ## 7.2 Trainer Object 

# %%
trainer = SFTTrainer(
    model            = model,
    processing_class = tokenizer,
    args             = config,
    train_dataset    = train_ds,
    eval_dataset     = val_ds,
)


# %% [markdown]
# ## 7.3 Start Training

# %%
print("🔥 Training started...")
trainer.train()
print("✅ Training complete!")


# %% [markdown]
# # 8.Save Adapters

# %%
# ─────────────────────────────────────────────
# STEP 8 — SAVE ADAPTER LOCALLY + PUSH TO HF
# ─────────────────────────────────────────────
model.save_pretrained(ADAPTER_PATH)
tokenizer.save_pretrained(ADAPTER_PATH)
print(f"✅ Adapter saved to {ADAPTER_PATH}")

# Push to HuggingFace Hub
model.push_to_hub(HF_REPO_ID)
tokenizer.push_to_hub(HF_REPO_ID)
print(f"✅ Pushed to huggingface.co/{HF_REPO_ID}")

# %% [markdown]
# # 9.Prepare Model For Evaluation

# %%
# ─────────────────────────────────────────────
# STEP 9 — PREPARE MODEL FOR EVALUATION
# ─────────────────────────────────────────────
FastLanguageModel.for_inference(model)   # enables faster inference
model.eval()

# Helper: parse question and answer from the text column
def parse_qa(text):
    try:
        q = text.split("### Answer:")[0].replace("### Question:", "").strip()
        a = text.split("### Answer:")[1].strip()
        return q, a
    except:
        return None, None

# Helper: generate model answer for a question
def generate_answer(question, max_new_tokens=150):
    prompt = f"### Question:\n{question}\n\n### Answer:\n"
    inputs = tokenizer(
        prompt,
        return_tensors = "pt",
        truncation     = True,
        max_length     = 512
    ).to("cuda")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens     = max_new_tokens,
            max_length=None,
            do_sample          = False,          # greedy = consistent results
            repetition_penalty = 1.1,
            pad_token_id       = tokenizer.eos_token_id
        )

    # Decode only the newly generated tokens
    answer = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens = True
    )
    return answer.strip()

print("✅ Model ready for evaluation!")



# %% [markdown]
# # 10.Perplexity

# %%
# ─────────────────────────────────────────────
# STEP 10 — METRIC 1: PERPLEXITY
# Lower = better | Good: <15 | Acceptable: <50
# ─────────────────────────────────────────────
print("\n" + "="*45)
print("  METRIC 1: PERPLEXITY")
print("="*45)

def get_perplexity(texts, n=50):
    losses = []
    for text in texts[:n]:
        inputs = tokenizer(
            text,
            return_tensors = "pt",
            truncation     = True,
            max_length     = 512
        ).to("cuda")

        with torch.no_grad():
            loss = model(
                **inputs,
                labels = inputs["input_ids"]
            ).loss

        losses.append(loss.item())

    avg_loss   = np.mean(losses)
    perplexity = np.exp(avg_loss)
    return perplexity

# Use the last 100 rows as unseen test text
test_texts = df.tail(100)["text"].tolist()
ppl = get_perplexity(test_texts)

print(f"  Perplexity: {ppl:.2f}")
print(
    "  Verdict: 🟢 EXCELLENT" if ppl < 15 else
    "  Verdict: 🟡 GOOD"      if ppl < 50 else
    "  Verdict: 🟠 ACCEPTABLE" if ppl < 100 else
    "  Verdict: 🔴 POOR"
)


# %% [markdown]
# # 11.Generate Predictions

# %%
# ─────────────────────────────────────────────
# STEP 11 — GENERATE PREDICTIONS (for ROUGE + BERTScore)
# ─────────────────────────────────────────────
print("\n" + "="*45)
print(f"  GENERATING {EVAL_SAMPLES} PREDICTIONS")
print("="*45)

predictions = []
references  = []

test_df = df.tail(EVAL_SAMPLES).reset_index(drop=True)

for i, row in test_df.iterrows():
    q, ref = parse_qa(row["text"])
    if not q:
        continue

    pred = generate_answer(q)
    predictions.append(pred)
    references.append(ref)

    if (i + 1) % 10 == 0:
        print(f"  Generated {i + 1}/{EVAL_SAMPLES}")

print(f"✅ {len(predictions)} predictions ready!")


# %% [markdown]
# # 12.Rouge Score

# %%
# ─────────────────────────────────────────────
# STEP 12 — METRIC 2: ROUGE SCORES
# Range: 0 to 1 | Higher = better
# ROUGE-L > 0.25 is good for medical QA
# ─────────────────────────────────────────────
print("\n" + "="*45)
print("  METRIC 2: ROUGE SCORES")
print("="*45)

scorer     = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
r1, r2, rL = [], [], []

for pred, ref in zip(predictions, references):
    s = scorer.score(ref, pred)
    r1.append(s["rouge1"].fmeasure)
    r2.append(s["rouge2"].fmeasure)
    rL.append(s["rougeL"].fmeasure)

rouge1 = np.mean(r1)
rouge2 = np.mean(r2)
rougeL = np.mean(rL)

print(f"  ROUGE-1: {rouge1:.4f}  ({rouge1*100:.1f}%)")
print(f"  ROUGE-2: {rouge2:.4f}  ({rouge2*100:.1f}%)")
print(f"  ROUGE-L: {rougeL:.4f}  ({rougeL*100:.1f}%)")
print(
    "  Verdict: 🟢 EXCELLENT" if rougeL > 0.35 else
    "  Verdict: 🟡 GOOD"      if rougeL > 0.25 else
    "  Verdict: 🟠 ACCEPTABLE" if rougeL > 0.15 else
    "  Verdict: 🔴 POOR"
)


# %% [markdown]
# # 13.Bert Score

# %%
# ─────────────────────────────────────────────
# STEP 13 — METRIC 3: BERTScore
# Semantic similarity using embeddings
# F1 > 0.83 is good | > 0.88 is excellent
# ─────────────────────────────────────────────
print("\n" + "="*45)
print("  METRIC 3: BERTScore")
print("="*45)

P, R, F1 = bert_score(
    predictions,
    references,
    lang       = "en",
    model_type = "distilbert-base-uncased",   # lightweight & fast
    batch_size = 8,
    verbose    = False
)

bp = P.mean().item()
br = R.mean().item()
bf = F1.mean().item()

print(f"  Precision : {bp:.4f}")
print(f"  Recall    : {br:.4f}")
print(f"  F1 Score  : {bf:.4f}")
print(
    "  Verdict: 🟢 EXCELLENT" if bf > 0.88 else
    "  Verdict: 🟡 GOOD"      if bf > 0.83 else
    "  Verdict: 🟠 ACCEPTABLE" if bf > 0.78 else
    "  Verdict: 🔴 POOR"
)

# %% [markdown]
# # 14.Summary Report

# %%
# ─────────────────────────────────────────────
# STEP 14 — FINAL SUMMARY REPORT
# ─────────────────────────────────────────────
print("\n" + "="*45)
print("  FINAL EVALUATION REPORT")
print("  BioMistral-7B  |  1K Sample Fine-tune")
print("="*45)
print(f"  Perplexity  : {ppl:.2f}       target < 15")
print(f"  ROUGE-1     : {rouge1:.4f}     target > 0.30")
print(f"  ROUGE-2     : {rouge2:.4f}     target > 0.15")
print(f"  ROUGE-L     : {rougeL:.4f}     target > 0.25")
print(f"  BERTScore F1: {bf:.4f}     target > 0.83")
print("="*45)
print("✅ Evaluation complete!")

# %%
print("Completed ")

# %%
# ─────────────────────────────────────────────
# INFERENCE — Load from HuggingFace & Ask Questions
# ─────────────────────────────────────────────

# STEP 1 — Install
!pip install unsloth -q

# STEP 2 — Imports
from unsloth import FastLanguageModel
import torch

# STEP 3 — Load your fine-tuned model from HuggingFace
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name   = "asadullahshehbaz/biomistral-health",  # your HF repo
    max_seq_length = 1024,
    dtype          = None,
    load_in_4bit   = True,
)

# Enable fast inference mode
FastLanguageModel.for_inference(model)
print("✅ Model loaded and ready!")


# STEP 4 — Simple ask function
def ask(question):
    prompt = f"### Question:\n{question}\n\n### Answer:\n"

    inputs = tokenizer(
        prompt,
        return_tensors = "pt",
        truncation     = True,
        max_length     = 512
    ).to("cuda")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens     = 300,
            do_sample          = True,
            temperature        = 0.7,   # 0.1 = focused, 1.0 = creative
            top_p              = 0.9,
            repetition_penalty = 1.1,
            pad_token_id       = tokenizer.eos_token_id,
        )

    # Decode only the new generated tokens (not the prompt)
    answer = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens = True
    )
    return answer.strip()


# STEP 5 — Ask anything!
questions = [
    "What are the symptoms of diabetes?",
    "How is hypertension treated?",
    "What causes a heart attack?",
]

for q in questions:
    print(f"\n{'='*50}")
    print(f"Q: {q}")
    print(f"A: {ask(q)}")
    print(f"{'='*50}")

# %%
import warnings
import transformers
warnings.filterwarnings("ignore")
transformers.logging.set_verbosity_error()

def ask(question):
    prompt = f"### Question:\n{question}\n\n### Answer:\n"

    inputs = tokenizer(
        prompt,
        return_tensors = "pt",
        truncation     = True,
        max_length     = 512
    ).to("cuda")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens     = 150,   # was 300 — prevents rambling
            do_sample          = True,
            temperature        = 0.7,
            top_p              = 0.9,
            repetition_penalty = 1.3,   # was 1.1 — stops repetition
            pad_token_id       = tokenizer.eos_token_id,
            eos_token_id       = tokenizer.eos_token_id,
        )

    answer = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens = True
    ).strip()

    return answer


# Clean print — no warnings in output
for q in questions:
    print(f"\n{'='*50}")
    print(f"Q: {q}")
    print(f"A: {ask(q)}")
    print(f"{'='*50}")

# %%
import warnings
import transformers
warnings.filterwarnings("ignore")
transformers.logging.set_verbosity_error()

def ask(question, length="medium"):
    
    # ── Length instruction injected into prompt ──────
    length_instruction = {
        "short"  : "Answer in 1-2 sentences only.",
        "medium" : "Answer in 3-5 sentences. Be concise and clear.",
        "long"   : "Answer in detail with proper explanation.",
    }

    prompt = f"""You are a helpful medical assistant. {length_instruction[length]}

### Question:
{question}

### Answer:
"""

    inputs = tokenizer(
        prompt,
        return_tensors = "pt",
        truncation     = True,
        max_length     = 512
    ).to("cuda")

    # ── Stop sequences — model stops at these tokens ─
    stop_strings = [
        "### Question:",   # stops if it tries to ask another question
        "### Answer:",     # stops if it tries to answer again
        "References:",     # stops before hallucinated references
        "\n\n\n",          # stops at triple newline
    ]
    stop_ids = [
        tokenizer.encode(s, add_special_tokens=False)[0]
        for s in stop_strings
    ]
    stop_ids.append(tokenizer.eos_token_id)

    # ── Max tokens based on length ────────────────────
    max_tokens = {
        "short"  : 60,
        "medium" : 130,
        "long"   : 300,
    }

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens     = max_tokens[length],
            do_sample          = True,
            temperature        = 0.7,
            top_p              = 0.9,
            repetition_penalty = 1.3,
            pad_token_id       = tokenizer.eos_token_id,
            eos_token_id       = stop_ids,   # stops at ANY of these
        )

    answer = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens = True
    ).strip()

    # ── Post-process: cut at incomplete last sentence ─
    if answer and answer[-1] not in ".!?":
        # trim to last complete sentence
        for punct in reversed(range(len(answer))):
            if answer[punct] in ".!?":
                answer = answer[:punct+1]
                break

    return answer


# ── Test all three lengths ────────────────────────────
questions = [
    "What are the symptoms of diabetes?",
    "How is hypertension treated?",
    "What causes a heart attack?",
]

for q in questions:
    print(f"\n{'='*50}")
    print(f"Q: {q}")
    print(f"\n--- SHORT ---")
    print(ask(q, length="short"))
    print(f"\n--- MEDIUM ---")
    print(ask(q, length="medium"))
    print(f"\n--- LONG ---")
    print(ask(q, length="long"))
    print(f"{'='*50}")




# %% [markdown]
# <p style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
#          font-family: Montserrat, sans-serif;
#          font-size: 32px; text-align: center; color: #ffffff;
#          padding: 40px 48px; border-radius: 40px; border: none;
#          box-shadow: 0 16px 32px rgba(0,0,0,0.3);
#          letter-spacing: 2px; font-weight: 800;
#          text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
#          margin: 10px 0 24px;">
#   🧬 Convert Fine-tuned Model → GGUF Format
# </p>
# 
# <div style="display:flex; gap:12px; flex-wrap:wrap; font-family:Montserrat,sans-serif; margin: 0 2px 24px; justify-content:center;">
#   <span style="background:#f0f4ff; border:1px solid #c7d9ff; color:#1e3a8a; padding:8px 18px; border-radius:999px; font-size:13px; font-weight:500;"> 👤 <b>Author:</b> Ali Asadullah Shehbaz</span>
#   <span style="background:#eef9f3; border:1px solid #b8e0ce; color:#166534; padding:8px 18px; border-radius:999px; font-size:13px; font-weight:500;"> 🧠 <b>Task:</b> Model Conversion & Quantization</span>
#   <span style="background:#fef7e0; border:1px solid #fde047; color:#713f12; padding:8px 18px; border-radius:999px; font-size:13px; font-weight:500;"> ⏱️ <b>Runtime:</b> ~15-25 min</span>
#   <span style="background:#f3e8ff; border:1px solid #d8b4fe; color:#4c1d95; padding:8px 18px; border-radius:999px; font-size:13px; font-weight:500;"> 💾 <b>Output:</b> ~4 GB GGUF file</span>
#   <span style="background:#fce7f3; border:1px solid #f9a8d4; color:#831843; padding:8px 18px; border-radius:999px; font-size:13px; font-weight:500;"> 🎯 <b>Level:</b> Beginner to Intermediate</span>
# </div>
# 
# ---
# 

# %% [markdown]
# <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:18px;
#             padding:26px 30px; text-align:center; margin-top:14px;
#             font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
#   <div style="font-size:15px; font-weight:800; color:#0B3D91; letter-spacing:0.5px; margin-bottom:14px;">
#     🔗 LET'S CONNECT — ASADULLAH AI
#   </div>
#   <div style="display:flex; flex-wrap:wrap; justify-content:center;">
#     <a href="https://www.youtube.com/@aiasadullah" style="text-decoration:none; background:#FF0000; color:white; padding:9px 16px; margin:5px; border-radius:999px; font-size:13px; font-weight:600; display:inline-block;">▶️ YouTube</a>
#     <a href="https://github.com/AsadullahShehbaz" style="text-decoration:none; background:#24292F; color:white; padding:9px 16px; margin:5px; border-radius:999px; font-size:13px; font-weight:600; display:inline-block;">🐙 GitHub</a>
#     <a href="https://www.kaggle.com/asadullahcreative" style="text-decoration:none; background:#20BEFF; color:white; padding:9px 16px; margin:5px; border-radius:999px; font-size:13px; font-weight:600; display:inline-block;">📊 Kaggle</a>
#     <a href="https://www.instagram.com/asadullah_creative" style="text-decoration:none; background:#E4405F; color:white; padding:9px 16px; margin:5px; border-radius:999px; font-size:13px; font-weight:600; display:inline-block;">📸 Instagram</a>
#     <a href="https://web.facebook.com/profile.php?id=61576230402114" style="text-decoration:none; background:#1877F2; color:white; padding:9px 16px; margin:5px; border-radius:999px; font-size:13px; font-weight:600; display:inline-block;">👍 Facebook</a>
#     <a href="https://x.com/asadullahgenai" style="text-decoration:none; background:#111827; color:white; padding:9px 16px; margin:5px; border-radius:999px; font-size:13px; font-weight:600; display:inline-block;">✖️ X</a>
#     <a href="mailto:asadullahcreative@gmail.com" style="text-decoration:none; background:#0B3D91; color:white; padding:9px 16px; margin:5px; border-radius:999px; font-size:13px; font-weight:600; display:inline-block;">✉️ Email</a>
#   </div>
# </div>

# %% [markdown]
# ## Project Overview
# 
# This notebook is the **final step** in an LLM fine-tuning pipeline. We take a fine-tuned model that was
# trained with **QLoRA** (4-bit) and convert it into the **GGUF format** -- the standard format used by
# `llama.cpp` for running LLMs locally on consumer hardware (CPU + limited RAM).
# 
# > **Goal:** Transform a HuggingFace-compatible model into a portable, quantized GGUF file that
# > anyone can download and run on their laptop -- no GPU required.
# 
# ---
# 
# ### End-to-End Workflow
# 
# ```mermaid
# flowchart TD
#     A["Fine-tuned Model (HuggingFace, 4-bit QLoRA)"]
#     B["Load in 4-bit on CPU (save VRAM)"]
#     C["Dequantize to FP16 (restore full precision)"]
#     D["Save FP16 weights (safe_serialization)"]
#     E["Convert to GGUF (llama.cpp convert_hf_to_gguf)"]
#     F["Quantize to Q4_K_M (llama-quantize)"]
#     G["Test Inference (llama-cpp-python)"]
#     H["Upload to HuggingFace Hub"]
#     A --> B --> C --> D --> E --> F --> G --> H
# ```
# 
# ---
# 

# %% [markdown]
# ## What You Will Learn
# 
# By the end of this notebook, you will understand:
# 
# | # | Concept | What you will learn |
# |---|---------|---------------------|
# | 1 | **Model Formats** | Difference between HuggingFace (safetensors) and GGUF formats |
# | 2 | **Dequantization** | How to restore 4-bit quantized weights back to FP16 |
# | 3 | **GGUF Conversion** | How llama.cpp converts HuggingFace models to GGUF |
# | 4 | **Quantization** | How to shrink a model from ~14 GB to ~4 GB with minimal quality loss |
# | 5 | **Local Inference** | How to run a GGUF model on CPU using llama-cpp-python |
# | 6 | **HuggingFace Upload** | How to share your model with the community |
# 
# ### Prerequisites
# 
# Before starting, you should:
# 
# - Know basic Python (imports, variables, function calls)
# - Have a **HuggingFace account** (free) with a **User Access Token**
# - Understand that LLMs are large neural networks that generate text
# - Be curious about how models move from training to production!
# 
# > **No prior knowledge of GGUF, quantization, or llama.cpp is needed** --
# > we explain every concept from scratch.
# 
# ---
# 

# %% [markdown]
# ## Environment & Requirements
# 
# This notebook is designed to run on **Kaggle** with the following specifications:
# 
# | Requirement | Value | Notes |
# |-------------|-------|-------|
# | **GPU** | Not required (CPU mode) | We deliberately avoid GPU to save VRAM |
# | **RAM** | >= 32 GB recommended | FP16 model loading needs ~14 GB |
# | **Disk** | >= 50 GB free | Temporary FP16 weights occupy ~14 GB |
# | **Kaggle Session** | Internet ON, GPU OFF | GPU not needed for conversion |
# | **Time** | ~15-25 minutes | Varies with Kaggle instance speed |
# 
# > **Important:** This notebook uses `/kaggle/tmp` (temporary storage, ~1 TB available)
# > instead of `/kaggle/working` (limited to 20 GB output quota). The FP16 model alone is ~14 GB!
# 
# ---
# 

# %% [markdown]
# ---
# 
# # Step 1: Install Dependencies
# 
# ---
# 
# ## Install Unsloth
# 
# ### What is Unsloth?
# 
# [Unsloth](https://github.com/unslothai/unsloth) is a library that makes fine-tuning LLMs **2x faster**
# and use **50% less memory**. It achieves this through:
# 
# - **Patching** the model attention and linear layers with optimized CUDA kernels
# - **Smart gradient checkpointing** that offloads activations during backpropagation
# - **4-bit QLoRA** integration that loads models in 4-bit precision
# 
# Even though we are not fine-tuning here, Unsloth provides the `FastLanguageModel` class
# which handles model loading, dequantization, and saving with a clean API.
# 
# ### Why `%pip` instead of `!pip`?
# 
# In Jupyter, `%pip` installs packages in the **same Python environment** as the running kernel.
# This avoids the common mistake of installing in one environment and importing from another.
# Always prefer `%pip` over `!pip` in notebooks!
# 
# ### Expected Output
# 
# Progress bars as packages download. Lines like `Successfully installed` indicate success.
# 
# ---
# 

# %%
%pip install unsloth -q


# %% [markdown]
# ---
# 
# # Step 2: Authenticate with HuggingFace Hub
# 
# ---
# 
# ### Why do we need to authenticate?
# 
# HuggingFace Hub hosts millions of models, datasets, and spaces. Many fine-tuned models are
# stored in **private or gated repositories**. To download (or upload) models, HuggingFace
# needs to verify your identity via an **API token**.
# 
# ### How does Kaggle Secrets work?
# 
# `UserSecretsClient()` is Kaggle built-in way to securely store and retrieve API keys.
# Your `HF_TOKEN` is set once in **Add-ons > Secrets** and never exposed in code.
# This is a **best practice** -- never hard-code tokens directly!
# 
# | Method | Security | Best for |
# |--------|----------|----------|
# | `UserSecretsClient` | High (stored in Kaggle) | Kaggle notebooks |
# | Environment variables | Medium | Local development |
# | Hard-coded in script | Never! | Anyone whose repo you can see |
# 
# ### Expected Output
# 
# ```
# Login successful
# Your token has been saved to /root/.cache/huggingface/token
# Login successful as: YourUsername
# ```
# 
# ### Common Issues
# 
# - **"Secret not found"**: You have not created `HF_TOKEN` in Kaggle Secrets.
# - **"Invalid token"**: Your HuggingFace token expired or has wrong permissions.
# - **No internet**: Ensure Kaggle internet is enabled (sidebar > Settings > Internet).
# 
# ---
# 

# %%
from huggingface_hub import login
from kaggle_secrets import UserSecretsClient

hf_token = UserSecretsClient().get_secret("HF_TOKEN")
login(token=hf_token)


# %% [markdown]
# ---
# 
# # Understanding Model Formats
# 
# ---
# 
# Before we start loading and converting, let us understand the different model formats
# we will encounter in this notebook.
# 
# ## Format Comparison
# 
# | Format | Precision | Size (7B model) | Use Case |
# |--------|-----------|-----------------|----------|
# | **4-bit (QLoRA)** | 4-bit integers | ~4 GB | Training / fine-tuning |
# | **FP16** | 16-bit float | ~14 GB | Full precision inference |
# | **GGUF (FP16)** | 16-bit float | ~14 GB | llama.cpp CPU inference |
# | **GGUF (Q4_K_M)** | 4-bit quantized | ~4 GB | Local CPU inference (our target) |
# 
# ### What is FP16?
# 
# **FP16** (Float16 / half-precision) stores each number using **16 bits** (2 bytes).
# A 7-billion-parameter model therefore needs:
# 
# > 7,000,000,000 parameters x 2 bytes = **14 GB**
# 
# This is why we save FP16 weights -- it is the highest precision we can practically handle.
# 
# ### What is GGUF?
# 
# **GGUF** (GPT-Generated Unified Format) is a file format created by the `llama.cpp` project.
# It stores:
# 
# - The model **weights** in a single file
# - The **tokenizer** (vocabulary + merges)
# - **Metadata** (model architecture, context length, etc.)
# 
# Think of GGUF as a **self-contained executable** for the model -- one file that has
# everything needed to run inference.
# 
# ### What is Q4_K_M?
# 
# **Q4_K_M** is a quantization method in the GGUF world:
# 
# - **Q4** = 4-bit quantization (weights stored as 4-bit integers)
# - **K** = K-quant (intelligent quantization that groups weights cleverly)
# - **M** = Medium size variant (balanced quality/size trade-off)
# 
# This is the **recommended default** for most use cases -- good quality at ~4 GB for a 7B model.
# 
# ---
# 

# %% [markdown]
# ---
# 
# # Step 3: Memory Setup & Environment Variables
# 
# ---
# 
# ### Why do we need `expandable_segments`?
# 
# PyTorch CUDA memory allocator manages GPU memory in **segments**. By default,
# it allocates fixed-size blocks. The `expandable_segments:True` option lets the allocator
# **grow segments dynamically** as needed.
# 
# ### Why load the model on CPU?
# 
# This is a critical optimization! Our fine-tuned model was trained on a **Tesla T4 with 16 GB VRAM**.
# If we load the model on GPU, it would consume that VRAM and leave no room for
# dequantization (which doubles memory usage temporarily).
# 
# By setting `device_map = {"": "cpu"}`, we force the model entirely into **system RAM**:
# 
# | Load Location | VRAM Used | RAM Used | Can we dequantize? |
# |--------------|-----------|---------|--------------------|
# | GPU (default) | ~8 GB | ~0 GB | Runs out of VRAM |
# | CPU (our choice) | ~0 GB | ~8 GB | Yes, plenty of RAM |
# 
# Kaggle instances typically have **32-64 GB RAM**, so CPU loading is the smart move here.
# 
# ---
# 

# %%
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# %%

from unsloth import FastLanguageModel
import torch, gc

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name     = "asadullahshehbaz/biomistral-health-merged",
    max_seq_length = 2048,
    load_in_4bit   = True,
    device_map     = {"": "cpu"},   # force everything onto CPU/RAM, not the 14.56GB T4
)


# %% [markdown]
# ---
# 
# # Step 4: Dequantize the Model (4-bit to FP16)
# 
# ---
# 
# ### What is Dequantization?
# 
# Imagine you took a high-resolution photo (FP32) and compressed it into a tiny JPEG (4-bit).
# **Dequantization** is like expanding that JPEG back to full resolution -- you recover
# the original quality (well, almost!).
# 
# In technical terms:
# 
# 1. **During QLoRA training**, the model weights were stored as **4-bit integers** to save memory
# 2. Each 4-bit value maps to a 16-bit float using a **scale factor** and **zero point**
# 3. **Dequantization** reverses this: `float16_value = scale x (int4_value - zero_point)`
# 4. The result is a full **FP16 model** that can be converted to GGUF
# 
# ### Memory During Dequantization
# 
# | Stage | Memory Used | Location |
# |-------|-------------|----------|
# | Before dequantization | ~4 GB (4-bit) | CPU RAM |
# | During dequantization | ~18 GB (4-bit + FP16) | CPU RAM (peak) |
# | After dequantization | ~14 GB (FP16) | CPU RAM |
# 
# > This is exactly why we load on CPU -- GPU VRAM cannot handle the peak memory!
# 
# ### Expected Output
# 
# ```
# The modules are dequantized in torch.float16 and casted to torch.float16.
# ```
# 
# This confirms your 4-bit model has been successfully restored to full FP16 precision.
# 
# ---
# 

# %%
gc.collect()
model = model.dequantize()   # now happens in system RAM, not VRAM


# %% [markdown]
# ---
# 
# # Step 5: Save FP16 Model to Disk
# 
# ---
# 
# ### Why save FP16 first?
# 
# The GGUF conversion tool (`convert_hf_to_gguf.py`) expects models in **HuggingFace format** --
# a directory containing:
# 
# - `model.safetensors` (the actual weights)
# - `config.json` (model architecture settings)
# - `tokenizer.json` / `tokenizer_config.json` (the tokenizer)
# 
# Since our model is currently loaded in memory, we need to **serialize** it to disk first.
# 
# ### What is safe_serialization?
# 
# By default, HuggingFace saved models as `pytorch_model.bin` (Python pickle format).
# But pickle files can execute arbitrary code when loaded!
# 
# **Safe serialization** uses the `.safetensors` format instead:
# 
# | Format | Extension | Safe? | Speed |
# |--------|-----------|-------|-------|
# | Pickle | `.bin` | Can contain malware | Slow |
# | Safetensors | `.safetensors` | No code execution | Fast |
# 
# Always use `safe_serialization=True` -- it is the HuggingFace-recommended best practice.
# 
# ### Why `/kaggle/tmp` and not `/kaggle/working`?
# 
# Kaggle only allows **20 GB** of output in `/kaggle/working`. An FP16 7B model is ~14 GB.
# By using `/kaggle/tmp` (temporary scratch space, ~1 TB), we avoid hitting this quota.
# 
# > **However:** `/kaggle/tmp` files are **deleted when the session ends**. You must upload to
# > HuggingFace before the session expires if you want to keep your work!
# 
# ---
# 

# %%
# Save to /kaggle/tmp, NOT /kaggle/working -- Kaggle output quota is 20GB
# and a merged fp16 7B model alone is ~14GB
model.save_pretrained("/kaggle/tmp/merged_fp16", safe_serialization=True, save_original_format=False)
tokenizer.save_pretrained("/kaggle/tmp/merged_fp16")


# %% [markdown]
# ---
# 
# # Step 6: Verify Saved Files
# 
# ---
# 
# ### What should we see?
# 
# After saving, we should see a directory with:
# 
# | File | Size | Purpose |
# |------|------|---------|
# | `model.safetensors` | ~14 GB | The actual model weights (FP16) |
# | `config.json` | ~700 B | Model architecture configuration |
# | `tokenizer.json` | ~3.5 MB | The tokenizer vocabulary |
# | `tokenizer_config.json` | ~1 KB | Tokenizer settings |
# | `tokenizer.model` | ~500 KB | SentencePiece model file |
# | `generation_config.json` | ~150 B | Generation parameters |
# | `chat_template.jinja` | ~500 B | Chat template for conversational models |
# 
# The most important file is `model.safetensors` -- it contains all 7 billion parameters!
# 
# ### How to verify success
# 
# 1. The file `model.safetensors` exists and is ~14 GB
# 2. All configuration files are present
# 3. No error messages in the output
# 
# ---
# 

# %%
!ls -la /kaggle/tmp/merged_fp16


# %% [markdown]
# ---
# 
# # Step 7: Check Available Disk Space
# 
# ---
# 
# ### Why check disk space?
# 
# We are about to:
# 
# 1. Clone the entire `llama.cpp` repository (~500 MB)
# 2. Create an FP16 GGUF file (~14 GB)
# 3. Create a Q4_K_M GGUF file (~4 GB)
# 
# That is ~20 GB of additional data! We need to make sure `/kaggle/tmp` has enough space.
# 
# > **Tip:** Kaggle `/kaggle/tmp` typically has ~1 TB of space, so this is usually fine.
# > But checking never hurts -- especially if you are on a shared instance.
# 
# ### Expected Output
# 
# The key number is **Avail** (available space). As long as it is > 30 GB, we are good.
# 
# ---
# 

# %%
!df -h /kaggle/tmp


# %% [markdown]
# ---
# 
# # Step 8: Convert HuggingFace Model to GGUF Format
# 
# ---
# 
# ### What is llama.cpp?
# 
# [llama.cpp](https://github.com/ggml-org/llama.cpp) is an open-source C++ library that runs LLMs
# efficiently on **CPUs** (and GPUs too). It is the go-to solution for:
# 
# - Running LLMs on laptops without dedicated GPUs
# - Running on Raspberry Pi, phones, and edge devices
# - Quantizing models to reduce their size
# 
# The `convert_hf_to_gguf.py` script is like a **translator** -- it reads a HuggingFace model
# directory and writes a single GGUF file.
# 
# ### What happens during conversion?
# 
# The script:
# 1. Reads each weight tensor from the `.safetensors` files
# 2. Maps them to GGUF internal tensor names
# 3. Copies the configuration (architecture, hyperparameters)
# 4. Serializes everything into a single binary file
# 
# ### Expected Output
# 
# You will see informational messages as each layer is processed.
# The final line should confirm the output file was created.
# 
# > **Tip:** The `--depth 1` flag in git clone only fetches the latest commit,
# > saving bandwidth and disk space. The `-q` flag on pip suppresses verbose output.
# 
# ---
# 

# %%
!git clone --depth 1 https://github.com/ggml-org/llama.cpp
!pip install -r llama.cpp/requirements.txt -q

!python llama.cpp/convert_hf_to_gguf.py /kaggle/tmp/merged_fp16 \
  --outfile /kaggle/tmp/biomistral-f16.gguf --outtype f16


# %% [markdown]
# ---
# 
# # Step 9: Build llama-quantize & Quantize to Q4_K_M
# 
# ---
# 
# ### What is llama-quantize?
# 
# `llama-quantize` is a C++ tool from the llama.cpp project that takes an FP16 GGUF file
# and produces a **quantized** GGUF file at a lower precision.
# 
# Think of it like **compressing a ZIP file** -- the information is preserved, but stored
# more efficiently. The trade-off is:
# 
# | Quantization | Size (7B model) | Quality Loss | Use Case |
# |--------------|-----------------|--------------|----------|
# | None (FP16) | ~14 GB | None | Maximum accuracy |
# | Q8_0 | ~7 GB | Minimal | Balanced quality |
# | **Q4_K_M** | **~4 GB** | **Small** | **Best general purpose** |
# | Q4_0 | ~3.5 GB | Moderate | Memory-constrained devices |
# | Q2_K | ~2.5 GB | Significant | Extreme compression |
# 
# **Q4_K_M is the recommended default** for most users -- it offers the best balance of
# file size and quality preservation.
# 
# ### Why build from source?
# 
# The `llama-quantize` tool needs to be compiled for your specific CPU architecture.
# We use CMake to build it:
# 
# - `cmake -S llama.cpp -B llama.cpp/build` configures the build
# - `-DGGML_CUDA=OFF` disables CUDA (we are on CPU)
# - `-j4` uses 4 CPU cores for faster compilation
# 
# After quantization, we **delete the FP16 GGUF file** (~14 GB) to free space.
# We do not need it anymore -- Q4_K_M is our final deliverable.
# 
# ---
# 

# %% [markdown]
# ### 🔧 Understanding the Two CMake Commands
# 
# Before we run the quantization, let's understand the two CMake commands that build the `llama-quantize` tool from source:
# 
# ---
# 
# #### Command 1: `cmake -S llama.cpp -B llama.cpp/build -DGGML_CUDA=OFF`
# 
# **What is CMake?**
# 
# CMake is a **build system generator**. It doesn't compile code directly — instead, it reads a `CMakeLists.txt` file and generates the instructions (Makefiles) that the actual C++ compiler (g++) follows. Think of CMake as the **architect** who draws up blueprints, and the compiler as the **construction crew** who follows them.
# 
# | Flag | Meaning | Why we set it |
# |------|---------|---------------|
# | `-S llama.cpp` | **Source directory** — where the code lives | The `llama.cpp/` folder we cloned earlier |
# | `-B llama.cpp/build` | **Build directory** — where compiled files go | Keeps build artifacts separate from source (clean practice) |
# | `-DGGML_CUDA=OFF` | **Define** a CMake variable = OFF | Disables GPU support since we're on CPU only |
# 
# When you run this, CMake:
# 1. Reads `llama.cpp/CMakeLists.txt`
# 2. Detects your C++ compiler (g++ / clang)
# 3. Checks for dependencies (OpenMP for parallel processing, pthreads, etc.)
# 4. Generates Makefiles inside `llama.cpp/build/`
# 5. Respects `GGML_CUDA=OFF` → skips all GPU code paths
# 
# > 💡 **Why `-DGGML_CUDA=OFF`?** If we left CUDA enabled, CMake would try to find NVIDIA's CUDA toolkit and compile GPU kernels — making the build slower and the binary larger. Since we're quantizing on CPU, we disable it for a faster, leaner build.
# 
# #### Command 2: `cmake --build llama.cpp/build --target llama-quantize -j4`
# 
# This **actually compiles the code** — the construction crew follows the blueprints from command 1.
# 
# | Flag | Meaning |
# |------|---------|
# | `--build llama.cpp/build` | "Look in this directory for the build system we just configured" |
# | `--target llama-quantize` | **Only compile this one tool**, not everything in llama.cpp (saves minutes!) |
# | `-j4` | Use **4 CPU cores** in parallel (instead of 1) |
# 
# > 🚀 **Why `--target llama-quantize`?** llama.cpp has 20+ tools (llama-cli, llama-server, llama-bench, etc.). Building only the one we need saves significant time.
# 
# > 🚀 **Why `-j4`?** Without it, only 1 CPU core works while the other 3 sit idle. With `-j4`, all 4 cores share the work — the build finishes ~4× faster.
# 
# #### What is `llama-quantize`?
# 
# It's a C++ program (`llama.cpp/examples/quantize/quantize.cpp`) that:
# 1. Opens the FP16 GGUF file (~14 GB)
# 2. Reads every weight tensor
# 3. Quantizes each tensor from 16-bit floats → 4-bit integers (with smart grouping)
# 4. Writes a new GGUF file with the quantized weights (~4 GB)
# 
# #### Why Not Just `pip install`?
# 
# You might wonder: "Why go through this CMake build instead of `pip install llama-cpp-python`?"
# 
# | Tool | Distribution | Purpose |
# |------|-------------|---------|
# | `llama-cpp-python` | `pip install` | **Run** GGUF models (inference) |
# | `llama-quantize` | Build from source | **Create** quantized GGUF models |
# 
# Both are needed — one to **produce** the quantized model, the other to **use** it.
# 
# ---
# 
# #### Expected Output
# 
# You'll see compilation messages like:
# ```
# [ 10%] Building CXX object CMakeFiles/llama-quantize.dir/examples/quantize/quantize.cpp.o
# [ 40%] Building CXX object ...
# [100%] Linking CXX executable bin/llama-quantize
# ```
# 
# The final line confirms success — a binary was created at `llama.cpp/build/bin/llama-quantize`.

# %%
!cmake -S llama.cpp -B llama.cpp/build -DGGML_CUDA=OFF
!cmake --build llama.cpp/build --target llama-quantize -j4

!./llama.cpp/build/bin/llama-quantize \
  /kaggle/tmp/biomistral-f16.gguf \
  /kaggle/working/biomistral-Q4_K_M.gguf \
  Q4_K_M

# free the big f16 intermediate immediately
!rm /kaggle/tmp/biomistral-f16.gguf


# %% [markdown]
# ---
# 
# # Step 10: Verify Quantized GGUF File
# 
# ---
# 
# ### What should we check?
# 
# After quantization, we verify:
# 
# 1. **File exists** -- the file was created successfully
# 2. **File size** -- should be ~4 GB for a Q4_K_M 7B model
# 3. **File not corrupted** -- a quick `ls -lh` confirms the file is the expected size
# 
# > **Tip:** A file much smaller than expected (e.g., 1 GB) indicates something went wrong
# > during quantization. A file close to 4 GB is a good sign!
# 
# ---
# 

# %%
!ls -lh /kaggle/working/biomistral-Q4_K_M.gguf


# %% [markdown]
# ---
# 
# # Step 11: Test GGUF Inference
# 
# ---
# 
# ### What is llama-cpp-python?
# 
# [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) is a Python wrapper around
# the `llama.cpp` library. It provides a simple Python API for loading GGUF files and running
# inference -- without needing to write any C++ code.
# 
# ```python
# from llama_cpp import Llama
# llm = Llama(model_path="model.gguf")
# output = llm("Your prompt here")
# ```
# 
# ### What do the parameters mean?
# 
# | Parameter | Value | Meaning |
# |-----------|-------|---------|
# | `model_path` | `biomistral-Q4_K_M.gguf` | Path to our quantized model |
# | `n_ctx` | `2048` | Context window (how many tokens the model can "remember") |
# | `n_threads` | `4` | CPU threads for parallel computation |
# | `n_gpu_layers` | `0` | Layers offloaded to GPU (0 = CPU only) |
# 
# > **Performance Tip:** Setting `n_gpu_layers > 0` can speed up inference if you have a GPU,
# > but our goal is pure CPU inference -- this is what most users will do locally.
# 
# ---
# 

# %%
!pip install llama-cpp-python -q

from llama_cpp import Llama

llm = Llama(
    model_path = "/kaggle/working/biomistral-Q4_K_M.gguf",
    n_ctx = 2048,
    n_threads = 4,
    n_gpu_layers = 0,   # simulate your local CPU-only setup
)

output = llm("What are the symptoms of type 2 diabetes?", max_tokens=200)
print(output["choices"][0]["text"])


# %% [markdown]
# ---
# 
# ## Understanding the Inference Output
# 
# ---
# 
# ### What did we just see?
# 
# The model generated a response to a medical question **entirely on CPU** using a ~4 GB file.
# This is remarkable because:
# 
# - The original FP16 model is 14 GB -- too large for most laptops
# - Q4_K_M compressed it to **28% of the original size**
# - Quality is preserved well enough for practical use
# 
# ### Interpreting the Response
# 
# | Aspect | What to look for |
# |--------|------------------|
# | **Relevance** | Does the answer address the question? |
# | **Accuracy** | Is the medical information correct? |
# | **Fluency** | Does the text read naturally? |
# | **Hallucination** | Does it invent facts not in its training? |
# 
# > **Important:** All LLMs can hallucinate. This is a demonstration of the conversion
# > pipeline -- always verify medical information from authoritative sources!
# 
# ### How to verify success
# 
# 1. The model loaded without errors
# 2. The output is coherent English text
# 3. The response is relevant to the medical question asked
# 
# ---
# 

# %% [markdown]
# ---
# 
# # Step 12: Upload GGUF to HuggingFace Hub
# 
# ---
# 
# ### Why upload to HuggingFace?
# 
# Uploading your GGUF model to HuggingFace Hub:
# 
# 1. **Preserves your work** -- Kaggle `/kaggle/working` is temporary
# 2. **Shares with the community** -- others can download and use your model
# 3. **Enables easy distribution** -- anyone can `pip install llama-cpp-python` and use it
# 4. **Version control** -- each upload creates a commit you can revert to
# 
# ### What is HfApi?
# 
# `HfApi` is HuggingFace programmatic API client. It lets you:
# 
# - Create repositories (like `git init`)
# - Upload files (like `git push`)
# - Download files, manage versions, and more
# 
# ### Step-by-step:
# 
# 1. **Check if repo exists** -- `api.create_repo(exist_ok=True)` creates it if needed
# 2. **Upload the file** -- `api.upload_file()` sends the GGUF file to the Hub
# 
# ### Expected Output
# 
# You will receive a **commit URL** -- click it to see your model on HuggingFace!
# 
# > **Tip:** Your model will be available at:
# > `https://huggingface.co/asadullahshehbaz/biomistral-health-gguf`
# 
# ---
# 

# %%
from huggingface_hub import HfApi
api = HfApi()
api.create_repo("asadullahshehbaz/biomistral-health-gguf", exist_ok=True)
api.upload_file(
    path_or_fileobj = "/kaggle/working/biomistral-Q4_K_M.gguf",
    path_in_repo    = "biomistral-Q4_K_M.gguf",
    repo_id         = "asadullahshehbaz/biomistral-health-gguf",
)


# %% [markdown]
# ---
# 
# # Bonus: How to Use This Model on Your Own Machine
# 
# ---
# 
# Once uploaded, anyone can download and run your model with just a few lines of code:
# 
# ```python
# # pip install llama-cpp-python
# 
# from llama_cpp import Llama
# 
# llm = Llama.from_pretrained(
#     repo_id="asadullahshehbaz/biomistral-health-gguf",
#     filename="biomistral-Q4_K_M.gguf",
# )
# 
# output = llm("What are the symptoms of type 2 diabetes?", max_tokens=200)
# print(output["choices"][0]["text"])
# ```
# 
# That is it! No GPU, no PyTorch, no transformers library -- just a single file and one
# Python package. This is the **beauty of the GGUF format**: extreme portability.
# 
# ---
# 

# %% [markdown]
# ---
# 
# # Conclusion & Key Takeaways
# 
# ---
# 
# ## What We Accomplished
# 
# We successfully converted a fine-tuned 7B LLM from HuggingFace format to GGUF and
# quantized it for local CPU inference:
# 
# | Step | What happened | Result |
# |------|---------------|--------|
# | Load | 4-bit model loaded from HuggingFace Hub | ~4 GB in CPU RAM |
# | Dequantize | 4-bit weights restored to FP16 | Full precision recovered |
# | Save FP16 | Weights saved as safetensors | ~14 GB on disk |
# | Convert GGUF | HuggingFace to GGUF format | FP16 GGUF file |
# | Quantize | FP16 to Q4_K_M (4-bit) | **~4 GB final file** |
# | Test | Load with llama-cpp-python, run inference | Coherent medical answers |
# | Upload | Push to HuggingFace Hub | Available for everyone |
# 
# ## Key Concepts Learned
# 
# 1. **Model Formats** -- HuggingFace (safetensors) vs GGUF (single-file binary)
# 2. **Quantization** -- Storing weights in fewer bits to save space (4-bit vs 16-bit)
# 3. **Dequantization** -- Restoring quantized weights to full precision
# 4. **Q4_K_M** -- The recommended quantization for balanced quality/size
# 5. **llama.cpp ecosystem** -- Convert, quantize, and run models locally
# 6. **CPU Inference** -- Running LLMs without a GPU is practical with GGUF
# 
# ## Final File Sizes
# 
# | File | Size | Format | Purpose |
# |------|------|--------|---------|
# | `model.safetensors` | ~14 GB | FP16 | HuggingFace format (temporary) |
# | `biomistral-f16.gguf` | ~14 GB | GGUF FP16 | Intermediate (deleted) |
# | `biomistral-Q4_K_M.gguf` | **~4 GB** | GGUF Q4_K_M | Final deliverable |
# 
# That is a **71% size reduction** -- from 14 GB to 4 GB -- with minimal quality degradation!
# 
# ---
# 

# %% [markdown]
# ---
# 
# # Where to Go From Here
# 
# ---
# 
# ## Ideas for Extension
# 
# 1. **Build a Web App** -- Use Gradio or Streamlit to create a UI for your model
# 2. **Comparison Benchmarks** -- Evaluate Q4_K_M vs Q8_0 vs FP16 on quality benchmarks
# 3. **Fine-tune a Different Model** -- Try Llama 3, Mistral, or Phi-3 with the same pipeline
# 4. **Add RAG** -- Combine your model with a vector database for retrieval-augmented generation
# 5. **Deploy as API** -- Use llama.cpp built-in HTTP server for API access
# 
# ## Useful Resources
# 
# | Resource | URL | Description |
# |----------|-----|-------------|
# | HuggingFace Hub | huggingface.co | Model repository |
# | llama.cpp | github.com/ggml-org/llama.cpp | C++ LLM inference |
# | llama-cpp-python | github.com/abetlen/llama-cpp-python | Python bindings |
# | Unsloth | github.com/unslothai/unsloth | Fast fine-tuning |
# | GGUF Docs | github.com/ggml-org/ggml | GGUF specification |
# | QLoRA Paper | arxiv.org/abs/2305.14314 | Original QLoRA research |
# 
# ---
# 
# ## Thank You!
# 
# If you found this notebook helpful, please:
# 
# - Upvote it on Kaggle
# - Star the related repositories on GitHub
# - Share it with fellow ML enthusiasts
# - Leave feedback in the comments!
# 
# > "The best way to learn is to teach. If you can explain this pipeline to someone else,
# > you truly understand it."
# 
# ---
# 


# %% [markdown]
# # 1.Import Libraries

# %%
!pip install -q sentence-transformers \
                datasets \
                qdrant-client \
                langchain \
                langchain-community \
                pypdf \
                requests

# %%
import os
import json
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)

# Use lightweight embedding model
# all-MiniLM-L6-v2 = 90MB only, 384 dim
# Fast on CPU, good quality
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM   = 384

embedder = SentenceTransformer(EMBED_MODEL)
print(f"✅ Embedder loaded: {EMBED_MODEL}")

# %% [markdown]
# # Collect RAG Knowledge Sources

# %%
# ── Collect RAG Knowledge Sources ──────────────────

all_documents = []

# Source 1 — Disease Symptoms (already have this)
print("Loading disease symptoms...")
ds = load_dataset("QuyenAnhDE/Diseases_Symptoms")
print(f"✅ Source 1 loaded")
print(ds)

# %%
for row in ds['train']:
    name = str(row.get('Name','')).strip() 
    symptoms = str(row.get('Symptoms','')).strip()
    treats = str(row.get('Treatments','')).strip()

    if name and symptoms:
        all_documents.append({
            "text":f"Disease : {name}\n Symptoms : {symptoms}\n Treatments : {treats}",
            "source":"disease_db",
            "category":"disease",
            "disease":name.lower()
        }) 
print(f"Disease Loaded : {len(all_documents)}")

# %%
# Source 3 — PubMedQA research findings
print("Loading PubMedQA...")
pubmed = load_dataset(
    "qiaojin/PubMedQA", "pqa_labeled",
    trust_remote_code=True
)
for row in pubmed['train'].select(range(500)):
    q      = str(row['question']).strip()
    answer = str(row['long_answer']).strip()
    all_documents.append({
        "text": f"Research Finding:\n{q}\nConclusion: {answer}",
        "source": "pubmed",
        "category": "research",
        "disease": "general"
    })
print(f"✅ Total after PubMed: {len(all_documents)}")



# %%
 # — ChatDoctor as knowledge base
print("Loading ChatDoctor knowledge...")
chat = load_dataset("lavita/ChatDoctor-HealthCareMagic-100k")
for row in chat['train'].select(range(5000)):
    inp = str(row.get('input','')).strip()
    out = str(row.get('output','')).strip()
    if len(inp) > 30 and len(out) > 50:
        all_documents.append({
            "text": f"Patient Case:\n{inp}\nDoctor Response:\n{out}",
            "source": "chatdoctor",
            "category": "consultation",
            "disease": "general"
        })

print(f"✅ Total documents: {len(all_documents)}")

# %% [markdown]
# # Generate Embeddings

# %%
# ── Generate Embeddings ────────────────────────────
print("\nGenerating embeddings...")
print("This takes 10-20 minutes on Kaggle CPU...")

texts = [doc['text'] for doc in all_documents]

# Batch encode for speed
embeddings = embedder.encode(
    texts,
    batch_size    = 64,
    show_progress_bar = True,
    normalize_embeddings = True  # important for cosine
)

print(f"✅ Embeddings shape: {embeddings.shape}")
# ── Save as JSON for export to local Qdrant ────────
print("\nSaving for export...")

export_data = []
for i, (doc, emb) in enumerate(
    zip(all_documents, embeddings)
):
    export_data.append({
        "id":      i + 1,
        "vector":  emb.tolist(),
        "payload": doc
    }) 

# Save in chunks to avoid memory issues
CHUNK_SIZE = 2000
for chunk_idx in range(
    0, len(export_data), CHUNK_SIZE
):
    chunk = export_data[chunk_idx:chunk_idx+CHUNK_SIZE]
    fname = f"rag_vectors_{chunk_idx//CHUNK_SIZE}.json"
    with open(fname, 'w') as f:
        json.dump(chunk, f)
    print(f"✅ Saved {fname}: {len(chunk)} vectors")

print(f"\nTotal chunks: {len(export_data)//CHUNK_SIZE+1}")
print("Download all rag_vectors_*.json files")

# %% [markdown]
# # Data Ingestion 

# %%
import os

for root, dirs, files in os.walk("/kaggle/working"):
    for file in files:
        if file.endswith(".json"):
            print(os.path.join(root, file))

# %%
import os

for file in os.listdir("/kaggle/working"):
    print(file)

# %%
import glob

vector_files = sorted(
    glob.glob("/kaggle/working/rag_vectors_*.json")
)
vector_files

# %%
# !pip install qdrant-client

# %%
from kaggle_secrets import UserSecretsClient

secrets = UserSecretsClient()

# QDRANT_URL = secrets.get_secret("QDRANT_URL")
# QDRANT_API_KEY = secrets.get_secret("QDRANT_API_KEY")

# %%
import json
import glob
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)

# ----------------------------------------------------
# Connect to the local Qdrant vector database
# ----------------------------------------------------
client = QdrantClient(
    url="https://f9abfea8-7fcd-45b5-9553-5573f66fb8e7.eu-west-1-0.aws.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6YjIwNzdlNjAtZDllOC00ZTVjLTlmODgtMWUxMmNhNWRlNzlhIn0.BIBaGGHcU84spCs_lIyXT-DVk_0qPA_jDXRY408j0Bw",
)

print("✅ Connected to Qdrant Cloud")


# %%
# ----------------------------------------------------
# Collection configuration
# COLLECTION : Name of the vector collection
# EMBED_DIM  : Dimension of embedding vectors
# ----------------------------------------------------
COLLECTION = "health_knowledge"
EMBED_DIM = 384

# ----------------------------------------------------
# Delete the collection if it already exists
# This ensures a fresh import every time the script runs
# ----------------------------------------------------
try:
    client.delete_collection(COLLECTION)
    print("Deleted existing collection")
except:
    # Ignore the error if the collection does not exist
    pass

# ----------------------------------------------------
# Create a new collection with cosine similarity
# ----------------------------------------------------
client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(
        size=EMBED_DIM,
        distance=Distance.COSINE
    )
)

print(f"✅ Collection created: {COLLECTION}")

# %%
# ----------------------------------------------------
# Find all JSON vector files
# Example:
# D:/rag_vectors_1.json
# D:/rag_vectors_2.json
# ...
# ----------------------------------------------------
vector_files = sorted(
    glob.glob("/kaggle/working/rag_vectors_*.json")
)

print(f"\nFound {len(vector_files)} vector files")

# %%


# Counter to track total imported vectors
total_imported = 0

# ----------------------------------------------------
# Read each JSON file and import vectors into Qdrant
# ----------------------------------------------------
for fpath in vector_files:

    # Open current JSON file
    with open(fpath, "r") as f:
        chunk = json.load(f)

    # ------------------------------------------------
    # Convert every JSON object into a Qdrant Point
    # Each point contains:
    #   - id
    #   - embedding vector
    #   - metadata (payload)
    # ------------------------------------------------
    points = [
        PointStruct(
            id=item["id"],
            vector=item["vector"],
            payload=item["payload"]
        )
        for item in chunk
    ]

    # ------------------------------------------------
    # Upload vectors in batches of 100
    # Batching reduces memory usage and improves speed
    # ------------------------------------------------
    for i in range(0, len(points), 100):

        # Select current batch
        batch = points[i:i + 100]

        # Insert or update vectors in Qdrant
        client.upsert(
            collection_name=COLLECTION,
            points=batch
        )

    # Update total imported count
    total_imported += len(points)

    print(f"✅ {fpath}: {len(points)} vectors imported")



# %%
# ----------------------------------------------------
# Print total vectors imported into the collection
# ----------------------------------------------------
print(f"\n✅ Total imported: {total_imported:,} vectors")

# ----------------------------------------------------
# Verify import by checking collection statistics
# ----------------------------------------------------
info = client.get_collection(COLLECTION)

print(
    f"✅ Qdrant collection size: "
    f"{info.points_count:,} points"
) 


