=============================================
  FINAL EVALUATION REPORT
  BioMistral-7B Using Unsloth |  10K Sample Fine-tune
=============================================
  Perplexity  : 5.69       target < 15
  ROUGE-1     : 0.2771     target > 0.30
  ROUGE-2     : 0.0942     target > 0.15
  ROUGE-L     : 0.1833     target > 0.25
  BERTScore F1: 0.7809     target > 0.83
=============================================

Perplexity , ROUGE-1 , ROUGE-2 , ROUGE-3,ROUGE-L,BERTScore F1

# Kaggle Packages to train model 

unsloth==2026.4.8
transformers==5.5.0
torch==2.10.0+cu128
trl==0.24.0
pandas== 2.3.3
datasets==4.3.0
rouge_score==0.1.2
bert_score==0.3.13
numpy==2.0.2
huggingface_hub==1.13.0