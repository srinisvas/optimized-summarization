import os
import pandas as pd
from bert_score import score

# Ensure bert-score is installed
!pip install -q bert-score

# --- 1. File Identification ---

def identify_summary_file_pairs_modified(ref_dir, res_dir, max_pairs=100):
    ref_files_full_paths = [os.path.join(ref_dir, f) for f in os.listdir(ref_dir) if os.path.isfile(os.path.join(ref_dir, f)) and not f.endswith('.gitkeep')]
    res_files_full_paths = [os.path.join(res_dir, f) for f in os.listdir(res_dir) if os.path.isfile(os.path.join(res_dir, f)) and not f.endswith('.gitkeep')]

    result_basenames = {os.path.splitext(os.path.basename(f))[0] for f in res_files_full_paths}

    file_pairs = []
    for ref_file_path in ref_files_full_paths:
        if len(file_pairs) >= max_pairs:
            break

        ref_basename = os.path.splitext(os.path.basename(ref_file_path))[0]

        if ref_basename in result_basenames:
            corresponding_res_file = next((f for f in res_files_full_paths if os.path.splitext(os.path.basename(f))[0] == ref_basename), None)
            if corresponding_res_file:
                file_pairs.append((ref_file_path, corresponding_res_file))
    return file_pairs

# Define the directories
reference_directory = '/content/optimized-summarization/optimized-summarization/Reference-Summary'
result_directory = '/content/optimized-summarization/optimized-summarization/LLM_Summaries_3B'

# Identify file pairs
identified_file_pairs = identify_summary_file_pairs_modified(reference_directory, result_directory)
print(f"Found {len(identified_file_pairs)} file pairs for BERT score calculation.")

# --- 2. BERT Score Calculation ---

def read_summary_from_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

all_bert_scores = []

for ref_file_path, res_file_path in identified_file_pairs:
    try:
        reference_summary = read_summary_from_file(ref_file_path)
        result_summary = read_summary_from_file(res_file_path)

        # BERTscore requires summaries to be in a list
        references = [reference_summary]
        candidates = [result_summary]

        # Calculate BERTscore
        P, R, F1 = score(candidates, references, lang="en", verbose=False)

        all_bert_scores.append({
            'reference_file': os.path.basename(ref_file_path),
            'result_file': os.path.basename(res_file_path),
            'bert_precision': P.mean().item(),
            'bert_recall': R.mean().item(),
            'bert_f1': F1.mean().item(),
        })
    except Exception as e:
        print(f"Error processing pair {os.path.basename(ref_file_path)} and {os.path.basename(res_file_path)}: {e}")

print(f"Processed {len(all_bert_scores)} file pairs and stored their BERT scores.")

# --- 3. Calculate and Display Average BERT Scores ---

if all_bert_scores:
    df_bert_scores = pd.DataFrame(all_bert_scores)
    avg_bert_precision = df_bert_scores['bert_precision'].mean()
    avg_bert_recall = df_bert_scores['bert_recall'].mean()
    avg_bert_f1 = df_bert_scores['bert_f1'].mean()

    print("\n--- Average BERT Scores Across All Pairs ---")
    print(f"Average BERT Precision: {avg_bert_precision:.4f}")
    print(f"Average BERT Recall: {avg_bert_recall:.4f}")
    print(f"Average BERT F1: {avg_bert_f1:.4f}")
else:
    print("\nNo BERT scores were processed to calculate averages.")

# --- 4. Save BERT Scores to File ---

evaluation_dir = '/content/optimized-summarization/optimized-summarization/Evaluation'
os.makedirs(evaluation_dir, exist_ok=True)
output_filepath = os.path.join(evaluation_dir, 'BERT_Score.csv') # Changed filename and extension

if all_bert_scores:
    df_output = pd.DataFrame({
        'Pair_ID': range(1, len(all_bert_scores) + 1),
        'bert_precision': [d['bert_precision'] for d in all_bert_scores],
        'bert_recall': [d['bert_recall'] for d in all_bert_scores],
        'bert_f1': [d['bert_f1'] for d in all_bert_scores],
    })
    df_output.to_csv(output_filepath, index=False)
    print(f"BERT scores successfully saved to {output_filepath}")
else:
    print("\nNo BERT scores were processed to save.")
